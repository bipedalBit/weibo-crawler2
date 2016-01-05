#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
脚本描述: DB模块中定义了操作MySQL数据库的相关函数和变量。
author: Bipedal Bit
email: me@bipedalbit.net
'''

import MySQLdb
import os

# 数据库用户名，默认为空
dbuser = ''
# 数据库密码，默认为空
dbpassword = ''

def init_DB():
	'''
	将使用尝试db_create.sql初始化数据库。
	'''
	cmd = 'mysql -u%s -p%s < db_create.sql ' % (dbuser, dbpassword)
	print os.popen(cmd).read()

def write_DB(data_list, dbname='crawl_result', tablename='weibo', dbhost='localhost', dbport=3306):
	'''
	保存熟数据，将爬虫获得的格式化数据录入MySQL数据库。
	默认数据库名为”crawler_result“，不应改变，除非修改了已经完成初始化的数据库的名称；
	默认数据库表名为”weibo“，不应改变，除非修改了已经完成初始化的数据库的表名称；
	数据库地址默认为本地；
	数据库端口号默认为MySQL数据库默认端口号3306。
	'''
	conn = MySQLdb.connect(
		host=dbhost,
		port=dbport,
		user=dbuser,
		passwd=dbpassword,
		db=dbname,
		charset='utf8'
	)
	cur = conn.cursor()
	for data in data_list:
		placeholders = []
		for value in data.values(): placeholders.append('%d' if type(value) is int else '\'%s\'')
		sql = 'insert into `' + tablename + '`(`' + '`,`'.join(data.keys()) + '`) values(' + ','.join(placeholders) + ')'
		# 微博ID重复则跳过，避免数据重复
		try: cur.execute(sql % tuple(data.values()))
		except: continue
	cur.close()
	conn.commit()
	conn.close()