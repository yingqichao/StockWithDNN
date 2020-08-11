import util
import os
import settings
import spider
import time
import traceback

def data_decimal_clean():
    print("Reading Data...")
    dict_day = util.readDict("alldata.txt")

    for name in dict_day:
        print("Cleaning: "+name)
        dict_info = dict_day[name]
        dict_info["price_di"] = [round(dict_info["price_di"][i],2) for i in range(len(dict_info["price_di"]))]
        dict_info["price_kai"] = [round(dict_info["price_kai"][i],2) for i in range(len(dict_info["price_kai"]))]
        dict_info["price_gao"] = [round(dict_info["price_gao"][i],2) for i in range(len(dict_info["price_gao"]))]
        dict_info["price_shou"] = [round(dict_info["price_shou"][i],2) for i in range(len(dict_info["price_shou"]))]
        dict_info["volumn"] = [round(dict_info["volumn"][i],2) for i in range(len(dict_info["volumn"]))]
        dict_info["latest_shou"] = round(dict_info["latest_shou"],2)
        dict_info["latest_volumn"] = round(dict_info["latest_volumn"],2)
        totalDays = len(dict_info["price_di"])
        if totalDays >= 20:
            dict_info["latest_AvePrice_20"] = [round(dict_info["latest_AvePrice_20"][i],2) for i in
                                               range(len(dict_info["latest_AvePrice_20"]))]
            dict_info["latest_AveVolumn_20"] = [round(dict_info["latest_AveVolumn_20"][i], 2) for i in
                                                range(len(dict_info["latest_AveVolumn_20"]))]
        if totalDays >= 5:
            dict_info["latest_AvePrice_5"] = [round(dict_info["latest_AvePrice_5"][i], 2) for i in
                                               range(len(dict_info["latest_AvePrice_5"]))]
            dict_info["latest_AveVolumn_5"] = [round(dict_info["latest_AveVolumn_5"][i], 2) for i in
                                                range(len(dict_info["latest_AveVolumn_5"]))]

    # Save Model
    util.saveDict(dict_day,"all.txt")

def modify_dict_by_key():
    dict_dirs = os.listdir(settings.dict_basedir)
    # 获取股票名和代码的对应dict并更新字典
    # dict_name_index = util.getStockDict()
    #
    # for dict_dir in dict_dirs:
    #     print("Modifying: "+dict_dir)
    #     dict_m = util.readDict(dict_basedir+"/"+dict_dir)
    #     new_dict_m = {}
    #     for key in dict_m:
    #         # 获取代号
    #         index = dict_name_index[key]
    #         dict_k = dict_m[key]
    #         dict_k["name"] = key
    #         new_dict_m[index] = dict_k
    #     util.saveDict(new_dict_m, dict_dir)

    # 补上5 20涨幅
    for dict_dir in dict_dirs:
        print("Modifying: "+dict_dir)
        dict_m = util.readDict(settings.dict_basedir+"/"+dict_dir)
        for key in dict_m:
            dict_info = dict_m[key]
            totalDays = len(dict_info["price_shou"])
            # 生成5日线 20日线
            if totalDays >= 5:
                AvePrice_5 = util.get_ave_data(dict_info["price_shou"], 5, totalDays)
                AveVolumn_5 = util.get_ave_data(dict_info["volumn"], 5, totalDays)
                latest_AvePrice_5, latest_AveVolumn_5 = round(AvePrice_5[-1], 2), round(AveVolumn_5[-1], 2)
                dict_info["latest_AvePrice_5"] = latest_AvePrice_5
                dict_info["AvePrice_5"] = AvePrice_5
                dict_info["latest_AveVolumn_5"] = latest_AveVolumn_5
                dict_info["AveVolumn_5"] = AveVolumn_5

            if totalDays >= 20:
                AvePrice_20 = util.get_ave_data(dict_info["price_shou"], 20, totalDays)
                AveVolumn_20 = util.get_ave_data(dict_info["volumn"], 20, totalDays)
                latest_AvePrice_20, latest_AveVolumn_20 = round(AvePrice_20[-1]), round(AveVolumn_20[-1])
                dict_info["latest_AvePrice_20"] = latest_AvePrice_20
                dict_info["AvePrice_20"] = AvePrice_20
                dict_info["latest_AveVolumn_20"] = latest_AveVolumn_20
                dict_info["AveVolumn_20"] = AveVolumn_20

        util.saveDict(dict_m, dict_dir)

    # 加盖最后修改的时间戳
    # timestamp = util.getTimestamp()
    # for dict_dir in dict_dirs:
    #     print("Modifying: "+dict_dir)
    #     dict_m = util.readDict(settings.dict_basedir+"/"+dict_dir)
    #     for key in dict_m:
    #         dict_k = dict_m[key]
    #         dict_k["lastModify"] = timestamp
    #
    #     util.saveDict(dict_m, dict_dir)

