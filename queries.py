import os
import settings
import util
import progressbar
import logging
import traceback

def query_price20LowerButAboutToReachCurrPrice(selected_sector:set=None):
    timestamp = util.getTimestamp("self")
    file = open("price20LowerButAboutToReachCurrPrice_{}.txt".format(timestamp), "w")
    res, found = {}, 0
    queryInfo = "Query:(ST除外)过去10个交易日，收盘价都比20日线高，最新收盘价不低于20的99%，不高于20的103%,最近量能低于5日均量"
    print(queryInfo)
    file.write(queryInfo+'\n')
    dict_dirs = os.listdir(settings.dict_basedir)
    for dict_dir in dict_dirs:
        print("Querying: "+dict_dir)
        dict_m = util.readDict(settings.dict_basedir+"/"+dict_dir)
        for key in dict_m:
            dict_k = dict_m[key]
            # 排除ST
            try:
                if "ST" in dict_k["name"]:
                    continue
                # 排除次新
                if "AvePrice_20" in dict_k and len(dict_k["AvePrice_20"]) > 250:
                    # 过滤条件
                    if selected_sector is not None:
                        if "sector" not in dict_k or dict_k["sector"] not in selected_sector:
                            continue


                    date_20Lower = [1 if dict_k["AvePrice_20"][-i]<dict_k["price_shou"][-i] else 0 for i in range(2, 12)]
                    if sum(date_20Lower) == 10 and \
                            dict_k["price_shou"][-1] >= dict_k["AvePrice_20"][-1]*0.99 and \
                            dict_k["price_shou"][-1] <= dict_k["AvePrice_20"][-1]*1.02:
                        res[key] = dict_k["name"]
                        found += 1
                        queryInfo = "Found: ({}) {} {} {} {}".format(found,key,dict_k["name"], dict_k["price_shou"][-1] , dict_k["AvePrice_20"][-1])
                        print(queryInfo)
                        file.write(queryInfo+'\n')
            except Exception as ex:
                print("遇到错误：" + str(dict_k))
                traceback.print_exc()

    file.close()
    return res


def query_price5RiseAndFall(percent=0.618):
    print("Query:5日线大幅上涨后遇到50%后撤到0.618或者0.5，最近量能低于5日均量")



def query_panzheng():
    # 中枢盘整模型

    pass

def querySpecific(query_dir:dict):
    dict_dirs = os.listdir(settings.dict_basedir)
    print("Query Num: {}".format(len(query_dir)))
    visited = set()
    query_result = []

    for dict_dir in dict_dirs:
        print("Querying: " + dict_dir)
        dict_m = util.readDict(settings.dict_basedir + "/" + dict_dir)
        for stock in query_dir:
            if query_dir[stock] is None:
                return dict_m[stock]
            attrs, indices = query_dir[stock]
            if stock in visited:
                continue
            if stock in dict_m:

                res = "{}/{} ".format(stock, dict_m[stock]["name"])
                for i in range(len(attrs)):
                    if attrs[i] not in dict_m[stock]:
                        print("{}/{} 没有 {}".format(stock,dict_m[stock]["name"],attrs[i]))
                        continue
                    if indices[i] == None:
                        res += " {} {}".format(attrs[i],dict_m[stock][attrs[i]])
                        # print("Query Succeeded: {}/{} {} {}".format(stock,dict_m[stock]["name"],attrs[i],res))
                        query_result.append(res)
                    else:
                        res += " {} {} {}".format(attrs[i], indices[i], dict_m[stock][attrs[i]][indices[i]])
                        # print("Query Succeeded: {}/{} {} {} {}".format(stock, dict_m[stock]["name"], attrs[i], indices[i], res))
                        query_result.append(res)
                print("Query Success. {}".format(res))
                visited.add(stock)
                if len(visited)==len(dict_dir):
                    break
        if len(visited) == len(dict_dir):
            break
    util.saveDict(query_result,"querySpecific_{}.txt".format(util.getTimestamp()))
    return query_result

if __name__ == '__main__':
    # match_result = query_price20LowerButAboutToReachCurrPrice()
    # print("Match result Num: "+str(len(match_result)))
    # print(match_result)
    # query_list = querySpecific({
    #     "000066":[["3DayNetMoney","netMoney"],[None,-1]],
    #     "002739":[["3DayNetMoney","netMoney"],[None,-1]],
    #     "000063":[["3DayNetMoney","netMoney"],[None,-1]],
    #     "000977":[["3DayNetMoney","netMoney"],[None,-1]],
    #     "600663":[["3DayNetMoney","netMoney"],[None,-1]],
    #     "603799":[["3DayNetMoney","netMoney"],[None,-1]],
    #     "600104":[["3DayNetMoney","netMoney"],[None,-1]],
    #     "603986":[["3DayNetMoney","netMoney"],[None,-1]],
    #     "002887":[["3DayNetMoney","netMoney"],[None,-1]],
    #
    #                            })
    # for query in query_list:
    #     print(query)
    print(query_price20LowerButAboutToReachCurrPrice())
    # dict_test = util.readDict("./batches/data_batch15.txt")
    # print(len(dict_test))
