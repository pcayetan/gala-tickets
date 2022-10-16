#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Bartuccio Antoine (Sli) (klmp200)
# @Date:   2016-07-03 17:57:28
# @Last Modified by:   pcayetan
# @Last Modified time: 2022-09-14 01:52:43

from flask import Flask, render_template, request, redirect, g
import sqlite3
import hmac
import hashlib
import json
import datetime
import settings

KEYS = []
with open('../data/keys.json', 'r') as json_data:
    KEYS = json.load(json_data)

app = Flask(__name__)


# Database administration
DATABASE = '../data/sqliteDB.db'


def get_db():
    """
        Opens connection to db, makes the db returns dicts, return db
    """
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db


def make_dicts(cursor, row):
    """
        change return value of cursor to a dict    
    """
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


@app.teardown_appcontext
def close_connection(exception):
    """
        Disconnect from db when not needed
    """
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    """
        Execute and commit sql queries
    """
    con = get_db()
    cur = con.execute(query, args)
    rv = cur.fetchall()
    con.commit()
    cur.close()
    return (rv[0] if rv else None) if one else rv


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


@app.route('/delete/<db_id>')
def DeleteTicket(db_id=None):
    """
        Delete a given ticket by id
    """
    if db_id:
        query_db('DELETE from ticket where id=:id',
                   {"id": db_id})
    return redirect(settings.ADMIN_PAGE_URL)


@app.route(settings.ADMIN_PAGE_URL, methods=['GET'])
def DisplayAdmin():
    """
        Get data from database based on get data:
        id where id the id in database
        verifKey the verification key of the ticket
    """
    form = ObtainGetArgs(request.args.to_dict(),['id', 'verifKey'])
    tickets = SearchDb(form)
    return render_template('admin.simple', table=tickets, form=form,
                    banlist=get_banlist(),
                    admin_url=settings.ADMIN_PAGE_URL)


@app.route(settings.ADMIN_PAGE_URL + '/ajax', methods=['GET'])
def DisplayAdminAjax():
    """
        Get data from database same as DisplayAdmin
        Return json for ajax request
    """
    form = ObtainGetArgs(request.args.to_dict(),['id', 'verifKey'])
    tickets = SearchDb(form)
    return dict(data=tickets)


@app.route('/', methods=['GET'])
def ScanTicketView(status=None):
    """
        A web app to check tickets
    """
    response = ObtainGetArgs(request.args.to_dict(), ['av', 'valid', 'child', 'banned'])
    return render_template('home.simple', response=response)