def append_daily_into_last_batch(stock,dict_newInfo,dict_batch):

    dict_info = {}

    for update_key in settings.direct_update_keys:
        if update_key not in dict_info:
            dict_info[update_key] = []
        dict_info[update_key].append(dict_newInfo[update_key])
    # 更新行业 板块 地区
    if "sector" not in dict_info or isinstance(dict_info["concept"], list):
        dict_info["sector"] = dict_newInfo["sector"]
        dict_info["region"] = dict_newInfo["region"]
        # 概念可能有多个
        concepts = dict_newInfo["concept"].split(",")
        dict_info["concept"] = set(concepts)
    # 通过计算修改的数据：5 20均线均量
    # "latest_shou","latest_volumn","latest_AvePrice_20","AvePrice_20","latest_AveVolumn_20","AveVolumn_20"
    dict_info["latest_shou"] = dict_info["price_shou"][-1]
    dict_info["latest_volumn"] = dict_info["volumn"][-1]
    # 更新3/10日净流入数据
    util.get_latest_ave(dict_info, 3, "netMoney", {"3DayNetMoney": False})
    util.get_latest_ave(dict_info, 10, "netMoney", {"10DayNetMoney": False})
    # 更新 5 20 均量/均价
    util.get_latest_ave(dict_info, 20, "price_shou", {"AvePrice_20": True, "latest_AvePrice_20": False})
    util.get_latest_ave(dict_info, 20, "volumn", {"AveVolumn_20": True, "latest_AveVolumn_20": False})
    util.get_latest_ave(dict_info, 5, "price_shou", {"AvePrice_5": True, "latest_AvePrice_5": False})
    util.get_latest_ave(dict_info, 5, "volumn", {"AveVolumn_5": True, "latest_AveVolumn_5": False})
    # last 5 20涨幅
    if len(dict_info["price_shou"]) >= 5:
        dict_info["5DayRise"] = round((dict_info["price_shou"][-1] / dict_info["price_kai"][-5] - 1) * 100, 2)
    if len(dict_info["price_shou"]) >= 10:
        dict_info["10DayRise"] = round((dict_info["price_shou"][-1] / dict_info["price_kai"][-10] - 1) * 100, 2)
    if len(dict_info["price_shou"]) >= 20:
        dict_info["20DayRise"] = round((dict_info["price_shou"][-1] / dict_info["price_kai"][-20] - 1) * 100, 2)
    # 修改时间戳
    dict_info["lastModify"] = util.getTimestamp("self")
    dict_batch[stock] = dict_info

