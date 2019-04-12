# -*- coding: utf-8 -*-

import requests
import json
import time
import sqlite3
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

def gettime():
    return int(round(time.time() * 1000))

def getCPI():
    # 用来自定义头部的
    headers = {}
    # 用来传递参数的
    keyvalue = {}
    # 目标网址
    url = 'http://data.stats.gov.cn/easyquery.htm'

    # 头部的填充
    headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) ' \
                            'AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                            'Version/12.0 Safari/605.1.15'

    # 参数的填充
    keyvalue['m'] = 'QueryData'
    keyvalue['dbcode'] = 'hgnd'
    keyvalue['rowcode'] = 'zb'
    keyvalue['colcode'] = 'sj'
    keyvalue['wds'] = '[]'
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A020B01"}]'
    keyvalue['k1'] = str(gettime())

    # 建立一个Session
    s = requests.session()
    # 在Session基础上进行一次请求
    r = s.get(url, params=keyvalue, headers=headers)

    # 修改dfwds字段内容
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    # 再次进行请求
    r1 = s.get(url, params=keyvalue, headers=headers)
    # print(r.text)

    # 爬取居民消费指数
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A020B04"}]'
    s = requests.session()
    r = s.get(url, params=keyvalue, headers=headers)
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    r2 = s.get(url, params=keyvalue, headers=headers)

    # 爬取农村居民消费指数
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A020B05"}]'
    s = requests.session()
    r = s.get(url, params=keyvalue, headers=headers)
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    r3 = s.get(url, params=keyvalue, headers=headers)

    # 爬取城镇居民消费指数
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A020B06"}]'
    s = requests.session()
    r = s.get(url, params=keyvalue, headers=headers)
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    r4 = s.get(url, params=keyvalue, headers=headers)

    # 定义人口数据存储数组
    year = []
    consumerlevel = []
    CPI = []
    cityCPI = []
    countryCPI = []

    # 从json文件提取居民消费水平
    data1 = json.loads(r1.text)
    data_one1 = data1['returndata']['datanodes']
    for value in data_one1:
        if ('zb.A020B01_sj' in value['code']):
            year.append(value['code'][-4:])
            consumerlevel.append(value['data']['data'])

    # 提取居民消费指数
    data2 = json.loads(r2.text)
    data_one2 = data2['returndata']['datanodes']
    for value in data_one2:
        if ('zb.A020B04_sj' in value['code']):
            CPI.append(value['data']['data'])

    # 提取农村居民消费指数
    data3 = json.loads(r3.text)
    data_one3 = data3['returndata']['datanodes']
    for value in data_one3:
        if ('zb.A020B05_sj' in value['code']):
            countryCPI.append(value['data']['data'])

    # 提取城镇居民消费指数
    data4 = json.loads(r4.text)
    data_one4 = data4['returndata']['datanodes']
    for value in data_one4:
        if ('zb.A020B06_sj' in value['code']):
            cityCPI.append(value['data']['data'])

    # 删除2018年的数据（空数据）
    del year[0]
    del consumerlevel[0]
    del CPI[0]
    del cityCPI[0]
    del countryCPI[0]

    # list逆序存放
    year.reverse()
    consumerlevel.reverse()
    CPI.reverse()
    cityCPI.reverse()
    countryCPI.reverse()

    print(year)
    print(consumerlevel)
    print(CPI)
    print(cityCPI)
    print(countryCPI)

    # 连接数据库，不存在时自动创建
    conn = sqlite3.connect("CPI.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS CPI
                  (year text, consumerlevel real, CPI real, countryCPI real, cityCPI real)''')
    for i in range(len(year)):
        cur.execute(
            "INSERT INTO CPI VALUES ('%s','%f','%f','%f','%f')" % (year[i], consumerlevel[i], CPI[i], countryCPI[i], cityCPI[i]))
    conn.commit()
    cur.close()
    conn.close()

def plotdata():
    conn = sqlite3.connect("CPI.db")
    cur = conn.cursor()
    cur.execute('select * from CPI ')
    data = cur.fetchall()
    cur.close()
    conn.close()
    print(data)

    year = [i[0] for i in data]
    cousumerlevel = [i[1] for i in data]
    CPI = [i[2] for i in data]
    countryCPI = [i[3] for i in data]
    cityCPI = [i[4] for i in data]

if __name__ == '__main__':

    # 从国家统计局获取人口数据并存入本地数据库population.db
    getCPI()

    # 作图
    plotdata()