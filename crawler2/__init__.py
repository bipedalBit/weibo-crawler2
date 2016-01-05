#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
包描述: crawler2包在crawler包的基础上扩展了代理池的功能，
并使用requests包对HTTP请求部分进行了重构。
脚本描述: __init__.py脚本可以看作是crawler2包的索引脚本，负责将包内所有模块组织起来。
author: Bipedal Bit
email: me@bipedalbit.net
'''

import sys
from getpass import getpass
from weiboParser import wap_weibo_parser as parser
from weiboLogin import wap_login as login
import DB
import crawler
import proxies
from time import time


def get_time_cost_str(time_cost):
	'''
	格式化时间开销（time()函数返回值的差），返回时间开销字符串。
	'''
	int_time_cost = int(time_cost)
	time_cost_str = ''
	day_seconds = 3600*24
	if time_cost < 60:
		time_cost_str += str(time_cost) + '秒'
	elif 60 <= time_cost < 3600:
		time_cost_str += str(int_time_cost/60) + '分' + str(time_cost%60) + '秒'
	elif 3600 <= time_cost < day_seconds:
		time_cost_str += str(int_time_cost/3600)  + '小时' + str(int_time_cost/60%60) + '分' + str(time_cost%60) + '秒'
	else:
		time_cost_str += str(int_time_cost/day_seconds) + '天' + str(int_time_cost/3600%24)  + '小时'\
		+ str(int_time_cost/60%60) + '分' + str(time_cost%60) + '秒'
	return time_cost_str

def main():
	'''
	定义一个入口函数来组织爬虫过程，虽然对于python来说入口函数的形式并不必要.
	'''
	# 指定系统默认编码为utf-8
	default_encoding = 'utf-8'
	if sys.getdefaultencoding() != default_encoding:
		reload(sys)
		sys.setdefaultencoding(default_encoding)

	# 必要数据收集
	url = 'http://weibo.cn/moegirlwiki' # 任意新浪微博移动版页面地址
	DB.dbuser = 'root' # MySQL数据库用户名
	DB.dbpassword = 'root' # MySQL数据库密码
	crawler.username = raw_input('请输入新浪通行证用户名：') # 爬取网站用户名
	crawler.password = getpass('请输入新浪通行证密码：') # 爬取网站密码
	crawler.cookie = login(crawler.username, crawler.password) # 获取第一个有效cookie

	# 初始化数据库，如果需要可以解开注释
	# DB.init_DB()

	# 启动代理池守护进程
	proxies.daemon_pool(test_url='http://weibo.cn', timeout=3, interval=30)

	# 执行爬虫过程
	time0 = time()
	weibo_cnt = crawler.crawl(
		url=url,
		parser=parser,
		login=login,
		write_DB=DB.write_DB,
		get_proxy=proxies.get_proxy,
		average_delay=3,
		page_limit=1000,
		# record_raw_data = True
	)
	time_cost = time() - time0
	print '共爬取数据', weibo_cnt, '条，用时' + get_time_cost_str(time_cost)
