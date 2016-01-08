#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
脚本描述: proxies模块定义了与代理相关的数据结构与函数。
author: Bipedal Bit
email: me@bipedalbit.net
'''

import requests
import re
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool
from multiprocessing import Process, Manager, Value
from time import time, sleep

# 客户端伪装
headers = {
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
	'DNT': '1',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0',
}

# 代理池定义
manager = Manager()
proxy_pool = manager.dict() # 键为代理对象，值为代理上一次被使用的时间戳
proxy_pool[None] = 0 # “不使用代理”也作为代理池的一个固定成员

# 新代理列表就绪标识
ready_flag = manager.Value(bool, False)

def get_soup(data):
	'''
	将BeautifulSoup查询得到的tag对象转换为新的可查询的BeautifualSoup对象。
	也可以用来从XML字符串获得BeautifualSoup对象。
	'''
	if not isinstance(data, basestring): data = str(data)
	return BeautifulSoup(data, 'lxml')

def get_proxies(test_url, timeout):
	'''
	通过西刺代理（http://www.xicidaili.com/）获得100个高匿国内代理，
	按照响应速度过滤后返回代理列表。
	'''

	src_url = 'http://www.xicidaili.com/nn'
	# 获取西刺代理首页数据
	global headers
	response = requests.get(src_url, headers=headers)
	# 解析网页
	soup = get_soup(response.text)
	tag_list = soup.find_all('tr')[1:]
	proxy_list = []
	for tag in tag_list:
		# 过滤响应时间太长的代理，我不信任西刺代理网对代理响应时间的测试结果，暂且不使用这层过滤
		# response_time = float(re.search(u'.+(?=秒)', tag.div['title']).group(0)) # 获取响应时间
		# if response_time > 1: continue # 执行过滤
		# 提取标签中的有用字符串
		tag_strings = []
		for string in tag.strings:
			if string.strip() != '':
				tag_strings.append(string)
		# 过滤非HTTP协议代理
		if not re.search('HTTP', tag_strings[4]): continue
		# 构造格式化代理字符串并插入代理列表
		proxy_list.append('http://' + tag_strings[0] + ':' + tag_strings[1])
	proxy_list = pick_proxies(proxy_list=proxy_list, test_url=test_url, timeout=timeout)
	return proxy_list

def test_proxy(test_url, proxy, timeout):
	'''
	使用给定的代理访问给定的地址并计时，
	返回请求响应时间。
	'''
	response_time = 0
	global headers
	try:
		time0 = time()
		requests.get(test_url, headers=headers, proxies={'http': proxy}, timeout=timeout)
		response_time = time() - time0
	except:
		response_time = timeout + 10
	return response_time

def multi_test_wrapper(kwargs):
	'''
	给test_proxy函数加一层封装，解决多参数问题。
	'''
	return test_proxy(**kwargs)

def pick_proxies(proxy_list, test_url, timeout):
	'''
	根据对特定地址的访问响应时间对代理列表进行过滤。
	'''
	proxy_num = len(proxy_list)
	# 并行测试
	pool = Pool(16) # 创建线程池
	kwargs = [{'test_url': test_url, 'proxy': proxy, 'timeout': timeout} for proxy in proxy_list] # 封装参数
	response_time_list = pool.map(multi_test_wrapper, kwargs) # 并行调用
	# 过滤响应慢的代理
	map_list = [] # (代理序号, 响应时间)元组列表，表示代理序号与响应时间的映射关系
	for i in xrange(proxy_num):
		if response_time_list[i] < timeout:
			map_list.append((i, response_time_list[i]))
	# 按响应时间排序
	# map_list = sorted(map_list, key=lambda d: d[1])
	# 填充一个新代理列表
	new_proxy_list = []
	for map_ in map_list:
		new_proxy_list.append(proxy_list[map_[0]])
		# print proxies_list[map_[0]], map_[1], '秒'
	return new_proxy_list

def update_proxy_pool(test_url, timeout, proxy_pool, ready_flag, interval):
	'''
	守护进程执行的任务，定时更新代理池。
	注意每次更新本身需要十几秒的时间，
	所谓定时，是规定更新间隔时间。
	'''
	while 1:
		proxy_list = get_proxies(test_url, timeout) # 获取新代理列表
		# 筛选不在新代理列表中的旧代理
		pre_test_list = proxy_pool.keys()
		pre_test_list.remove(None)
		for proxy in proxy_list:
			if proxy in proxy_pool: # 如果该旧代理在新代理列表中，不测试该代理
				pre_test_list.remove(proxy)
		# 测试旧代理，弃用响应太慢的旧代理
		if len(pre_test_list) > 0:
			pool = Pool(16) # 创建线程池
			kwargs = [{'test_url': test_url, 'proxy': proxy, 'timeout': timeout} for proxy in pre_test_list] # 封装参数
			response_time_list = pool.map(multi_test_wrapper, kwargs) # 并行测试
			for i in xrange(len(pre_test_list)): # 弃用响应太慢的旧代理
				if response_time_list[i] > timeout:
					del proxy_pool[pre_test_list[i]]
		# 合并新旧代理列表
		for proxy in proxy_list:
			if proxy not in proxy_pool: # 如果新代理不在代理池中，初始化新代理
				proxy_pool[proxy] = 0
		ready_flag.value = True
		print '代理池更新完成，当前代理池中有', len(proxy_pool), '个代理'
		sleep(interval) # 定时更新一次代理列表

def get_proxy(delay):
	'''
	从代理池中获取一个合适的代理字符串。
	delay: 每个代理延迟使用时间
	'''
	global proxy_pool, ready_flag
	while 1:
		if ready_flag.value: # 如果预更新代理列表已就绪
			ready_flag.value = False # 置伪就绪标记，等待新的代理列表
		now = time() # 获取当前时间戳
		for proxy in proxy_pool.keys():
			if now - proxy_pool[proxy] < delay: # 如果该代理延迟未满，不使用
				continue
			else: # 如果该代理延迟已满，更新代理时间戳，返回代理字符串
				proxy_pool[proxy] = now
				return proxy
		sleep(1) # 所有代理都延迟未满，等待１秒

def daemon_pool(test_url, timeout, interval):
	'''
	fork一个守护子进程定时更新代理池。
	test_url: 代理测试地址
	timeout: 判定代理响应超时秒数
	interval: 代理池更新间隔秒数
	'''
	global proxy_pool, ready_flag
	kwargs = {
		'test_url': test_url,
		'timeout': timeout,
		'proxy_pool': proxy_pool,
		'ready_flag': ready_flag,
		'interval': interval
	}
	p_update_proxies = Process(target=update_proxy_pool, kwargs=kwargs)
	p_update_proxies.daemon = True # 标记子进程为守护进程，随主进程退出而退出
	p_update_proxies.start()

# 以下为代理池守护进程测试代码
if __name__ == '__main__':
	daemon_pool(test_url='http://weibo.cn/moegirlwiki', timeout=3, interval=30)
	for i in xrange(5):
		print '='*10, '当前代理池（包括不使用代理，即None）', '='*10
		for proxy in proxy_pool.keys():
			print proxy
		print '='*30
		sleep(30)
