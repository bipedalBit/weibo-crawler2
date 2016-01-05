#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
脚本描述: crawler模块中定义了网络爬虫的相关函数。
author: Bipedal Bit
email: me@bipedalbit.net
'''

import re
import requests
from random import random

# 客户端伪装
headers = {
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
	'DNT': '1',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0',
}

# 网络爬虫使用的默认cookie
cookie = ''
# 网络爬虫所需的登录用户名
username = ''
# 网络爬虫所需的登录密码
password = ''

def log_raw_result(raw_result):
	'''
	记录当前请求返回的生数据
	'''
	f = open('raw_result.htm', 'w')
	f.write(raw_result)
	f.close()

def clear_log():
	'''
	清空爬虫日志文件
	'''
	f = open('log', 'w')
	f.close()

def crawl(url, parser, login, write_DB, get_proxy=None, average_delay=3, page_limit=None, record_raw_data=False):
	'''
	在指定url用指定登录器和解析方法爬取页面数据并保存，返回爬取数据数，爬取页面上限为可选项。
	url: 爬虫起点地址
	parser: 页面解析器函数
	login: 登录器函数
	write_DB: 写数据库函数
	average_delay: 每组请求的平均延时，实际延时将是平均延迟周围的一个随机值
	page_limit: 爬取页面上限，可选项
	record_raw_data: 是否记录页面生数据，默认不记录
	'''
	# 引入模块的全局变量
	global cookie
	global username
	global password
	# 记录爬取的页数
	p = 1
	# 记录爬取的数据数
	data_cnt = 0
	clear_log() # 清空爬虫日志
	f = open('log', 'a') # 打开爬虫日志
	print '开始执行网络爬虫...' # 显示提示信息
	while True:
		proxy = None
		if not get_proxy: # 如果使用代理
			delay = random()*(2*average_delay - 2) + 1 # 计算一个以1为下限以average_delay为平均值的随机延迟
			proxy = get_proxy(delay)
			proxy = {'http': proxy} if not proxy else None # 获取一个合适的代理
		response = requests.get(url, headers=headers, cookies=cookie, proxies=proxy) # 请求页面数据
		raw_result = response.text
		actual_url = response.url # 获取实际访问页面地址
		if actual_url != url: # 被服务器执行了请求重定向
			if not re.match('login', actual_url):
				print 'cookie无效或已经过期失效，重新登录' # 显示提示信息
				f.write('cookie无效或已经过期失效，重新登录\n') # 记录爬虫日志
				cookie = login(username, password)
			else:
				print '账号的访问请求被服务器重定向，IP可能被封禁，更换代理' # 显示提示信息
				f.write('账号的访问请求被服务器重定向，IP可能被封禁，更换代理\n') # 记录爬虫日志
			continue # 重新尝试爬取该页
		if record_raw_data: log_raw_result(raw_result) # 记录当前请求返回的生数据
		page_result = None
		host = re.search('(?<=http://).+?(?=/)', url).group(0) # 提取url对应host
		try:
			page_result = parser(url, host, raw_result) # 尝试解析页面
		except: # 如果页面解析不成功，可能页面结构已经发生变化，停止爬虫
			print '页面解析失败，停止爬虫' # 显示提示信息
			f.write('页面解析失败，停止爬虫') # 记录爬虫日志
			break
		f.write('从"' + url + '"爬取' + str(len(page_result['data_list'])) + '条数据\n') # 记录爬虫日志
		# 保存熟数据（SQL录入）
		if len(page_result['data_list']) > 0: write_DB(data_list = page_result['data_list'])
		p += 1 # 页面数加1
		data_cnt += len(page_result['data_list']) # 更新解析出的数据数
		# 检查是否到达指定的爬取页面上限
		if page_limit is not None and p > page_limit: break
		# 检查是否已经没有下一页
		if page_result['next_page_link'] is None: break
		# 更新目标url
		else: url = page_result['next_page_link']
	f.close() # 关闭爬虫日志
	return data_cnt
