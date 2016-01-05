#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
脚本描述: weiboLogin.py模块与上个版本的weiboLogin相同，提供了获取登录必要cookie字段的函数。
author: Bipedal Bit
email: me@bipedalbit.net
'''

import requests
import re
from bs4 import BeautifulSoup
from getpass import getpass

# 尽管不设置报文头也不会被新浪服务器阻拦，还是做一些必要的伪装与配置比较保险
headers = {
	'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
	'DNT': '1',
	'Connection': 'keep-alive',
	'Cache-Control': 'max-age=0',
}

def get_post_needs():
	'''
	从新浪微博移动版登录页面获得登录post请求的必要数据：
	action_url: 登录post请求的目标地址
	password_name: 登录post请求中密码数据的数据名
	vk: 登录post请求中vk数据的值
	'''
	url = 'http://login.weibo.cn/login/?ns=1&revalid=2&backURL=http://weibo.cn/&backTitle=微博&vt='
	text = requests.get(url, headers=headers).text
	soup = BeautifulSoup(text, 'lxml')
	action_url = 'http://login.weibo.cn/login/' + soup.form['action']
	password_tag = soup.find('input', type = 'password')
	password_name = re.search('(?<=name=")\w+(?=")', str(password_tag)).group(0)
	vk_tag = soup.find('input', attrs = {'name': 'vk'})
	vk = re.search('(?<=value=")\w+(?=")', str(vk_tag)).group(0)
	return action_url, password_name, vk

def get_post_data(username, password, password_name, vk):
	'''
	使用从新浪微博移动版登录页面获取的参数和已知的固定参数填充表单，
	获取一个dist对象准备作为数据段填入post请求中。
	'''
	form_data = {
		'mobile': username,
		password_name: password,
		'remeber': 'on',
		'backURL': 'http://weibo.cn/',
		'backTitle': '微博',
		'tryCount': '',
		'vk': vk,
		'submit': '登录'
	}
	return form_data

def wap_login(username, password):
	'''
	按照新浪通信证的用户名和密码进行新浪微博移动版的模拟登录，
	获取以登录状态访问新浪微博移动版页面必需的cookie字段。
	'''
	url, password_name, vk = get_post_needs()
	data = get_post_data(username, password, password_name, vk)
	session = requests.Session()
	response = session.post(url, headers=headers, data=data)
	# 以下三种来自不同domain的名为SUB的cookie字段都可以用来验证登录状态
	# return session.cookies.get('SUB', domain='.sina.cn')
	# return session.cookies.get('SUB', domain='.weibo.com')
	cookie = {'SUB': session.cookies.get('SUB', domain='.weibo.cn')}
	return cookie

# 以下是模拟登录测试代码
if __name__ == '__main__':
	url = 'http://weibo.cn/moegirlwiki'
	username = raw_input('请输入新浪通行证用户名：')
	password = getpass('请输入新浪通行证密码：')
	cookie = wap_login(username, password)
	response = requests.get(url, cookies=cookie)
	print '登录成功！' if response.url == url else '登录失败！'
