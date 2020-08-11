import requests
import util
from settings import *
from bs4 import BeautifulSoup
import sys
import time
import random
import csv
import util
import settings
import traceback

class crawl(object):

    def __init__(self,file,host=None, URL_START=None, PARAMS=None, fieldnames=settings.fieldnames,MAX_PAGE=settings.MAX_PAGE):


        self.timestamp = util.getTimestamp()
        self.PAGE_TRACK = settings.PAGE_TRACK    #跟踪次数
        self.FLAG = settings.FLAG                #设置标志位
        self.PAGE_LIST = []     #第一次获取失败的 html 的 列表
        self.URL_START = URL_START     #初始链接
        self.PARAMS = PARAMS            #url 构造参数
        self.MAX_PAGE = MAX_PAGE
        self.host = host
        if host is not None:
            setting_dict = settings.setting_dict[host]
            self.URL_START = setting_dict["URL_START"]
            self.PARAMS = setting_dict["PARAMS"]
            if host == "THS":
                self.MAX_PAGE = util.get_THS_max_page()
            else:
                self.MAX_PAGE = util.get_eastMoney_max_page()
            print("MAX_PAGE: {}".format(self.MAX_PAGE))

        self.proxy_save = None   #用于存储代理
        self.proxy_con  = 0      #用于控制代理什么时候更换 
        self.fieldnames = fieldnames
        self.file = open(file,"w") #open("ths"+str(self.timestamp)+".csv",'a', newline='')   #打开文件
        self.writer = csv.DictWriter(self.file, fieldnames = self.fieldnames)
        self.writer.writeheader()

    def proxy_get(self, num_retries=2):
        """
        #代理获取模块

        """
        try:
            r_proxy = requests.get(self.PROXY_POOL_API, timeout = 5)
            proxy = r_proxy.text    #指定代理
            print("代理是", proxy)
            proxies = {
                "http": 'http://' + proxy,
                "https": 'https://' + proxy,
                }
            return proxies
        except:
            if num_retries > 0:
                print("代理获取失败，重新获取")
                self.proxy_get(num_retries-1)

    def url_yield(self):
        """
        :func 用于生成url
        :yield items
        """
        for i in range(1, self.MAX_PAGE + 1):
            self.PAGE_TRACK = i
            self.FLAG += 1
            print('FLAG 是：', self.FLAG)
            url = ""
            if self.host == "THS":
                url = "{}{}{}".format(self.URL_START, i, self.PARAMS)
            elif self.host == "eastMoney":
                url = self.URL_START.format(util.getTimestamp("millis"),i, util.getTimestamp("millis"))
            yield url

    def url_omi(self):
        print("开始补漏")
        length_pl = len(self.PAGE_LIST) 
        if length_pl != 0:
            for i in range(length_pl):
                self.PAGE_TRACK = self.PAGE_LIST.pop(0)
                url = "{}{}{}".format(self.URL_START, self.PAGE_TRACK, self.PARAMS) 
                yield url

    def downloader(self, url, num_retries=3):
        # if self.proxy_con == 0:
        #     proxies = self.proxy_get()
        # else:
        #     proxies = self.proxy_save
        # self.proxy_save = proxies       #更换代理值

        try:
            time.sleep(max(2,random.random()*5))
            headers = settings.common_header #random.choice(headers_list)
            r = requests.get(url, headers = headers, proxies=None, timeout=4)
        except:
            if num_retries > 0:
                print("重新下载")
                self.proxy_con = 0
                self.downloader(url,num_retries-1)
            else:
                # 首先应该判断 该页是否存在列表中，如果不存在， 则将其加入其中
                if not self.PAGE_TRACK in self.PAGE_LIST:
                    # 将获取失败的url保存起来，后面再次循环利用，将元素添加在末尾，
                        self.PAGE_LIST.append(self.PAGE_TRACK)
        else:            
            return r.text

    def items_return(self):
        sys.setrecursionlimit(5000)
        count = 0
        while True:
            if self.FLAG < self.MAX_PAGE:
                url_list = self.url_yield()  # 获取url
            else:
                url_list = self.url_omi()
                if len(self.PAGE_LIST) == 0:
                    break
            print("执行到了获取模块")

            #一页20个股票，大概3800只股票，所以大概是190页
            for url in url_list:
                items = {}  # 建立一个空字典，用于信息存储
                try:
                    if self.host == "THS":
                            html = self.downloader(url)
                            # 打印提示信息
                            print('URL is:', url)
                            soup = BeautifulSoup(html, 'lxml')
                            for tr in soup.find('tbody').find_all('tr'):
                                td_list = tr.find_all('td')
                                # [序号 代码 名称 现价 涨跌幅 涨跌 涨速 换手 量比 振幅 成交额 流通股  流通市值 市盈率]
                                items['代码'] = td_list[1].string
                                items['名称'] = td_list[2].string
                                items['现价'] = td_list[3].string
                                items['涨跌幅'] = td_list[4].string
                                items['涨跌'] = td_list[5].string
                                items['涨速'] = td_list[6].string
                                items['换手'] = td_list[7].string
                                items['量比'] = td_list[8].string
                                items['振幅'] = td_list[9].string
                                items['成交额'] = td_list[10].string
                                items['流通股'] = td_list[11].string
                                items['流通市值'] = td_list[12].string
                                items['市盈率'] = td_list[13].string
                                self.writer.writerow(items)
                                print(items)

                    elif self.host == "eastMoney":
                        # url = settings.setting_dict["eastMoney"]["URL_START"].format(1, util.getTimestamp("millis"))
                        dataflow = util.get_json_from_url(url, settings.common_header)["data"]["diff"]  # list
                        # print(dataflow["data"])
                        for data in dataflow:
                            items["代码"] = data[settings.index_easyMoney_name]
                            for key in settings.map_easyMoney_dict:
                                items[key] = data[settings.map_easyMoney_dict[key]]
                            self.writer.writerow(items)
                            print(items)

                    print("保存成功")
                    #如果保存成功，则继续使用代理
                    self.proxy_con = 1
                except:
                    print("解析失败")
                    traceback.print_exc()
                    # 解析失败，则将代理换掉
                    self.proxy_con = 0
                    # print(html)
                    if not self.PAGE_TRACK in self.PAGE_LIST:
                        self.PAGE_LIST.append(self.PAGE_TRACK)
                    else:
                        count += 1
            # 如果下载失败的数量大于2，则表示网络不畅，直接退出
            if count == 2:
                break

        if len(self.PAGE_LIST) != 0:
            print("【注意！！】有 {} 页下载失败！".format(len(self.PAGE_LIST)))
            util.saveDict(self.PAGE_LIST, "download_fail_dailydata_pages.txt")
        return self.PAGE_LIST


if __name__ == '__main__':
    app = crawl(file="eastMoney"+util.getTimestamp()+".csv",host="eastMoney")
    failed_list = app.items_return()