def update_daily_data(comitNewCrawl=False):
    filename = "eastMoney"+util.getTimestamp()+".csv"
    timestamp = util.getTimestamp()
    print("Filename "+filename)
    print("Timestamp: "+timestamp)
    # dict_netMoney = {}
    if comitNewCrawl:
        app = spider.crawl(file=filename,host="eastMoney")
        app.items_return()
        # 现在开始，不需要访问净流入网站
        # dict_netMoney = addNetMoney()
    # else:
    #     dict_netMoney = util.readDict("netMoney_{}.txt".format(util.getTimestamp("self")))
    dict_day = util.getStockDict(filename)
    print("Test:{}".format(dict_day["600667"]))
    print("读取到的daily data 条数： {}".format(len(dict_day)))
    num_updated = 0

    foundInBatches, notFound_day, notFound_batches, duplicated_data = set(), set(), set(), set()

    #更新数据后，需要补5 20均线，并更新5 20涨幅
    dict_dirs = os.listdir(settings.dict_basedir)
    for dict_dir in dict_dirs:
        print("Modifying: "+dict_dir)
        dict_m = util.readDict(settings.dict_basedir+"/"+dict_dir)
        for key in dict_m:
            if key in foundInBatches:
                #去除数据库中已经存在的重复数据
                duplicated_data.add(key)
                continue
            foundInBatches.add(key)
            if key not in dict_day:
                notFound_day.add(key)
                continue
            #更新数据，当天数据为dict_newInfo,历史数据为dict_info
            dict_newInfo = dict_day[key]
            dict_info = dict_m[key]
            try:
                if not dict_info["lastModify"] == timestamp:
                    # 直接修改的数据
                    # 添加净流入信息（netMoney已经加入到directModify中）
                    # if key in dict_netMoney:
                    #     if "netMoney" not in dict_info:
                    #         dict_info["netMoney"] = []
                    #     dict_info["netMoney"].append(dict_netMoney[key])


                    for update_key in settings.direct_update_keys:
                        if update_key not in dict_info:
                            dict_info[update_key] = []
                        dict_info[update_key].append(dict_newInfo[update_key])
                    # 更新行业 板块 地区
                    if "sector" not in dict_info or isinstance(dict_info["concept"],list):
                        dict_info["sector"] = dict_newInfo["sector"]
                        dict_info["region"] = dict_newInfo["region"]
                        # 概念可能有多个
                        concepts = dict_newInfo["concept"].split(",")
                        dict_info["concept"] = set(concepts)
                    #通过计算修改的数据：5 20均线均量
                    #"latest_shou","latest_volumn","latest_AvePrice_20","AvePrice_20","latest_AveVolumn_20","AveVolumn_20"
                    dict_info["latest_shou"] = dict_info["price_shou"][-1]
                    dict_info["latest_volumn"] = dict_info["volumn"][-1]
                    # 更新3/10日净流入数据
                    util.get_latest_ave(dict_info, 3, "netMoney", {"3DayNetMoney": False})
                    util.get_latest_ave(dict_info, 10, "netMoney", {"10DayNetMoney": False})
                    # 更新 5 20 均量/均价
                    util.get_latest_ave(dict_info, 20, "price_shou", {"AvePrice_20":True,"latest_AvePrice_20":False})
                    util.get_latest_ave(dict_info, 20, "volumn", {"AveVolumn_20":True,"latest_AveVolumn_20":False})
                    util.get_latest_ave(dict_info, 5, "price_shou", {"AvePrice_5": True, "latest_AvePrice_5": False})
                    util.get_latest_ave(dict_info, 5, "volumn", {"AveVolumn_5": True, "latest_AveVolumn_5": False})
                    # last 5 20涨幅
                    if len(dict_info["price_shou"]) >= 5:
                        try:
                            dict_info["5DayRise"] = round((dict_info["price_shou"][-1]/dict_info["price_kai"][-5]-1)*100,2)
                        except ZeroDivisionError as ex:
                            dict_info["5DayRise"] = round((dict_info["price_shou"][-1] / dict_info["price_shou"][-6] - 1) * 100, 2)
                            print("ZeroDivisionError:{}/{} Solved".format(key,dict_info["name"]))
                    if len(dict_info["price_shou"]) >= 20:
                        try:
                            dict_info["20DayRise"] = round((dict_info["price_shou"][-1]/dict_info["price_kai"][-20]-1)*100,2)
                        except ZeroDivisionError as ex:
                            dict_info["20DayRise"] = round((dict_info["price_shou"][-1] / dict_info["price_kai"][-21] - 1) * 100, 2)
                            print("ZeroDivisionError:{}/{} Solved".format(key, dict_info["name"]))
                    # 修改时间戳
                    dict_info["lastModify"] = timestamp
                    num_updated += 1
                # 更新后，从dict_day中删除这个stock
                dict_day.pop(key)
            except Exception as ex:
                print("遇到错误:{}/{} Solved".format(key,dict_info["name"]))
                traceback.print_exc()

        # 删除多余数据 RuntimeError: dictionary changed size during iteration
        for dupKey in duplicated_data:
            if dupKey in dict_m:
                dict_m.pop(dupKey)
        util.saveDict(dict_m, dict_dir)
        print("更新记录数量：{}".format(num_updated))

    # dict_day中剩余Stock没有在batches中出现过，需要补充下载
    for key in dict_day:
        notFound_batches.add(key)
    # 补充到最后一个batch中
    dict_dir = settings.dict_basedir+"/"+dict_dirs[-1]
    dict_m = util.readDict(dict_dir)
    for key in dict_day:
        append_daily_into_last_batch(key,dict_day[key],dict_m)

    util.saveDict(dict_m, dict_dir)

    #保存出错的结果
    # print("notFound in batches:")
    # print(notFound_batches)
    # util.saveDict(notFound_batches,"notFound_batches.txt")
    print("duplicated_data")
    print(duplicated_data)
    util.saveDict(duplicated_data, "duplicated_data.txt")
    # 这个情况是需要额外处理的！
    print("notFound_day")
    print(notFound_day)
    print("[Warning!!!] 有{}条数据没有更新成功，请检查是否停牌！".format(len(notFound_day)))
    util.saveDict(notFound_day, "notFound_day.txt")
    #最后统计大盘指数 涨跌停家数
    update_Shanghai()
    return len(notFound_day)

