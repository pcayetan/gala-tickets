#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: klmp200
# @Date:   2016-07-03 17:57:28
# @Last Modified by:   klmp200
# @Last Modified time: 2016-07-03 22:32:39

from bottle import route, static_file, run, request, template


@route('/keys')
def GetKeys():
    return static_file("keys.json", root="../data/")


@route('/validate', method='POST')
def Validate():
    data = request.json

    return template('<p>id: {{id}}, type: {{type}}</p>', id=data['id'], type=data['type'])

run(host='localhost', port=8080, debug=True)
