#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: klmp200
# @Date:   2016-07-03 17:57:28
# @Last Modified by:   klmp200
# @Last Modified time: 2016-11-04 21:16:27

from bottle import Bottle, static_file, request, template, redirect
from bottle.ext import sqlite

app = Bottle()
plugin = sqlite.Plugin(dbfile='../data/sqliteDB.db')
app.install(plugin)

def serialize_table(table):
    obj = list()
    dict_tmp = {}
    for row in table:
        dict_tmp = {}
        for key in row.keys():
            dict_tmp[key] = row[key]
        obj.append(dict_tmp)
    return obj

@app.route('/app.apk')
def GetApp():
    return static_file("app.apk", root="../data/")

@app.route('/')
def HomePage():
    text = ''.join(("<h1>Serveur de validation de ebillets du gala</h1><p>Cliquez <a href=",
            "/app.apk",">ici</a> pour télécarger l'application</p>"))
    return text

@app.route('/keys')
def GetKeys():
    return static_file("keys.json", root="../data/")

@app.route('/delete/<db_id>')
def DeleteTicket(db, db_id=None):
    """
        Delete a given ticket by id
    """
    if db_id:
        db.execute('DELETE from ticket where id=:id',
                   {"id": db_id})
    redirect('/admin')


@app.route('/media/<file:path>')
def Media(file=""):
    """
        Provide media files
    """
    return static_file(file, root="./media/")


@app.route('/admin', method='GET')
def DisplayAdmin(db):
    """
        Get data from database based on get data:
        id where id the id in database
        verifKey the verification key of the ticket
    """
    table = []
    form = {}
    form['key'] = ""
    form['id'] = ""
    if request.query.verifKey:
        request.query.verifKey = request.query.verifKey.upper()
        form['key'] = request.query.verifKey
    if request.query.id:
        form['id'] = request.query.id
    if not request.query.id and not request.query.verifKey:
        table = db.execute('SELECT * from ticket').fetchall()
    elif request.query.id and not request.query.verifKey:
        table = db.execute('SELECT * from ticket where id=:id',
                           {"id": request.query.id}).fetchall()
    elif not request.query.id and request.query.verifKey:
        table = db.execute('SELECT * from ticket where verifKey=:key',
                           {"key": request.query.verifKey})
    else:
        table = db.execute('SELECT * from ticket where verifKey=:key and id=:id',
                           {"key": request.query.verifKey,
                            "id": request.query.id})
    tickets = serialize_table(table)
    tickets = tickets[::-1]
    if request.query.ajax:
        return dict(data=tickets)
    else:
        return template('admin.simple', table=tickets, form=form)


@app.route('/validate', method='POST')
def Validate(db):

    try:
        send = request.json
        ticket = db.execute('SELECT * from ticket where verifKey=:key and totalPlaces=:nb',
                            {"key": send['verif'], "nb": send['nb']}).fetchone()

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

    db.execute('INSERT into ticket(verifKey, availablePlaces, totalPlaces) values (?, ?, ?)',
               (data['verif'], available, data['nb']))

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
