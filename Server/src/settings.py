# -*- coding: utf-8 -*-
# @Author: klmp200
# @Date:   2016-11-05 19:58:43
# @Last Modified by:   klmp200
# @Last Modified time: 2016-11-05 20:02:41

HOST = '0.0.0.0'
PORT = '8080'
DEBUG = True

# Loads custom settings

try:
    from settings_custom import *
except:
    print("Custom settings import failed")
