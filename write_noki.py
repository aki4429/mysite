#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, glob
import pandas as pd
import datetime

def write_noki():

    #生産計画ファイル名取得
    k_file = glob.glob('./UP/keikaku/*')[0]
    #KEEP納期ファイル名取得
    n_file = glob.glob('./UP/noki/*')[0]


    #生産計画をDataFrame形式で読み込み
    k_df = pd.read_excel(k_file)
    #KEEP納期ファイルをDataFrame形式で読み込み
    n_df = pd.read_excel(n_file)

    #生産計画の製番から枝番前の番号6桁を受注NOカラムとして追加
    k_df['受注NO']=k_df['製番'].str[0:6]

    #KEEP納期ファイルの受注NOと伝票のみ取り出し。
    t_df = n_df[['受注NO','伝票摘要']] 

    #重複データを削除
    t_df = t_df[-t_df.duplicated()]

    #マージキーのタイプを統一するために納期データの受注NOタイプを文字型に
    t_df = t_df.astype({'受注NO': 'str'})

    #生産計画と納期データをマージキーは受注NOで
    r_df = pd.merge(k_df, t_df, on='受注NO', how='left')

    #NaNでなければ、納期データの伝票摘要を備考に上書きコピーします。
    r_df.loc[r_df['伝票摘要'].notna(), '備考']=r_df['伝票摘要']

    #不要なカラムは削除します。
    r_df.drop(['伝票摘要','受注NO'], axis=1, inplace=True)

    #書込み後ファイルのファイル名を変数に入れます。
    filename ='keikaku_{0}.xlsx'.format(str(datetime.date.today()))
    fullname = os.path.join('.', 'UP', 'result', filename)

    #ファイル保存
    r_df.to_excel(fullname, index=False)

    #最後にファイル名を返します。
    return filename
