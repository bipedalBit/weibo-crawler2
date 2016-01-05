#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
脚本描述: weiboParser模块中定义了新浪微博页面的解析过程相关的函数。
author: Bipedal Bit
email: me@bipedalbit.net
'''

from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def get_soup(data):
	'''
	将BeautifulSoup查询得到的tag对象转换为新的可查询的BeautifualSoup对象。
	也可以用来从XML字符串获得BeautifualSoup对象。
	'''
	if not isinstance(data, basestring): data = str(data)
	return BeautifulSoup(data, 'lxml')

def wap_weibo_data_parser(data_list, weibo_soup, client_info_soup):
	'''
	用于新浪微博移动版用户主页每个的微博标签的数据解析。
	可能解析出的数据项包括：
	weibo_id: 微博唯一标识字符串
	datetime: 微博时间
	client: 微博客户端
	content: 微博原文
	image_url: 微博图片地址
	attitude_cnt: 微博点赞数
	repost_cnt: 微博转发数
	comment_cnt: 微博评论数
	comment_url: 微博评论地址
	repost_flag: 微博转发标识
	org_weibo_user: 微博原文作者
	org_weibo_user_url: 微博原文作者主页地址
	'''
	data = {}
	# 获取微博ID
	data['weibo_id'] = weibo_soup.div['id']
	# 获取客户端信息，即时间和客户端类型
	client_info = ''.join(client_info_soup.strings).split(u'\xa0来自')
	# 获取日期、时间
	datetime_ = client_info[0].encode('utf8').split(' ')
	# 获取当前日期、时间
	now = datetime.now()
	# 时间格式为DD分钟前
	if len(datetime_) == 1:
		minutes_delta = int(datetime_[0].split('分钟前')[0])
		dt = (now - timedelta(minutes = minutes_delta))
		data['datetime'] = str(dt.date()) + ' ' + dt.strftime('%I:%M')
	# 时间格式为今天 HH:MM
	elif len(datetime_) == 2 and datetime_[0] == '今天':
		data['datetime'] = str(now.date()) + ' ' + datetime_[1]
	# 时间格式为MM月DD日 HH:MM
	elif datetime_[0].find('月') != -1:
		month = int(datetime_[0].split('月')[0])
		day = int(datetime_[0].split('月')[1].split('日')[0])
		dt = datetime(now.year, month, day)
		data['datetime'] = str(dt.date()) + ' ' + datetime_[1]
	# 时间格式为YY-MM-DD HH:MM
	else:
		data['datetime'] = client_info[0]
	# 获取客户端类型
	data['client'] = client_info[1]
	# 获取微博正文
	data['content'] = ''.join(get_soup(weibo_soup.find('span', class_ = 'ctt')).strings)
	# 获取图片链接
	if weibo_soup.find('img', class_ = 'ib') is not None:
		image_soup = get_soup(weibo_soup.find('img', class_ = 'ib').parent)
		data['image_url'] = image_soup.a['href']
	# 获取微博中的所有div子标签
	div_list = weibo_soup.find_all('div', class_ = False)
	# 获取赞数
	attitude_soup = get_soup(get_soup(div_list[-1]).find('a', href = re.compile('^http://weibo.cn/attitude/')))
	data['attitude_cnt'] = int(re.search(r'\d+', attitude_soup.string).group(0))
	# 获取转发数
	repost_soup = get_soup(get_soup(div_list[-1]).find('a', href = re.compile('^http://weibo.cn/repost/')))
	data['repost_cnt'] = int(re.search(r'\d+', repost_soup.string).group(0))
	# 获取评论数
	comment_soup = get_soup(get_soup(div_list[-1]).find('a', class_ = 'cc'))
	data['comment_cnt'] = int(re.search(r'\d+', comment_soup.string).group(0))
	# 获取评论地址
	data['comment_url'] = comment_soup.a['href']
	# 如果微博为转发型
	if weibo_soup.find('span', class_ = 'cmt') is not None:
		# 标记为转发型微博
		data['repost_flag'] = 1
		post_user_soup = get_soup(get_soup(div_list[0]).span.a)
		if post_user_soup.a is None:
			data['org_weibo_user'] = ''
			data['org_weibo_user_url'] = ''
		else:
			data['org_weibo_user'] = post_user_soup.a.string
			data['org_weibo_user_url'] = post_user_soup.a['href']
		# 获取微博最后一个div标签的第二段文本内容为转发理由
		str_generator = get_soup(div_list[-1]).strings
		str_generator.next() # 跳过第一段文本即“转发理由:”
		data['repost_reason'] = str_generator.next()
	# 如果微博为原创型
	else: data['repost_flag'] = 0 # 标记为非转发型微博
	# 统一字符串编码
	for key in data.keys():
		if isinstance(data[key], basestring):
			data[key] = data[key].encode('utf8')
	# 装填数据
	data_list.append(data)

def wap_weibo_parser(url, host, data):
	'''
	用于新浪微博移动版用户主页的微博数据解析。
	按特定url、host地址和特定页面生数据（刚获取的HTML字符串）解析页面数据，
	获取页面微博内容数据weibo_list数组和页面跳转链接next_page_link。
	'''
	# 获取页面BueatifulSoup对象
	soup = get_soup(data)
	# 获取各条微博的Tag对象
	weibo_list = soup.find_all('div', class_ = 'c', id = True)
	# 获取下一页链接
	next_page_link = re.search('(?<=href=").+(?=">下页)', str(soup.find('div', id = 'pagelist'))).group(0)
	# 获取页面数据
	data_list = []
	# 提取目标主页的用户微博ID
	user_tag_soup = get_soup(soup.find('div', class_ = 'ut'))
	weibo_user = user_tag_soup.strings.next().split()[0].encode('utf8')
	# 当前页不是是微博主页首页
	if user_tag_soup.find('span', class_ = 'ctt') is None:
		weibo_user = re.search('.+(?=的微博)', weibo_user).group(0)
	# 遍历当前页面的微博，解析数据
	for weibo in weibo_list:
		# 获取微博的BueatifulSoup对象
		weibo_soup = get_soup(weibo)
		# 获取微博客户端标签的BueatifulSoup对象
		client_info_soup = get_soup(weibo_soup.find('span', class_ = 'ct'))
		# 微博过滤，是否解析当前微博的数据
		# 私货1：根据客户端类型过滤来自萌百自动机的微博
		if client_info_soup.find(text = re.compile(u'来自萌娘百科')): continue
		# 私货2：过滤导致客户端字段解析错误的微博
		if len(''.join(client_info_soup.strings).split(u'\xa0来自')) == 1: continue
		# 解析微博细节数据
		wap_weibo_data_parser(data_list, weibo_soup, client_info_soup)
		# 添加目标用户的微博ID和主页链接
		data_list[-1]['weibo_user'] = weibo_user
		data_list[-1]['weibo_user_url'] = url
	if next_page_link is not None: next_page_link = 'http://' + host + next_page_link + '/'
	page_result = {
		'data_list': data_list,
		'next_page_link': next_page_link
	}
	return page_result

# 以下为微博页面解析器测试代码
if __name__ == '__main__':
	# f = open('test_raw_data', 'r')
	f = open('test_raw_data', 'r')
	data = f.read()
	f.close()
	page_result = wap_weibo_parser('http://weibo.cn/moegirlwiki', 'weibo.cn', data)
	print page_result['data_list'][0]
	print page_result['next_page_link']