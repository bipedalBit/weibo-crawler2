#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
脚本描述: __main__.py脚本可以看作是crawler2包的对外接口。
author: Bipedal Bit
email: me@bipedalbit.net
'''

import sys
import os

if not __package__:
	path = os.path.join(os.path.dirname(__file__), os.pardir)
	sys.path.insert(0, path)

import crawler2
crawler2.main()