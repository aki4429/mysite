#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
import sqlite3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

app = Flask(__name__)

Base = declarative_base()

engine = create_engine('sqlite:///tfc.sqlite')

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

def searchHin(hin, item):
    Session = sessionmaker(bind=engine)
    ses = Session()
    res = ses.query(TfcCode).filter(TfcCode.hinban.like('%{0}%'.format(hin)),
            TfcCode.hinban.like('%{0}%'.format(item))).all()
    ses.close()
    return res


@app.route('/')
def menu():
    return render_template('menu.html',
                           data = [["TFCコード編集","code"],[ "発注", "order"]],
                           title ="最初のメニュー",
                           msg ="メニュー項目から選んでください。")

@app.route('/code', methods=['POSt', 'GET'])
def code():
    #db=sqlite3.connect("tfc.sqlite")
    #cur = db.execute("select id, hinban, description, uprice, vol from tfc_code")
    #items=cur.fetchall()
    hinban = request.form.get("kensaku")
    item = request.form.get("code")
    #items = getAll()
    items = searchHin(hinban, item)
    return render_template('clist.html',
                           data = items,
                           title = "TFCコード表示",
                           msg = "TFCコード表を表示します。")

    db.close()
app.debug = True
app.run(host='0.0.0.0', port='8000')