def update_Shanghai():
    zhangting, dieting = util.get_zhangting(url='http://q.10jqka.com.cn/api.php?t=indexflash&')
    print("涨停/跌停家数： {}/{}".format(zhangting, dieting))
    dict_data = {}
    for url in settings.Stock_data:
        util.get_Shanghai(dict_data, settings.Stock_data[url])
    dict_data['zhangting'] = zhangting
    dict_data['dieting'] = dieting
    # 保存到每日数据
    timestamp = util.getTimestamp()
    dict_everyday = util.readDict("大盘数据.txt")
    dict_everyday[timestamp] = dict_data
    util.saveDict(dict_everyday, "大盘数据.txt")

# def addNetMoney():
#     millis = util.getTimestamp("millis")
#     numPages = util.get_eastMoney_max_page(settings.net_money_url.format(1,millis,millis+167),numPerPage=50)
#     dict_netMoney = {}
#
#     for i in range(1,numPages+1):
#         print("Page {}/{}".format(i,numPages))
#         millis = util.getTimestamp("millis")
#         url = settings.net_money_url.format(i,millis,millis+167)
#         dataflow = util.get_json_from_url(url, settings.common_header)["data"]["diff"]  # list
#
#         for data in dataflow:
#             if not isinstance(data[settings.map_eastMoney_netMoney["主力净流入"]],str):
#                 key = data[settings.index_easyMoney_name]
#                 dict_netMoney[key] = data[settings.map_eastMoney_netMoney["主力净流入"]]/10000
#
#     print("NetMoney Got Records: "+str(len(dict_netMoney)))
#     util.saveDict(dict_netMoney,"netMoney_{}.txt".format(util.getTimestamp("self")))
#
#     return dict_netMoney


if __name__ == '__main__':
    #print (int(round(time.time() * 1000))-1596423136235)
    # update_daily_data(comitNewCrawl=True)
    # lens = update_daily_data(comitNewCrawl=True)
    # if lens !=0:
    update_daily_data(comitNewCrawl=True)
    # 为今天的新股手动加入到batch
    # dict_dirs = os.listdir(settings.dict_basedir)
    # dict_dir = settings.dict_basedir + "/" + dict_dirs[-1]
    # dict_m = util.readDict(dict_dir)
    # filename = "eastMoney" + util.getTimestamp() + ".csv"
    # timestamp = util.getTimestamp()
    # dict_day = util.getStockDict(filename)
    # notFound = util.readDict("notFound_batches.txt","set")
    # for stock in notFound:
    #     append_daily_into_last_batch(stock,dict_day[stock],dict_m)
    # util.saveDict(dict_m, dict_dir)

    # filename = "eastMoney" + util.getTimestamp() + ".csv"
    # app = spider.crawl(file=filename, host="eastMoney")
    # app.items_return()

