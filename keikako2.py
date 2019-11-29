#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import pandas as pd
import datetime as dt
import os
import re
import glob

#kei = pd.read_csv("../urethane/source/keikaku.csv",encoding="CP932")
#KFILE = "./source/keikaku.csv"
RFILE = "./source/remove_list.csv"
REFILE = "./source/replace_list.csv"

def go():

    #生産計画ファイル名取得
    kfile = glob.glob('./UP/ukeikaku/*')[0]

    kei=[]

    #納期は'yyyy/mm/dd'形式なので、/でスプリットして、int()で数のリストを作成
    #datetime形式に変換
    def s2d(hiduke):
        hlist = hiduke.split('/')
        hlist = [int(x) for x in hlist]
        return dt.datetime(*hlist)


    #"製品コード","計画数","納期","製番" = 1, 6, 5. 4
    with open(kfile, encoding='CP932') as f:
        reader = csv.reader(f)
        next(reader) #ヘッダ行は飛ばす
        for row in reader:
            kei.append([row[1], row[6].strip(), s2d(row[5]), row[4].split("-")[0]])

    dates = set()

    #納期を取り出す。
    for row in kei:
        dates.add(row[2])

    dates = list(dates)
    dates.sort()

    if len(dates) == 2 :
        print("納期は{0}と{1} です。".format(dates[0].strftime("%m/%d"), 
            dates[1].strftime("%m/%d")))
    else:
        print("計画の日付が２日分でありません")

    #無ければ、納期日のデータフォルダを作成
    dir1 = os.path.join("./data/", dates[0].strftime("%Y%m%d"))
    dir2 = os.path.join("./data/", dates[1].strftime("%Y%m%d"))

    if not os.path.exists(dir1):
        os.mkdir(dir1)

    if not os.path.exists(dir2):
        os.mkdir(dir2)

    remlist =[]

    with open(RFILE) as f:
        reader = csv.reader(f)
        for row in reader:
            remlist.append(*row)

    pattern = r"^(" + "|".join(remlist) + ")"

    pt = re.compile(pattern)

    #仕様記号をウレタンに適した記号に変換
    def spec_check(words):
        if "H" in words:
            return "H"
        elif "U" in words:
            return "H"
        elif "S" in words:
            return "S"
        elif "CN" in words:
            return "CN"
        elif "W" in words:
            return "W"
        else:
            return ""

    def spec2_check(words):
        if "T" in words:
            return "T"
        else:
            return ""


    rp = []

    #変換リストの作成
    with open(REFILE) as f:
        reader = csv.reader(f)
        for row in reader:
            rp.append(row)

    def listrep(word, rp):
        for row in rp:
            word = word.replace(row[0], row[1])

        return word

    kei_1 = []
    for row in kei:
        if row[2] == dates[0] and not pt.match(row[0]):
            model = row[0][:8].split(' ')[0] 
            spec = row[0][8:11].strip()
            piece = row[0][11:16].strip()
            spec2 = row[0][17:19].strip()
            #コクヨだったらハイフォン外す
            if model.startswith("CE"):
                code =  model + spec_check(spec) + piece + spec2_check(spec2)
            else:
                code =  model + spec_check(spec) + "-" + piece + spec2_check(spec2)
        #kei=製品コード","計画数","納期","製番" 
        #製品コード",spec,code, "計画数", orderN, "納期"
        #spec2 のC カバー　は除外
        if not "C" in spec2:
            kei_1.append([row[0], spec, listrep(code, rp), row[1], row[3], row[2].strftime('%Y/%m/%d')])

#print(kei_1)

    with open(os.path.join(dir1, 'keikaku_new.csv'), "w" ) as f:
        writer = csv.writer(f)
        writer.writerows(kei_1)

    bycode = {}
    cd = ""

    for row in kei_1:
        if row[2] in bycode:
            bycode[row[2]] = [bycode[row[2]][0] + int(float(row[3])), 
                    min(bycode[row[2]][1], row[4])]
        else:
            bycode[row[2]] = [int(float(row[3])), row[4]]

    bylist =[]
    i = 0
    for key, val in bycode.items():
        line = []
        line.append(key)
        for v in val:
            line.append(str(v))

        bylist.append(line)

    bylist.sort()
    for row in bylist:
        row[:0] =[i + 1]
        i += 1

    with open(os.path.join(dir1, 'by_code_new.csv'), "w", encoding='CP932' ) as f:
        writer = csv.writer(f)
        writer.writerows(bylist)

    return os.path.join(dir1, 'by_code_new.csv')



