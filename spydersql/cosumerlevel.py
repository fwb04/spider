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
    r = s.post(url, params=keyvalue, headers=headers)
    # print(r.text)

    # 修改dfwds字段内容
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    # 再次进行请求
    r1 = s.post(url, params=keyvalue, headers=headers)

    # 爬取农村居民消费水平
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A020B02"}]'
    s = requests.session()
    r = s.get(url, params=keyvalue, headers=headers)
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    r2 = s.get(url, params=keyvalue, headers=headers)

    # 爬取城镇居民消费水平
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A020B03"}]'
    s = requests.session()
    r = s.get(url, params=keyvalue, headers=headers)
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    r3 = s.get(url, params=keyvalue, headers=headers)

    # 定义人口数据存储数组
    year = []
    consumerlevel = []
    citycl = []
    countrycl = []

    # 从json文件提取居民消费水平
    data1 = json.loads(r1.text)
    data_one1 = data1['returndata']['datanodes']
    for value in data_one1:
        if ('zb.A020B01_sj' in value['code']):
            year.append(value['code'][-4:])
            consumerlevel.append(value['data']['data'])

    # 提取农村居民消费水平
    data2 = json.loads(r2.text)
    data_one2 = data2['returndata']['datanodes']
    for value in data_one2:
        if ('zb.A020B02_sj' in value['code']):
            countrycl.append(value['data']['data'])

    # 提取城镇居民消费水平
    data3 = json.loads(r3.text)
    data_one3 = data3['returndata']['datanodes']
    for value in data_one3:
        if ('zb.A020B03_sj' in value['code']):
            citycl.append(value['data']['data'])

    # 删除2018年的数据（空数据）
    del year[0]
    del consumerlevel[0]
    del citycl[0]
    del countrycl[0]

    # list逆序存放
    year.reverse()
    consumerlevel.reverse()
    citycl.reverse()
    countrycl.reverse()

    print(consumerlevel)
    print(countrycl)
    print(citycl)


    # 连接数据库，不存在时自动创建
    conn = sqlite3.connect("cosumerlevel.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS cosumerlevel
                  (year text, consumerlevel real, countrycl real, citycl real)''')
    cur.execute('select * from cosumerlevel ')
    data = cur.fetchall()
    if data == []:
        for i in range(len(year)):
            cur.execute(
                "INSERT INTO cosumerlevel VALUES ('%s','%f','%f','%f')" % (year[i], consumerlevel[i], countrycl[i], citycl[i]))
    conn.commit()
    cur.close()
    conn.close()

def plot1(year, consumerlevel):

    plt.figure(figsize=(12, 6))
    ax = plt.subplot()  # 创建图片区域
    plt.ylim(2000, 25000)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    ax.bar(year, consumerlevel, align='center', color='darkseagreen', edgecolor='white')
    for a, b in zip(year, consumerlevel):
        plt.text(a, b + 0.05, '%.1f' % b, ha='center', va='bottom', fontsize=10)
    plt.xlabel(u'年份')
    plt.xticks(rotation=45)
    plt.ylabel(u'元')
    plt.title(u'1999-2017年居民消费水平条形图')
    plt.show()

def plot2(year, countrycl, citycl):
    r = []
    for i in range(len(countrycl)):
        r.append(citycl[i] / countrycl[i])
    plt.figure(figsize=(10, 5))
    plt.ylim(2, 4)
    # ax = plt.subplot()  # 创建图片区域
    plt.title("1999-2018年城市居民消费水平相对农村变化折线图（农村=1）")
    plt.xlabel(u'年份')
    plt.xticks(rotation=45)
    plt.ylabel(u'1')
    plt.plot(year, r)
    for a, b in zip(year, r):
        plt.text(a, b + 0.03, '%.2f' % b, ha='center', va='bottom', fontsize=9)
    # plt.fill_between(year, r, interpolate=True, color='lishtgreen', alpha=0.5)
    plt.grid(color='whitesmoke', ls='--')
    plt.show()

def plotdata():
    conn = sqlite3.connect("cosumerlevel.db")
    cur = conn.cursor()
    cur.execute('select * from cosumerlevel ')
    data = cur.fetchall()
    cur.close()
    conn.close()
    print(data)

    year = [i[0] for i in data]
    cousumerlevel = [i[1] for i in data]
    countrycl = [i[2] for i in data]
    citycl = [i[3] for i in data]
    # print(year)
    # print(cousumerlevel)
    # print(countrycl)
    # print(citycl)

    plot1(year, cousumerlevel)
    plot2(year, countrycl, citycl)

if __name__ == '__main__':

    # 从国家统计局获取人口数据并存入本地数据库cosumerlevel.db
    # getCPI()

    # 作图
    plotdata()