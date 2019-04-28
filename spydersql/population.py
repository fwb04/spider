# -*- coding: utf-8 -*-

import requests
import json
import time
import sqlite3
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

def gettime():
    return int(round(time.time() * 1000))

def getpopulation():
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
    keyvalue['dfwds'] = '[{"wdcode":"zb","valuecode":"A0301"}]'
    keyvalue['k1'] = str(gettime())

    # 建立一个Session
    s = requests.session()
    # 在Session基础上进行一次请求
    r = s.post(url, params=keyvalue, headers=headers)

    # 修改dfwds字段内容
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    # 再次进行请求
    r = s.get(url, params=keyvalue, headers=headers)
    r.encoding = 'utf-8'
    print(r.text)
    # 定义人口数据存储数组
    year = []
    population = []
    male = []
    female = []

    # 从json文件提取想要的数据
    data = json.loads(r.text)
    data_one = data['returndata']['datanodes']
    for value in data_one:
        if ('A030101_sj' in value['code']):
            year.append(value['code'][-4:])
            population.append(int(value['data']['strdata']))
        if ('A030102_sj' in value['code']):
            male.append(int(value['data']['strdata']))
        if ('A030103_sj' in value['code']):
            female.append(int(value['data']['strdata']))

    print(year)
    print(population)
    print(male)
    print(female)

    # 数组逆序存放
    year.reverse()
    population.reverse()
    male.reverse()
    female.reverse()

    # 连接数据库，不存在时自动创建
    conn = sqlite3.connect("population.db")
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS population
              (year text, popu int, male int, female int)''')
    cur.execute('select * from population ')
    data = cur.fetchall()
    if data == []:
        for i in range(len(year)):
            cur.execute("INSERT INTO population VALUES ('%s','%d','%d','%d')" % (year[i], population[i], male[i], female[i]))
    # cur.execute("INSERT INTO population VALUES ('2009',1,2,3)")
    # y = ('2009',)
    # cur.execute('SELECT * FROM population WHERE year=?', y)
    # print(cur.fetchone())
    conn.commit()
    cur.close()
    conn.close()

def plot1(year, population):
    # fig = plt.figure()  # 创建画布
    plt.figure(figsize=(10, 6))
    ax = plt.subplot()  # 创建图片区域
    # plt.grid(color='lightgrey', ls='--')
    plt.ylim(125000, 140000)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    ax.bar(year, population, align='center', color='darkseagreen', edgecolor='white')
    for a, b in zip(year, population):
        plt.text(a, b + 0.05, '%.0f' % b, ha='center', va='bottom', fontsize=11)
    plt.xlabel(u'年份')
    plt.xticks(rotation=45)
    plt.ylabel(u'万人')
    plt.title(u'1999-2018年末总人口条形图')
    plt.show()

def plot2(year, male, female):
    r1 = []
    r2 = []
    for i in range(len(male)):
        r1.append(male[i] / (male[i] + female[i]))
        r2.append(female[i] / (male[i] + female[i]))
    plt.figure(figsize=(10, 5))
    # plt.ylim(0, 1)
    ax = plt.subplot()  # 创建图片区域
    plt.title("1999-2018年全国男性人口和女性人口占比变化折线图")
    plt.xlabel(u'年份')
    plt.xticks(rotation=45)
    plt.ylabel(u'1')
    line1, = plt.plot(year, r1)
    line2, = plt.plot(year, r2)
    for a, b in zip(year, r1):
        plt.text(a, b + 0.03, '%.2f' % b, ha='center', va='bottom', fontsize=9)
    plt.legend((line1, line2), ('男性人口占比', "女性人口占比"))
    plt.grid(color='whitesmoke', ls='--')
    plt.show()

def plotdata():
    conn = sqlite3.connect("population.db")
    cur = conn.cursor()
    cur.execute('select * from population ')
    data = cur.fetchall()
    cur.close()
    conn.close()

    year = [i[0] for i in data]
    population = [i[1] for i in data]
    male = [i[2] for i in data]
    female = [i[3] for i in data]
    print(population)
    print(male)
    print(female)

    plot1(year, population)

    plot2(year, male, female)


if __name__ == '__main__':

    # 从国家统计局获取人口数据并存入本地数据库population.db
    # getpopulation()

    # 作图
    plotdata()
