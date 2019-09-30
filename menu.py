#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def menu():
    return render_template('menu.html',
                           data = [["TFCコード編集","code"],[ "発注", "order"]],
                           title ="最初のメニュー",
                           msg ="メニュー項目から選んでください。")

@app.route('/code')
def code():
    db=sqlite3.connect("tfc.sqlite")
    cur = db.execute("select id, hinban, description, uprice, vol from tfc_code")
    items=cur.fetchall()
    return render_template('clist.html',
                           data = items,
                           title = "TFCコード表示",
                           msg = "TFCコード表を表示します。")

    db.close()
app.debug = True
app.run(host='0.0.0.0', port='8000')
