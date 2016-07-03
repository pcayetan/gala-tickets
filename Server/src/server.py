#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: klmp200
# @Date:   2016-07-03 17:57:28
# @Last Modified by:   klmp200
# @Last Modified time: 2016-07-03 18:11:45

from bottle import route, static_file, run


@route('/keys')
def getKeys():
    return static_file("keys.json", root="../data/")

run(host='localhost', port=8080)
