#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: klmp200
# @Date:   2016-07-03 17:57:28
# @Last Modified by:   klmp200
# @Last Modified time: 2016-11-05 20:23:47

from bottle import Bottle, static_file, request, template, redirect
from bottle.ext import sqlite
import datetime
import settings

app = Bottle()
plugin = sqlite.Plugin(dbfile='../data/sqliteDB.db')
app.install(plugin)


def serialize_table(table):
    """
        Convert a row in a list of dict
    """
    obj = list()
    dict_tmp = {}
    for row in table:
        dict_tmp = {}
        for key in row.keys():
            dict_tmp[key] = row[key]
        obj.append(dict_tmp)
    return obj


@app.route('/gala.apk')
def GetApp():
    """
        Allow to download the gala
    """
    return static_file("gala.apk", root="../data/")


@app.route('/scanner.apk')
def GetScan():
    """
        Allow to download the qr code reader
    """
    return static_file("scanner.apk", root="../data/")


@app.route('/')
def HomePage():
    """
        Home page
    """
    return template('home.simple')


@app.route('/keys')
def GetKeys():
    """
        Return json file for keys
    """
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
    form = ObtainGetArgs(request.query, ['id', 'verifKey'])
    tickets = SearchDb(db, form)
    return template('admin.simple', table=tickets, form=form)


@app.route('/admin/ajax', method='GET')
def DisplayAdminAjax(db):
    """
        Get data from database same as DisplayAdmin
        Return json for ajax request
    """
    form = ObtainGetArgs(request.query, ['id', 'verifKey'])
    tickets = SearchDb(db, form)
    return dict(data=tickets)


def SearchDb(db, args):
    """
        Qwery used in db
    """
    if args['id'] or args['verifKey']:
        table = db.execute("SELECT * from ticket where upper(verifKey) like :key or id =:id",
                           {"key": '%' + args['verifKey'].upper() + '%',
                            "id": args['id']}).fetchall()
    else:
        table = db.execute('SELECT * from ticket').fetchall()
    tickets = serialize_table(table)[::-1]
    return tickets


def ObtainGetArgs(query, args):
    """
        Fill a dict with get args in query
        query : the query object
        args : a list of get arguments to get
    """
    getargs = {}
    for arg in args:
        if getattr(query, arg):
            getargs[arg] = getattr(query, arg)
        else:
            getargs[arg] = ""
    return getargs


@app.route('/edit/qt/<id_ticket>/<nb>')
def EditTicketQuantity(db, id_ticket, nb):
    """
        Edit the quantity avaliable for a ticket
    """
    nb = int(nb)
    ticket = db.execute('SELECT * from ticket where id=:id',
                        {"id": id_ticket}).fetchone()
    if ticket is not None:
        nb_new = ticket['availablePlaces'] + nb
        if nb_new >= 0 and nb_new <= ticket['totalPlaces']:
            db.execute('UPDATE ticket SET availablePlaces=:av WHERE id=:id',
                       {"av": nb_new, "id": id_ticket})
    redirect('/admin')


@app.route('/validate', method='POST')
def Validate(db):
    """
        Verify in bdd if the ticket exists and create it
        Return a json to the app
    """

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
    """
        Add a new ticket in bdd
    """
    available = data['nb'] - data['qt']
    response = {
        "available": available,
        "valid": True
    }
    db.execute('INSERT into ticket(verifKey, availablePlaces, totalPlaces, validationDate) values (?, ?, ?, ?)',
               (data['verif'], available, data['nb'], datetime.datetime.now().strftime('%Hh %Mmin %Ss')))

    return dict(response)


def UpdateEntry(db, data, obj):
    """
        Update info in ticket
    """
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


app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)

app.uninstall(plugin)
