# -*- coding: utf-8 -*-

import requests
import json
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


if __name__ == '__main__':

    Cookie = "JSESSIONID=EBF8BACD3FEC0F066623339F04231D7E; u=1; SL_GWPT_Show_Hide_tmp=1; SL_wptGlobTipTmp=1"
    # 设置动态js的url
    url = 'http://data.stats.gov.cn/easyquery.htm?m=QueryData&dbcode=hgnd&rowcode=zb&colcode=sj&wds=%5B%5D&dfwds=%5B%7B%22wdcode%22%3A%22sj%22%2C%22valuecode%22%3A%22LAST20%22%7D%5D&k1=1554383870752'
    # 设置requests请求的 headers
    headers = {
        # 'User-agent': random.choice(USER_AGENTS),  # 设置get请求的User-Agent，用于伪装浏览器UA
        'Cookie': Cookie,
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Host': 'data.stats.gov.cn',
        'Referer': 'http://data.stats.gov.cn/easyquery.htm?cn=C01&zb=A0301&sj=2018'
    }

    # 设置页面索引
    pageIndex = 0
    # 设置url post请求的参数
    data = {
        'page': pageIndex,
        'disclosureType': 8
    }

    # requests post请求
    req = requests.post(url, data=data, headers=headers)
    # print(req.content)

    year = []
    population = []
    male = []
    female = []
    data = json.loads(req.text)
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

    fig = plt.figure()  # 创建画布
    ax = plt.subplot()  # 创建图片区域
    plt.grid(color='lightgrey', ls='--')
    plt.ylim(125000, 140000)
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    ax.bar(year, population, align='edge', color='sandybrown', edgecolor='white')
    plt.xlabel(u'年份')
    plt.ylabel(u'万人')
    plt.title(u'1999-2018年末总人口')
    plt.show()

    plt.plot(year, male)
    plt.plot(year, female)
    plt.show()
