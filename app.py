#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request

app = Flask(__name__)

#@app.route('/<i>/<pas>')
@app.route('/', methods=['GET', 'POST'])
#def hello_world(i: str, pas: str) -> str:
def hello_world():
    #return 'Welcome to flask world!!'
    #return render_template('index.html',
    data=['ab', 'cd', 'ef', 'gh']
    result = request.form.get('aescape')
    if result == 'on':
        check = True
    else:
        check = False
        
    return render_template('forin.html',
                           check = check,
                           data = data,
                           title = "with jinja",
                           msg ="これはテンプレートの利用例")
                           #msg = "id:{0}, passwd:{1}".format(i, pas))
                           #msg = "お名前は?")

@app.route('/next', methods=['POST'])
def form():
    field = request.form.get('field')
    ck = request.form.get('check')
    rd = request.form.get('radio')
    sel = request.form.getlist('sel')
    return render_template('index.html',
                           title = "index with jinja",
                           #msg ="これはテンプレートの利用例")
                           #msg = "id:{0}, passwd:{1}".format(i, pas))
                           #msg = "こんにちは。{0}さん".format(field))
                           msg = [field, ck, rd, sel])

app.debug = True
app.run(host='0.0.0.0', port='8000')
