import requests
import util
from settings import *
import os
import settings
import time
import random
import json
import traceback
from collections import deque

def get_all_data(stock, headers, dict_day):
    timestamp = util.getTimestamp()
    try:
        url = 'http://d.10jqka.com.cn/v6/line/hs_' + stock + '/01/all.js'  # 002613
        dataflow = util.get_json_from_url(url, headers)
        totalDays, sortYear, name, startDate, priceFactor, price, volumn, dates, issuePrice = \
            int(dataflow['total']), dataflow['sortYear'], dataflow['name'], dataflow['start'], dataflow['priceFactor'], dataflow['price'], \
            dataflow['volumn'], dataflow['dates'], dataflow['issuePrice']

        priceSum = price.split(',')
        volumn = volumn.split(',')
        # Price
        price_di = [round(int(priceSum[4*i])/priceFactor,2) for i in range(totalDays)]
        price_kai = [round(int(priceSum[4*i+1])/priceFactor+price_di[i],2) for i in range(totalDays)]
        price_gao = [round(int(priceSum[4*i+2])/priceFactor+price_di[i],2) for i in range(totalDays)]
        price_shou = [round(int(priceSum[4*i+3])/priceFactor+price_di[i],2) for i in range(totalDays)]
        if totalDays == 0 or len(price_di) == 0:
            print("该公司还未上市：" + stock+" "+name)
            return dict_day, None

        latest_di, latest_kai, latest_shou, latest_gao = price_di[-1], price_kai[-1], price_shou[-1], price_gao[-1]
        # Volumn
        volumn = [int(volumn[i])/10000 for i in range(totalDays)]
        latest_volumn = volumn[-1]
        AvePrice_5, AveVolumn_5, AvePrice_20, AveVolumn_20 = None, None, None, None
        latest_AvePrice_5, latest_AveVolumn_5, latest_AvePrice_20, latest_AveVolumn_20 = None, None, None, None
        #生成5日线 20日线
        if totalDays>=5:
            AvePrice_5 = util.get_ave_data(price_shou,5,totalDays)
            AveVolumn_5 = util.get_ave_data(volumn,5,totalDays)
            latest_AvePrice_5, latest_AveVolumn_5 = round(AvePrice_5[-1],2), round(AveVolumn_5[-1],2)

        if totalDays>=20:
            AvePrice_20 = util.get_ave_data(price_shou,20,totalDays)
            AveVolumn_20 = util.get_ave_data(volumn, 20, totalDays)
            latest_AvePrice_20, latest_AveVolumn_20 = round(AvePrice_20[-1]), round(AveVolumn_20[-1])


        dict_info = {}

        # direct_update_keys = ["price_di","price_kai","price_gao","price_shou","volumn"]
        # other_update_keys = ["latest_shou","latest_volumn","latest_AvePrice_20","AvePrice_20","latest_AveVolumn_20","AveVolumn_20"]

        dict_info["name"] = name
        dict_info["price_di"] = price_di
        dict_info["price_kai"] = price_kai
        dict_info["price_gao"] = price_gao
        dict_info["price_shou"] = price_shou
        dict_info["volumn"] = volumn
        dict_info["latest_shou"] = latest_shou
        dict_info["latest_volumn"] = latest_volumn
        dict_info["lastModify"] = timestamp

        if totalDays >= 20:
            dict_info["latest_AvePrice_20"] = latest_AvePrice_20
            dict_info["AvePrice_20"] = AvePrice_20
            dict_info["latest_AveVolumn_20"] = latest_AveVolumn_20
            dict_info["AveVolumn_20"] = AveVolumn_20
        if totalDays >= 5:
            dict_info["latest_AvePrice_5"] = latest_AvePrice_5
            dict_info["AvePrice_5"] = AvePrice_5
            dict_info["latest_AveVolumn_5"] = latest_AveVolumn_5
            dict_info["AveVolumn_5"] = AveVolumn_5

        dict_day[stock] = dict_info
        print("下载完成：" + stock +" "+name)
        return dict_day, None

    except Exception as ex:
        print("遇到错误：" + stock)
        traceback.print_exc()
        return dict_day, stock


def crawl_history_data(mode=settings.UPDATE):

    # dict_day = readDict("alldata.txt")
    stocks = []
    if mode == settings.ALL_DATA:
        stocks = deque(util.getStockIndices())
    elif mode == settings.UPDATE:
        stocks = deque(util.checkStockMissing())
    elif mode == settings.FromFailure:
        stocks = deque(util.readDict("Download_fail.txt", "set"))
    elif mode == settings.NotFound:
        stocks = deque(util.readDict("notFound_batches.txt", "set"))
    else:
        raise Exception("Mode not found.")

    downloaded,  dict_day, fail_set = 0,  {}, set()
    index = len(os.listdir(dict_basedir))
    while not len(stocks) == 0:
        stock = stocks.popleft()

        dict_day, failed = get_all_data(stock, settings.common_header, dict_day)#0  if random.random()<0.5 else 1
        if failed is None:
            downloaded += 1
            print("Downloaded: "+str(downloaded))
            if stock in fail_set:
                fail_set.remove(stock)
        elif failed not in fail_set:
            stocks.append(failed)
            fail_set.add(failed)

        if len(dict_day) >= 256:
            # Save Model
            util.saveDict(dict_day,"batches"+str(index)+".txt")
            index += 1
            dict_day = {}

    # 保存剩余的数据
    if len(dict_day) > 0:
        # Save Model
        util.saveDict(dict_day, "batches" + str(index) + ".txt")
        index += 1
        dict_day = {}

    return fail_set

#从EastMoney上爬取当天所有股票的涨跌信息
# def crawl_today_data():
#     url = settings.setting_dict["eastMoney"]["URL_START"].format(1, util.getTimestamp("millis"))
#     dataflow = util.get_json_from_url(url, settings.common_header)["data"]["diff"] #list
#     #print(dataflow["data"])
#     for data in dataflow:
#
#         for key in settings.map_easyMoney_dict:



if __name__ == '__main__':
    fail_set = crawl_history_data(settings.ALL_DATA)
    print(fail_set)
    # 保存下载失败的代码
    util.saveDict(fail_set,"download_fail_history_data.txt")