@app.route('/check_ticket', methods=['POST'])
def CheckTicketPost():
    """
        Receive form and validate data
    """
    code = request.form['code']
    code_list = code.split()
    is_child = False
    banned = is_banned(code)
    if len(code_list) >= 4:
        verif_key = code_list.pop(-1)
        place_tot = SafeInt(code_list.pop(-1))
        product_type = code_list.pop(1)
        product = find_product(KEYS, product_type)
        is_recharge = product['is_recharge']
    else:
        verif_key = ""
        product = {}

    if not banned and CheckHmac(code, product, verif_key) and place_tot > 0 and not is_recharge: 
        used_qt = SafeInt(request.form['qt'])
        is_child = product['is_child']
        if used_qt < 1 or used_qt > place_tot:
            status = {'available': 0, 'valid': False}
        else:
            status = Validate(place_tot, verif_key, used_qt, product_type)
    else:
        status = {'available': 0, 'valid': False}

    if request.form['ajax'] == "True":
        return dict({'av': status['available'], 'valid': status['valid'],
                    'child': is_child, 'banned': banned})
    else:
        return redirect('/?av={}&valid={}&child={}&banned={}'.format(status['available'],
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


def SearchDb(args):
    """
        Qwery used in db
    """
    if args['id'] or args['verifKey']:
        print(args['id'], args['verifKey'])
        tickets = query_db("SELECT * from ticket where upper(verifKey) like :key or productType=:id",
                           {"key": '%' + args['verifKey'].upper() + '%',
                            "id": args['id']})
    else:
        tickets = query_db('SELECT * from ticket')
    return tickets


def ObtainGetArgs(query, args):
    """
        Fill a dict with get args in query
        query : the query object
        args : a list of get arguments to get
    """
    for arg in args:
        query[arg] = query.get(arg,"")
    return query


@app.route('/edit/qt/<id_ticket>/<nb>')
def EditTicketQuantity(id_ticket, nb):
    """
        Edit the quantity avaliable for a ticket
    """
    nb = int(nb)
    ticket = query_db('SELECT * from ticket where id=:id',
                        {"id": id_ticket}, one=True)
    if ticket is not None:
        nb_new = ticket['availablePlaces'] + nb
        if nb_new >= 0 and nb_new <= ticket['totalPlaces']:
            query_db('UPDATE ticket SET availablePlaces=:av WHERE id=:id',
                       {"av": nb_new, "id": id_ticket})
    return redirect(settings.ADMIN_PAGE_URL)


def Validate(place_tot, verif_key, place_used, product_type):
    """
        Verify in bdd if the ticket exists and create it
        Return if it's valid and quantity avaliable
    """
    ticket = query_db('SELECT * from ticket where verifKey=:key and totalPlaces=:nb and productType=:type',
                        {"key": verif_key, "nb": place_tot, 'type': product_type}, one=True)
    
    data = {'nb': place_tot, 'qt': place_used, 'verif': verif_key, 'type': product_type}
    if (ticket is None):
        message = NewEntry(data)
    else:
        message = UpdateEntry(data, ticket)

    return message


@app.route('/validate', methods=['POST'])
def ValidateApi():
    """
        Verify in bdd if the ticket exists and create it
        Return a json to the app
    """

    try:
        send = request.json
        message = Validate(send['nb'], send['verif'], send['qt'], send['type'])

    except:
        message = '<p>Error processing data</p>'

    return message


def NewEntry(data):
    """
        Add a new ticket in bdd
    """
    available = data['nb'] - data['qt']
    response = {
        "available": available,
        "valid": True
    }
    query_db('INSERT into ticket(verifKey, availablePlaces, totalPlaces, validationDate, productType) values (?, ?, ?, ?, ?)',
               (data['verif'], available, data['nb'], datetime.datetime.now().strftime('%Hh %Mmin %Ss'), data['type']))
    
    return dict(response)


def UpdateEntry(data, obj):
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

    query_db('UPDATE ticket SET availablePlaces=:av WHERE id=:id',
               {"av": availableP, "id": obj['id']})

    return dict(response)

@app.route('/recharge', methods=['GET'])
def RechargeView(status=None):
    """
        A web app to check tickets
    """
    response = ObtainGetArgs(request.args.to_dict(), ['av', 'valid', 'child', 'banned'])
    return render_template('recharge.simple', response=response)

@app.route('/check_recharge', methods=['POST'])
def CheckRechargePost():
    """
        Receive form and validate data
    """
    code = request.form['code']
    code_list = code.split()
    banned = is_banned(code)

    if len(code_list) >= 4:
        verif_key = code_list.pop(-1)
        place_tot = SafeInt(code_list.pop(-1))
        product_type = code_list.pop(1)
        product = find_product(KEYS, product_type)
        is_recharge = product['is_recharge']
    else:
        verif_key = ""
        product = {}

    if not banned and CheckHmac(code, product, verif_key) and place_tot > 0 and is_recharge:
        used_qt = SafeInt(request.form['qt'])
        value = product['value_recharge']
        if used_qt < 1 or used_qt > place_tot:
            status = {'available': 0, 'valid': False}
        else:
            status = Validate(place_tot, verif_key, used_qt, product_type)
    else:
        status = {'available': 0, 'valid': False}
        value = 0

    if request.form['ajax'] == "True":
        return dict({'av': status['available'], 'valid': status['valid'],
                    'value': value, 'banned': banned})
    else:
        return redirect('/recharge?av={}&valid={}&value={}&banned={}'.format(status['available'],
                                                                     status['valid'],
                                                                     value, banned))  

app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)