#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
Date: 2019/12/2 22:24
Desc: 微博指数
"""
import datetime
import re

import pandas as pd
import requests

from akshare.index.cons import index_weibo_headers  # 伪装游览器, 必备


def _get_items(word="股票"):
    url = "https://data.weibo.com/index/ajax/newindex/searchword"
    payload = {"word": word}
    res = requests.post(url, data=payload, headers=index_weibo_headers)
    return {word: re.findall(r"\d+", res.json()["html"])[0]}


def _get_index_data(wid, time_type):
    url = "http://data.weibo.com/index/ajax/newindex/getchartdata"
    data = {
        "wid": wid,
        "dateGroup": time_type,
    }
    res = requests.get(url, params=data, headers=index_weibo_headers)
    json_df = res.json()
    data = {
        "index": json_df["data"][0]["trend"]["x"],
        "value": json_df["data"][0]["trend"]["s"],
    }
    return pd.DataFrame(data)


def _process_index(index):
    now = datetime.datetime.now()
    curr_year = now.year
    curr_date = "%04d%02d%02d" % (now.year, now.month, now.day)
    if "月" in index:
        tmp = index.replace("日", "").split("月")
        date = "%04d%02d%02d" % (curr_year, int(tmp[0]), int(tmp[1]))
        if date > curr_date:
            date = "%04d%02d%02d" % (curr_year - 1, int(tmp[0]), int(tmp[1]))
        return date
    return index


def weibo_index(word="python", time_type="3month"):
    """
    :param word: str
    :param time_type: str 1hour, 1day, 1month, 3month
    :return:
    """
    dict_keyword = _get_items(word)
    df_list = []
    for keyword, wid in dict_keyword.items():
        df = _get_index_data(wid, time_type)
        if df is not None:
            df.columns = ["index", keyword]
            df["index"] = df["index"].apply(lambda x: _process_index(x))
            df.set_index("index", inplace=True)
            df_list.append(df)
    if df_list:
        df = pd.concat(df_list, axis=1)
        df.index = pd.to_datetime(df.index)
        return df


if __name__ == "__main__":
    df_index = weibo_index(word="口罩", time_type="1hour")
    print(df_index)
