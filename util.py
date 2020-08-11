import traceback
import time
from bs4 import BeautifulSoup
import re
import csv
import os
import settings
import time
import random
import json
import traceback
import requests
import math


def readDict(file, type="dict"):
    f = open(file, 'r')
    res = {}
    if type == "set":
        res = set()
    try:
        res = eval(f.read())
    except Exception as ex:
        print("遇到错误：readDict")

        traceback.print_exc()
    f.close()
    print("read successfully")
    # if type == "set":
    print("Loaded records: " + str(len(res)))
    return res


def saveDict(res, file):
    #dict set都适用
    f = open(file, 'w')
    f.write(str(res))
    f.close()
    print("save successfully: " + file)


def getStockIndices():
    column = []
    with open('ths.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        column = [row[1] for row in reader]
        column = column[1:]
        column = [column[i].zfill(6) for i in range(len(column))]
    return column


def getStockNames():
    column = []
    with open('ths.csv', 'r') as csvfile:
        reader = csv.reader(csvfile)
        column = [row[2] for row in reader]
        column = column[1:]
    return column


def getStockDict(filename):
    # indices, names, price_shou, huanshou, volumnRate, volumn, TTM, dict_res = [], [], [],[], [], [],[], {}
    dict_res = {}
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) == 0:
                continue
            indices,names,price_shou, huanshou, volumnRate, volumn, PE = row[1],row[2],row[3],row[10],row[11],row[13],row[16]
            price_gao, price_di, price_kai = row[4], row[5], row[6]
            sector, region, concept, netMoney = row[17],row[18],row[19],row[20]
            if not indices=="代码":
        # for i in range(1, len(indices)):
                if price_shou=='-':
                    print("请检查 {}/{} 是否今日停牌".format(names,indices))
                    continue
                new_dict = {}
                new_dict["name"] = names
                new_dict["price_gao"] = price_gao if price_gao=='-' or not isinstance(price_gao,str) else eval(price_gao)
                new_dict["price_di"] = price_di if price_di=='-' or  not isinstance(price_di,str) else eval(price_di)
                new_dict["price_kai"] = price_kai if price_kai=='-' or  not isinstance(price_kai,str) else eval(price_kai)
                new_dict["price_shou"] = price_shou if price_shou=='-' or  not isinstance(price_shou,str) else eval(price_shou)
                new_dict["huanshou"] = huanshou if huanshou=='-' or  not isinstance(huanshou,str) else eval(huanshou)
                new_dict["volumnRate"] = volumnRate if volumnRate=='-' or  not isinstance(volumnRate,str) else eval(volumnRate)
                new_dict["volumn"] = volumn if volumn=='-' or  not isinstance(volumn,str) else eval(volumn)
                new_dict["PE"] = PE if PE=='-' or  not isinstance(PE,str) else eval(PE)
                new_dict["sector"] = sector
                new_dict["region"] = region
                new_dict["concept"] = concept
                new_dict["netMoney"] = netMoney/10000 if netMoney=='-' or  not isinstance(netMoney,str) else eval(netMoney)/10000

                dict_res[indices] = new_dict
    print("Loaded Stock Info: "+str(len(dict_res)))
    return dict_res



def get_ave_data(data, period, totalDays):
    res = [0.0] * (totalDays - period + 1)
    # 初始值
    # for i in range(period):
    #     res[0] += data[i] / period
    # res[0] = round(res[0],2)
    for i in range(totalDays - period + 1):
        for j in range(period):
            res[i] += data[i+j]
        res[i] = round(res[i] / period, 2)
        # res[i] = round(res[i - 1] + (data[i + period - 1] - data[i - 1]) / period, 2)

    return res


def getTimestamp(type="self"):
    if type == "self":
        return time.strftime('%Y%m%d', time.localtime(time.time()))
    else:
        return int(round(time.time() * 1000))

#从同花顺主页动态获取页数范围
def get_THS_max_page(url=None,numTries=3):
    if numTries<0:
        raise Exception("get_THS_max_page 出错")
    if url==None:
        url = settings.setting_dict["THS"]["URL_START"]+"1"
    # Source url: http://q.10jqka.com.cn//index/index/board/all/field/zdf/order/desc/page/1
    page_source = common_downloader(url,num_retries=3)
    try:
        #读取html文件
        page=BeautifulSoup(page_source,'html5lib')
        #搜索目标信息
        # mu_mes = page.find('div',{'style':re.compile('position: relative; min-height: ')})
        # class="css-901oao r-hkyrab r-1qd0xha r-a023e6 r-16dba41 r-ad9z0x r-bcqeeo r-bnwqim r-qvutc0"
        mu_meses = page.find_all('span',{'class':re.compile('page_info')})
        page = mu_meses[0].get_text().split('/')[1]
        print('MAX_PAGE: '+ page)
        return int(page)
    except AttributeError as e:
        print('Error Occured while loading MAX_PAGE')
        traceback.print_exc()
        return get_THS_max_page(url,numTries-1)

def get_zhangting(url=None,numTries=3):
    if numTries<0:
        raise Exception("get_zhangting 出错")
    if url==None:
        url = settings.setting_dict["THS"]["URL_START"]+"1"
    # Source url: 'http://q.10jqka.com.cn/'
    page_source = common_downloader(url,num_retries=3)
    try:
        text = get_json_from_url(url,settings.common_header,head_cut=False)
        return text["zdt_data"]["last_zdt"]["ztzs"], text["zdt_data"]["last_zdt"]["dtzs"]
    except AttributeError as e:
        print('Error Occured while loading get_zhangting')
        traceback.print_exc()
        return get_zhangting(url,numTries-1)

