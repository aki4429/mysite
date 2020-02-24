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
#RFILE = "./source/remove_list.csv"
#REFILE = "./source/replace_list.csv"

def go():
    RFILE = "./source/remove_list.csv"
    REFILE = "./source/replace_list.csv"

    #生産計画ファイル名取得
    kfile = glob.glob('./UP/ukeikaku/*')[0]
    jfile = glob.glob('./UP/juchu/*')[0]

    #納期は'yyyy/mm/dd'形式なので、/でスプリットして、int()で数のリストを作成
    #datetime形式に変換
    def s2d(hiduke):
        hlist = hiduke.split('/')
        hlist = [int(x) for x in hlist]
        return dt.datetime(*hlist)

    kei=[] #計画データ用変数

    #計画ファイル読み込み"製品コード","計画数","納期","製番" = 1, 6, 5. 4
    #shiji 規格23 製番55 製造開始日27 製品数 35 = 23, 35, 27, 55
    with open(kfile, encoding='CP932') as f:
        reader = csv.reader(f)
        next(reader) #ヘッダ行は飛ばす
        for row in reader:
            kei.append([row[23], row[35].strip(), s2d(row[27]), row[55].split("-")[0]])
            #kei.append([row[1], row[6].strip(), s2d(row[5]), row[4].split("-")[0]])


    #受注日を変数に代入
    juc_date = ""

    juc=[] #受注データ用変数

    #受注ファイル読み込み"品目名(規格)51","HUKLA品番57", "受注数73","納期30",'受注伝票№1',"受注日0"
    #= 51, 57, 73, 30, 1. 0
    with open(jfile, encoding='CP932') as f:
        reader = csv.reader(f)
        next(reader) #ヘッダ行は飛ばす
        for row in reader:
            juc.append([row[51], row[57], row[73].strip(), s2d(row[30]), row[1], s2d(row[0])])
            if juc_date == "":
                juc_date = s2d(row[0])

    #受注データは、納期順でソートします。
    sort_noki = lambda val: val[3]
    juc = sorted(juc, key = sort_noki)

    dates = set()

    #計画の納期を取り出す。
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
    #dir1 = os.path.join("./UP/data/", dates[0].strftime("%Y%m%d"))
    #dir2 = os.path.join("./UP/data/", dates[1].strftime("%Y%m%d"))
    day_1 = dates[0].strftime("%Y%m%d") #若い方の計画日付
    day_2 = dates[1].strftime("%Y%m%d") #遅い方の計画日付
    day_3 = juc_date.strftime("%Y%m%d") #遅い方の計画日付

    #ファイル保存用のファイル名を作っておく
    keiname_1 = "keikaku_" + day_1 + "-2" + ".csv"
    keiname_2 = "keikaku_" + day_2 + "-1" + ".csv"
    by_name = "by_code_" + day_2 + ".csv"
    jucname = "juchu_" + day_3 + ".csv"

    #if not os.path.exists(dir1):
    #    os.mkdir(dir1)

    #if not os.path.exists(dir2):
    #    os.mkdir(dir2)

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

    kei_1 = [] #若い日付の計画用変数
    kei_2 = []
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

    for row in kei:
        if row[2] == dates[1] and not pt.match(row[0]):
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
                kei_2.append([row[0], spec, listrep(code, rp), row[1], row[3], row[2].strftime('%Y/%m/%d')])

    juc_k = [] #加工後の受注データを格納

    #受注データ=品目名(規格),HUKLA品番,受注数,納期,受注伝票№,受注日
    hjogai=['9999', '0003', '0007', '0002', '0022', '0004']
    for row in juc:
        if not pt.match(row[0]) and not row[1] in hjogai:
            model = row[0][:8].split(' ')[0] 
            spec = row[0][8:11].strip()
            piece = row[0][11:16].strip()
            spec2 = row[0][17:19].strip()
            #コクヨだったらハイフォン外す
            if model.startswith("CE"):
                code =  model + spec_check(spec) + piece + spec2_check(spec2)
            else:
                code =  model + spec_check(spec) + "-" + piece + spec2_check(spec2)
        #品目名(規格),受注数,納期,受注伝票№,受注日
        #製品コード",spec,code, "計画数", orderN, "納期", 受注日
        #spec2 のC カバー　は除外
            if not "C" in spec2:
                juc_k.append([row[0], spec, listrep(code, rp), row[2], row[4], row[3].strftime('%Y/%m/%d'), row[5].strftime('%Y/%m/%d') ])


#print(kei_1)

    with open(os.path.join('./UP/data', keiname_1), "w", encoding='CP932' ) as f:
        writer = csv.writer(f)
        writer.writerows(kei_1)

    with open(os.path.join('./UP/data', keiname_2), "w", encoding='CP932' ) as f:
        writer = csv.writer(f)
        writer.writerows(kei_2)

    with open(os.path.join('./UP/data', jucname), "w", encoding='CP932' ) as f:
        writer = csv.writer(f)
        writer.writerows(juc_k)


    bycode = {}
    cd = ""

    for row in kei_2:
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

    with open(os.path.join('./UP/data', by_name), "w", encoding='CP932' ) as f:
        writer = csv.writer(f)
        writer.writerows(bylist)

    return [keiname_1, keiname_2, by_name, jucname]



