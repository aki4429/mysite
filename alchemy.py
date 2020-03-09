#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, session, redirect, flash, url_for, send_from_directory, make_response
from werkzeug.utils import secure_filename
import sqlite3
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func

from checker import check_logged_in

from flask_bootstrap import Bootstrap

import write_noki
import keikako2
import csv

from io import StringIO

app = Flask(__name__)
bootstrap = Bootstrap(app)
app.secret_key = '++--**%$$#&,,,.tttjkwoudHH'

Base = declarative_base()

UPLOAD_FOLDER = './UP'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if __name__ == '__main__':
    engine = create_engine('sqlite:///tfc.sqlite')
    engine2 = create_engine('sqlite:///se.sqlite')
else:
    engine = create_engine('sqlite:///anywhere/tfc.sqlite')
    engine2 = create_engine('sqlite:///mysite/se.sqlite')

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

#Model Sebango Class
class SeBango(Base):
    """
    背番号テーブルクラス
    """

    # テーブル名
    __tablename__ = 'sebango'

    # 個々のカラムを定義
    id = Column(Integer, primary_key=True)
    hcode = Column(String)
    se = Column(String)
    scode = Column(String)
    sname = Column(String)

    def __repr__(self):
        return [self.id, self.hcode, self.se, self.scode, self.sname]

def searchSe(hcode, se, scode, sname):
    Session = sessionmaker(bind=engine2)
    ses = Session()
    res = ses.query(SeBango).filter(SeBango.hcode.like('%{0}%'.format(hcode)), 
            SeBango.se.like('%{0}%'.format(se)),
            SeBango.scode.like('%{0}%'.format(scode)),
            SeBango.sname.like('%{0}%'.format(sname)),
            ).all()
    ses.close()
    return res

def getSone(id):
    Session = sessionmaker(bind=engine2)
    ses = Session()
    res = ses.query(SeBango).get(id)
    ses.close()
    return res

def getSeMax():
    """ 
    背番号DBの次のIDを取り出します。
    """
    Session = sessionmaker(bind=engine2)
    ses = Session()
    res = ses.query(func.max(SeBango.id)).one()
    ses.close()
    return res[0] + 1

def getSeNext(id):
    """ 
    そのIDの背番号アルファベットの次の番号を取り出します。
    """
    Session = sessionmaker(bind=engine2)
    ses = Session()
    sonoDB = ses.query(SeBango).get(id)
    #背番号アルファベット取り出し
    al = sonoDB.se[0]
    se_max = ses.query(func.max(SeBango.se)).\
        filter(SeBango.se.like('%{0}%'.format(al))).one()
    ses.close()
    #数字部分を取り出し1加えて４桁0埋め
    suuji = str(int(se_max[0].split('-')[1]) + 1).zfill(4)
    next_se = al + "-" + suuji
    return next_se

@app.route('/updateSe/<id>', methods=['POSt'])
def updateSe(id):
    Session = sessionmaker(bind=engine2)
    ses = Session()
    data = ses.query(SeBango).filter(SeBango.id == id).one()
    hcode = request.form.get("hcode")
    se = request.form.get("se")
    scode = request.form.get("scode")
    sname = request.form.get("sname")
    data.hcode = hcode
    data.se = se
    data.scode = scode
    data.sname = sname
    ses.add(data)
    ses.commit()
    items = searchSe(hcode, se, scode, sname)
    #res = getSone(id)
    ses.close()
    return render_template('selist.html', 
            data = items,  msg = "背番号検索")

@app.route('/insertSe/<id>', methods=['POSt'])
def insertSe(id):
    Session = sessionmaker(bind=engine2)
    ses = Session()
    hcode = request.form.get("hcode")
    se = request.form.get("se")
    scode = request.form.get("scode")
    sname = request.form.get("sname")
    sebango = SeBango(id = id, hcode = hcode, se = se, scode = scode, sname = sname)
    ses.add(sebango)
    ses.commit()
    #res = getSone(id)
    items = searchSe(hcode, se, scode, sname)
    ses.close()
    return render_template('selist.html', 
            data = items,  msg = "背番号検索")

@app.route('/delSe/<id>', methods=['POSt'])
def delSe(id):
    Session = sessionmaker(bind=engine2)
    ses = Session()
    data = ses.query(SeBango).get(id)
    ses.delete(data)
    ses.commit()
    ses.close()
    return render_template('selist.html', msg = "背番号検索")

@app.route('/download/<obj>/')
def download(obj):
    Session = sessionmaker(bind=engine2)
    ses = Session()

    f = StringIO()
    writer = csv.writer(f, quotechar='"', quoting=csv.QUOTE_ALL, lineterminator="\n")

    if obj == 'sebango':
        writer.writerow(['id','コード','背番号','仕入先コード','仕入先名'])
        for u in ses.query(SeBango).all():
            writer.writerow([u.id, u.hcode,u.se,u.scode,u.sname])

    res = make_response()
    res.data = f.getvalue().encode('CP932')
    res.headers['Content-Type'] = 'text/csv'
    res.headers['Content-Disposition'] = 'attachment; filename='+ obj +'.csv'
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
                           data = [["背番号検索","se"],[ "KEEP納期書込み", "keep"], ["ウレタン発注","ure"]],
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
        return redirect('/keep')

@app.route('/ure', methods=['POST', 'GET'])
@check_logged_in
def ure():
    dfiles=os.listdir(os.path.join(app.config['UPLOAD_FOLDER'], 'data'))
    os.chdir(os.path.join(app.config['UPLOAD_FOLDER'], 'data'))
    for f in dfiles:
        os.remove(f)

    os.chdir('../..')

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

        return render_template('ureres.html', keiname_1 = files[0], 
                keiname_2 = files[1], 
                by_name = files[2] , 
                jucname = files[3])

    else:
        return redirect('/ure')

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
    max_id = getSeMax()
    return render_template('clist.html',
                           data = items,
                           max_id = max_id,
                           msg = "TFCコード検索")

    #db.close()

@app.route('/edit/<id>', methods=['POSt', 'GET'])
@check_logged_in
def edit(id):
    res = getOne(id)
    return render_template('edit.html',
                           data = res,
                           msg = "TFCコード編集")

@app.route('/se', methods=['POSt', 'GET'])
@check_logged_in
def se():
    hcode = request.form.get("hcode")
    se = request.form.get("se")
    scode = request.form.get("scode")
    sname = request.form.get("sname")
    items = searchSe(hcode, se, scode, sname)
    return render_template('selist.html',
                           data = items,
                           msg = "背番号検索")

@app.route('/sedit/<id>', methods=['POSt', 'GET'])
@check_logged_in
def sedit(id):
    res = getSone(id)
    return render_template('sedit.html',
                           data = res,
                           msg = "背番号編集")

@app.route('/secopy/<id>', methods=['POSt', 'GET'])
@check_logged_in
def secopy(id):
    res = getSone(id)
    se_next = getSeNext(id)
    next_id = getSeMax()
    return render_template('secopy.html',
                           data = res,
                           next_id = next_id,
                           se_next = se_next,
                           msg = "背番号コピー")

@app.route('/delse/<id>', methods=['POSt', 'GET'])
@check_logged_in
def delse(id):
    res = getSone(id)
    return render_template('delse.html',
                           data = res,
                           msg = "背番号削除")

@app.route('/senew/<id>', methods=['POSt', 'GET'])
@check_logged_in
def senew(id):
    return render_template('senew.html',
                           max_id = id,
                           msg = "新規入力")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port='8000')