def get_Shanghai(dict_data:dict, url=None,  numTries=3):
    if numTries < 0:
        raise Exception("get_zhangting 出错")
    if url == None:
        url = settings.setting_dict["THS"]["URL_START"] + "1"
    # Source url: 'http://q.10jqka.com.cn/'
    page_source = common_downloader(url, num_retries=3)
    try:
        dict_new = {}
        stdoutInfo = common_downloader(url)
        index = url[-6:]
        tempData = re.search('''(")(.+)(")''', stdoutInfo).group(2)
        stockInfo = tempData.split(",")
        #stockCode = stockCode,
        stockName   = stockInfo[0]
        dict_new["stockName"] = stockName
        stockEnd    = stockInfo[1]  #当前价，15点后为收盘价
        dict_new["stockEnd"] = stockEnd
        stockZD     = stockInfo[2]  #涨跌
        stockLastEnd= str(float(stockEnd) - float(stockZD)) #开盘价
        stockFD     = stockInfo[3]  #幅度
        dict_new["stockFD"] = stockFD
        stockZS     = stockInfo[4]  #总手
        stockZS_W   = str(int(stockZS) / 100)
        stockJE     = stockInfo[5]  #金额
        stockJE_Y   = str(int(stockJE) / 10000)
        dict_new["stockJE_Y"] = stockJE_Y
        content = "#" + stockName + "#" + "(" + str(index) + ")" + " 收盘：" \
          + stockEnd + "，涨跌：" + stockZD + "，幅度：" + stockFD + "%" \
          + "，总手：" + stockZS_W + "万" + "，金额：" + stockJE_Y + "亿" + "  "
        print(content)
        dict_data[index] = dict_new

    except AttributeError as e:
        print('Error Occured while loading get_Shanghai')
        traceback.print_exc()
        return get_Shanghai(url,numTries-1)

def get_eastMoney_max_page(url=None,numPerPage=20,numTries=3):
    if numTries<0:
        raise Exception("get_eastMoney_max_page 出错")
    if url==None:
        url = settings.setting_dict["eastMoney"]["URL_START"].format(getTimestamp("millis"), 1, getTimestamp("millis"))
    try:
        total = get_json_from_url(url, settings.common_header)["data"]["total"]  # list
        print("MAX_PAGE: {}".format(math.ceil(total / numPerPage)))
        return math.ceil(total / numPerPage)
    except Exception as ex:
        print("遇到错误：get_eastMoney_max_page")
        traceback.print_exc()
        return get_eastMoney_max_page(url, numPerPage=20, numTries=numTries-1)


def get_latest_ave(dict_info:dict,day:int,key:str,update_keys:dict):
    if len(dict_info[key]) >= day:
        sum_price = 0.0
        for i in range(day):
            sum_price += dict_info[key][-1 - i]

        for update_key in update_keys:
            if update_keys[update_key]:
                if update_key not in dict_info:
                    dict_info[update_key] = []
                dict_info[update_key].append(round(sum_price / day, 2))
            else:
                dict_info[update_key] = round(sum_price / day, 2)


def common_downloader(url, num_retries=3, t=max(2,random.random()*5)):
    # if self.proxy_con == 0:
    #     proxies = self.proxy_get()
    # else:
    #     proxies = self.proxy_save
    # self.proxy_save = proxies       #更换代理值

    try:
        time.sleep(t)
        headers = settings.common_header #random.choice(headers_list)
        r = requests.get(url, headers = headers, proxies=None, timeout=4)
        return r.text
    except:
        if num_retries > 0:
            print("重新下载")
            common_downloader(url, num_retries-1)
        else:
            print("下载失败")
            return ""

def checkStockMissing():
    stocks = set(getStockIndices())
    num_sum = len(stocks)
    num_downloaded = 0
    dict_dirs = os.listdir(settings.dict_basedir)
    # 在所有batch中寻找代号，找到的话就从set中删除
    for dict_dir in dict_dirs:
        print("Reading From: " + dict_dir)
        dict_m = readDict(settings.dict_basedir + "/" + dict_dir)
        num_downloaded += len(dict_m)
        for key in dict_m:
            if key in stocks:
                stocks.remove(key)
    print("代码总数： " + str(num_sum))
    print("已下载总数： " + str(num_downloaded))
    print("剩余未下载的代码数量： " + str(len(stocks)))
    return stocks

def get_json_from_url(url, headers=None, t=max(2,random.random()*5),numTries=3,head_cut = True):
    # for stock in stocks:
    if headers==None:
        headers = settings.common_header
    if numTries<0:
        raise Exception("下载失败！{}".format(url))
    try:
        time.sleep(t)   #设置延时
        # headers = myHeader # random.choice(headers_list)
        r = requests.get(url, headers = headers, proxies=None, timeout=4)
        if head_cut:
            json_str = r.text[r.text.find('{'):r.text.rfind('}')+1]
        else:
            json_str = r.text
        print("Test:" + url)
        print(json_str[:100]+" User-Agent: "+headers["User-Agent"])
        dataflow = json.loads(json_str) #json.loads(r.text)
        return dataflow
    except Exception as ex:
        print("遇到错误：" + url)
        traceback.print_exc()
        return get_json_from_url(url,headers,t,numTries-1)



if __name__ == '__main__':
    # dict_test = readDict("./data_batch/data_batch0.txt")
    # print(dict_test["N江航"])
    # print(getTimestamp())
    # remain_set = deque(checkStockMissing())
    # print(remain_set)
    # print(len(getStockDict("eastMoney20200803.csv")))
    print(getTimestamp("millis"))


