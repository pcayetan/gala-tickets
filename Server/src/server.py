#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: klmp200
# @Date:   2016-07-03 17:57:28
# @Last Modified by:   klmp200
# @Last Modified time: 2016-07-04 17:50:18

from bottle import Bottle, static_file, request
from bottle.ext import sqlite

app = Bottle()
plugin = sqlite.Plugin(dbfile='../data/sqliteDB.db')
app.install(plugin)

@app.route('/')
def GetApp():
    return static_file("app.apk", root="../data/")

@app.route('/keys')
def GetKeys():
    return static_file("keys.json", root="../data/")


@app.route('/validate', method='POST')
def Validate(db):

    try:
        send = request.json
        ticket = db.execute('SELECT * from ticket where verifKey=:key',
                            {"key": send['verif']}).fetchone()

        if (ticket is None):
            message = NewEntry(db, send)
        else:
            message = UpdateEntry(db, send, ticket)

    except:
        message = '<p>Error processing data</p>'

    return message


def NewEntry(db, data):
    available = data['nb'] - data['qt']
    response = {
        "available": available,
        "valid": True
    }

    db.execute('INSERT into ticket(verifKey, availablePlaces) values (?, ?)',
               (data['verif'], available))

    return dict(response)


def UpdateEntry(db, data, obj):
    availableP = obj['availablePlaces'] - data['qt']

    if availableP >= 0:
        available = True
    else:
        availableP = obj['availablePlaces']
        available = False

    response = {
        "available": availableP,
        "valid": available
    }

    db.execute('UPDATE ticket SET availablePlaces=:av WHERE id=:id',
               {"av": availableP, "id": obj['id']})

    return dict(response)


app.run(host='0.0.0.0', port=8080, debug=True)

app.uninstall(plugin)
