#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Bartuccio Antoine (Sli) (klmp200)
# @Date:   2016-07-03 17:57:28
# @Last Modified by:   klmp200
# @Last Modified time: 2016-11-17 00:54:23

from bottle import Bottle, static_file, request, template, redirect
from bottle.ext import sqlite
import hmac
import hashlib
import json
import datetime
import settings

KEYS = []
with open('../data/keys.json', 'r') as json_data:
    KEYS = json.load(json_data)


def SafeInt(string):
    if string.isdecimal():
        return int(string)
    else:
        return 0


def find_product(keys, id_product):
    product = SafeInt(id_product)
    for obj in keys:
        if obj['id'] == product:
            return obj
    return None


def get_banlist():
    with open('../data/banlist.json', 'r') as json_data:
        return json.load(json_data)


def is_banned(code):
    if code in get_banlist():
        return True
    else:
        return False

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


@app.route('/banlist')
def GetBanlist():
    """
        Return json file for banned tickets
    """
    return static_file("banlist.json", root="../data/")


@app.route('/delete/<db_id>')
def DeleteTicket(db, db_id=None):
    """
        Delete a given ticket by id
    """
    if db_id:
        db.execute('DELETE from ticket where id=:id',
                   {"id": db_id})
    redirect(settings.ADMIN_PAGE_URL)


@app.route('/media/<file:path>')
def Media(file=""):
    """
        Provide media files
    """
    return static_file(file, root="./media/")


@app.route(settings.ADMIN_PAGE_URL, method='GET')
def DisplayAdmin(db):
    """
        Get data from database based on get data:
        id where id the id in database
        verifKey the verification key of the ticket
    """
    form = ObtainGetArgs(request.query, ['id', 'verifKey'])
    tickets = SearchDb(db, form)
    return template('admin.simple', table=tickets, form=form,
                    banlist=get_banlist(),
                    admin_url=settings.ADMIN_PAGE_URL)


@app.route(settings.ADMIN_PAGE_URL + '/ajax', method='GET')
def DisplayAdminAjax(db):
    """
        Get data from database same as DisplayAdmin
        Return json for ajax request
    """
    form = ObtainGetArgs(request.query, ['id', 'verifKey'])
    tickets = SearchDb(db, form)
    return dict(data=tickets)


@app.route('/webscan', method='GET')
def ScanTicketView(status=None):
    """
        A web app to check tickets
    """
    response = ObtainGetArgs(request.query, ['av', 'valid', 'child', 'banned'])
    return template('scan.simple', response=response)


@app.route('/webscan/form', method='POST')
def CheckTicketPost(db):
    """
        Recieve form and validate data
    """
    code = request.forms.get('code').upper()
    code_list = code.split()
    is_child = False
    banned = is_banned(code)
    if len(code_list) >= 4:
        verif_key = code_list.pop(-1)
        place_tot = SafeInt(code_list.pop(-1))
        product_type = code_list.pop(1)
        product = find_product(KEYS, product_type)
    else:
        verif_key = ""
        product = {}

    if not banned and CheckHmac(code, product, verif_key) and place_tot > 0:
        used_qt = SafeInt(request.forms.get('qt'))
        is_child = product['is_child']

        if used_qt < 1 or used_qt > place_tot:
            status = {'available': 0, 'valid': False}
        else:
            status = Validate(db, place_tot, verif_key, used_qt, product_type)
    else:
        status = {'available': 0, 'valid': False}

    if request.forms.get('ajax') == "True":
        return dict({'av': status['available'], 'valid': status['valid'],
                     'child': is_child, 'banned': banned})
    else:
        redirect('/webscan?av={}&valid={}&child={}&banned={}'.format(status['available'],
                                                                     status['valid'],
                                                                     is_child, banned))


def CheckHmac(code, product, verif_key):
    new_code = code.split(' ')
    new_code.pop(-1)
    code = ' '.join(new_code)
    if product:
        true_key = hmac.new(bytes(product['key'], 'utf-8'),
                            bytes(code, 'utf-8'), hashlib.sha1).hexdigest()
        return hmac.compare_digest(true_key[:8].upper(), verif_key)
    else:
        return False


def SearchDb(db, args):
    """
        Qwery used in db
    """
    if args['id'] or args['verifKey']:
        table = db.execute("SELECT * from ticket where upper(verifKey) like :key or productType=:id",
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
    redirect(settings.ADMIN_PAGE_URL)


def Validate(db, place_tot, verif_key, place_used, product_type):
    """
        Verify in bdd if the ticket exists and create it
        Return if it's valid and quantity avaliable
    """
    ticket = db.execute('SELECT * from ticket where verifKey=:key and totalPlaces=:nb and productType=:type',
                        {"key": verif_key, "nb": place_tot, 'type': product_type}).fetchone()
    data = {'nb': place_tot, 'qt': place_used, 'verif': verif_key, 'type': product_type}
    if (ticket is None):
        message = NewEntry(db, data)
    else:
        message = UpdateEntry(db, data, ticket)

    return message


@app.route('/validate', method='POST')
def ValidateApi(db):
    """
        Verify in bdd if the ticket exists and create it
        Return a json to the app
    """

    try:
        send = request.json
        message = Validate(db, send['nb'], send['verif'], send['qt'], send['type'])

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
    db.execute('INSERT into ticket(verifKey, availablePlaces, totalPlaces, validationDate, productType) values (?, ?, ?, ?, ?)',
               (data['verif'], available, data['nb'], datetime.datetime.now().strftime('%Hh %Mmin %Ss'), data['type']))

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


app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG, server='paste')

app.uninstall(plugin)
