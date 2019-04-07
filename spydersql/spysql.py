# -*- coding: utf-8 -*-

import requests
import json
import time
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

def gettime():
    return int(round(time.time() * 1000))

if __name__ == '__main__':

    # 用来自定义头部的
    headers = {}
    # 用来传递参数的
    keyvalue = {}
    # 目标网址(问号前面的东西)
    url = 'http://data.stats.gov.cn/easyquery.htm'

    # 头部的填充
    headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) ' \
                            'AppleWebKit/605.1.15 (KHTML, like Gecko) ' \
                            'Version/12.0 Safari/605.1.15'

    # 下面是参数的填充
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
    r = s.get(url, params=keyvalue, headers=headers)
    # 打印返回过来的状态码
    print(r.status_code)
    # 修改dfwds字段内容
    keyvalue['dfwds'] = '[{"wdcode":"sj","valuecode":"LAST20"}]'
    # 再次进行请求
    r = s.get(url, params=keyvalue, headers=headers)
    # 此时我们就能获取到我们搜索到的数据了
    # print(r.text)

    year = []
    population = []
    male = []
    female = []
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

    year.reverse()
    population.reverse()
    male.reverse()
    female.reverse()

    # fig = plt.figure()  # 创建画布
    # ax = plt.subplot()  # 创建图片区域
    # plt.grid(color='lightgrey', ls='--')
    # plt.ylim(125000, 140000)
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # plt.rcParams['axes.unicode_minus'] = False
    # ax.bar(year, population, align='edge', color='sandybrown', edgecolor='white')
    # plt.xlabel(u'年份')
    # plt.ylabel(u'万人')
    # plt.title(u'1999-2018年末总人口')
    # plt.show()
    #
    # plt.plot(year, male)
    # plt.plot(year, female)
    # plt.show()
