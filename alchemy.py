#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, session, redirect
import sqlite3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from checker import check_logged_in

from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = '++--**%$$#&,,,.tttjkwoudHH'

Base = declarative_base()



if __name__ == '__main__':
    engine = create_engine('sqlite:///tfc.sqlite')
else:
    engine = create_engine('sqlite:///mysite/tfc.sqlite')

#Model Class
class TfcCode(Base):
    """
    TfcCodeテーブルクラス
    """

    # テーブル名
    __tablename__ = 'tfc_code'

    # 個々のカラムを定義
    id = Column(Integer, primary_key=True)
    hinban = Column(String)
    item = Column(String)
    description = Column(String)
    remarks = Column(String)
    unit = Column(String)
    uprice = Column(String)
    ouritem = Column(String)
    vol = Column(String)
    zaiko = Column(String)
    kento = Column(String)
    hcode = Column(String)
    cat = Column(String)

def getAll():
    Session = sessionmaker(bind=engine)
    ses = Session()
    res = ses.query(TfcCode).all()
    ses.close()
    return res

def getOne(id):
    Session = sessionmaker(bind=engine)
    ses = Session()
    res = ses.query(TfcCode).filter(TfcCode.id == id).one()
    ses.close()
    return res

def searchHin(hin, item, description, hcode):
    Session = sessionmaker(bind=engine)
    ses = Session()
    res = ses.query(TfcCode).filter(TfcCode.hinban.like('%{0}%'.format(hin)),
            TfcCode.item.like('%{0}%'.format(item)),
            TfcCode.description.like('%{0}%'.format(description)),
            TfcCode.hcode.like('%{0}%'.format(hcode)),
            ).all()
    ses.close()
    return res

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        session['password'] = request.form['password']
        return redirect('/')
    else:
        return render_template('login.html')


@app.route('/')
@check_logged_in
def menu():
    return render_template('menu.html',
                           data = [["TFCコード編集","code"],[ "発注", "order"]],
                           title ="最初のメニュー",
                           msg ="メニュー項目から選んでください。",
                           menu='class="active"')

@app.route('/code', methods=['POSt', 'GET'])
@check_logged_in
def code():
    #db=sqlite3.connect("tfc.sqlite")
    #cur = db.execute("select id, hinban, description, uprice, vol from tfc_code")
    #items=cur.fetchall()
    hinban = request.form.get("hinban")
    item = request.form.get("item")
    description = request.form.get("description")
    hcode = request.form.get("hcode")
    #items = getAll()
    items = searchHin(hinban, item, description, hcode)
    return render_template('clist.html',
                           data = items,
                           msg = "TFCコード検索")

    #db.close()

@app.route('/edit/<id>', methods=['POSt', 'GET'])
@check_logged_in
def edit(id):
    res = getOne(id)
    return render_template('edit.html',
                           data = res,
                           msg = "TFCコード編集")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port='8000')
