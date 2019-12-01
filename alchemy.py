#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, session, redirect, flash, url_for, send_from_directory
from werkzeug.utils import secure_filename
import sqlite3
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from checker import check_logged_in

from flask_bootstrap import Bootstrap

import write_noki
import keikako2

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = '++--**%$$#&,,,.tttjkwoudHH'

Base = declarative_base()

UPLOAD_FOLDER = './UP'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if __name__ == '__main__':
    engine = create_engine('sqlite:///tfc.sqlite')
else:
    engine = create_engine('sqlite:///anywhere/tfc.sqlite')

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

def searchHin(hin, description):
    Session = sessionmaker(bind=engine)
    ses = Session()
    res = ses.query(TfcCode).filter(TfcCode.hinban.like('%{0}%'.format(hin)),
            TfcCode.description.like('%{0}%'.format(description)),
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
                           data = [["TFCコード編集","code"],[ "KEEP納期書込み", "keep"], ["ウレタン発注","ure"]],
                           title ="調達メニュー",
                           msg ="メニュー項目から選んでください。",
                           menu='class="active"')

@app.route('/keep', methods=['POST', 'GET'])
@check_logged_in
def keep():
    #変換結果ファイルを削除しておきます。
    rfiles=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'result'))
    os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], 'result'))
    for f in rfiles:
        os.remove(f)
    os.chdir('../..')
    msg=""
    kfiles=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'keikaku'))
    nfiles=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'noki'))
    if request.method == 'POST':
        # check if the post request has the file part
        if 'keikaku' in request.files:
            file = request.files['keikaku']
            filename = os.path.join('keikaku', file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            msg += 'ファイル:' + file.filename + 'を保存しました。'

        if 'noki' in request.files:
            file = request.files['noki']
            filename = os.path.join('noki', file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            msg += 'ファイル:' + file.filename + 'を保存しました。'

        if request.form.get('keep_del') =='削除':
            os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], 'keikaku'))
            for f in kfiles:
                os.remove(f)
            os.chdir('../..')
            os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], 'noki'))
            for f in nfiles:
                os.remove(f)
            os.chdir('../..')


    return render_template('keep.html',
                           title ="KEEP納期書込み",
                           msg = msg,
                           kfiles = kfiles,
                           nfiles = nfiles,
                           len_k = len(kfiles),
                           len_n = len(nfiles)
                           )

@app.route('/result', methods=['POST'])
@check_logged_in
def result():
    kfiles=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'keikaku'))
    nfiles=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'noki'))
    if len(kfiles) > 0 and len(nfiles) > 0 :
        filename = write_noki.write_noki()
        os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], 'keikaku'))
        for f in kfiles:
            os.remove(f)
        os.chdir('../..')
        os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], 'noki'))
        for f in nfiles:
            os.remove(f)
        os.chdir('../..')

        return render_template('result.html', 
                filename = filename)
    else:
        return redirect /keep

@app.route('/ure', methods=['POST', 'GET'])
@check_logged_in
def ure():
    #kfile=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'ukeikaku'))[0]
    msg1=""
    msg2=""
    if request.method == 'POST':
        # check if the post request has the file part
        if 'ukeikaku' in request.files:
            file = request.files['ukeikaku']
            filename = os.path.join('ukeikaku', file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            msg1 += 'ファイル:' + file.filename + 'を保存しました。'

        if 'juchu' in request.files:
            file = request.files['juchu']
            filename = os.path.join('juchu', file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            msg2 += 'ファイル:' + file.filename + 'を保存しました。'

    return render_template('ure.html',
                           msg1 = msg1,
                           msg2 = msg2)

@app.route('/ures', methods=['POST'])
@check_logged_in
def ures():
    kfiles=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'ukeikaku'))
    jfiles=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'juchu'))
    if len(kfiles) > 0 and len(jfiles) > 0 :
        files = keikako2.go()
        os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], 'ukeikaku'))
        for f in kfiles:
            os.remove(f)
        os.chdir('../..')
        os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], 'juchu'))
        for f in jfiles:
            os.remove(f)
        os.chdir('../..')

        return render_template('ureres.html', 
                keiname_1 = files[0], 
                keiname_2 = files[1],
                by_name = files[2] ,
                jucname = files[3] )
    else:
        return redirect /ure

@app.route('/UP/data/<path:filename>')
def down_file(filename):
    print("filename=", filename)
    if __name__ == '__main__':
        return send_from_directory('./UP/data/', filename, as_attachment=True)
    else:
        return send_from_directory('/home/huklajapan/UP/data/', filename, as_attachment=True)

@app.route('/UP/result/<path:filename>')
def download_file(filename):
    print("filename=", filename)
    if __name__ == '__main__':
        return send_from_directory('./UP/result/', filename, as_attachment=True)
    else:
        return send_from_directory('/home/huklajapan/UP/result/', filename, as_attachment=True)

@app.route('/code', methods=['POSt', 'GET'])
@check_logged_in
def code():
    #db=sqlite3.connect("tfc.sqlite")
    #cur = db.execute("select id, hinban, description, uprice, vol from tfc_code")
    #items=cur.fetchall()
    hinban = request.form.get("hinban")
    description = request.form.get("description")
    #items = getAll()
    items = searchHin(hinban, description)
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
