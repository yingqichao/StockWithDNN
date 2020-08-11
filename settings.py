from bs4 import BeautifulSoup
import re
from collections import deque
import util
# crawl_all ?
ALL_DATA = 0
UPDATE = 1
FromFailure = 2
NotFound = 3

dict_basedir = "./batches"

#必要参数设置
MAX_PAGE = 193   #最大页数
PAGE_TRACK = 1   #追踪到了第几页
MAX_GET = 1      #获取最大尝试次数
MAX_PARSE = 1    #解析尝试最大次数
MAX_CSV = 1      #文件保存最大次数
MAX_PROXY =1     #获取代理的最大次数
MAX_START = 1    #MAX_*的初始值
MAX_TRY = 4      #最大尝试次数
FLAG = 0         #用于标识，是否使用 url_omi() 函数

#初始链接
setting_dict = {
    "THS":{
        "URL_START":"http://q.10jqka.com.cn//index/index/board/all/field/zdf/order/desc/page/",
        "PARAMS" : "/ajax/1/",
        # "MaxPage" : util.get_THS_max_page()
    },
    "eastMoney":{
        # URL_START是一个template，需要.format填充时间戳、页码和时间戳
        # 主力资金流向网站：http://data.eastmoney.com/zjlx/detail.html
        # http://quote.eastmoney.com/center/gridlist.html#hs_a_board
        "URL_START":'http://47.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112401597019051519455_{}&pn={}&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152,f100,f102,f103,f62&_={}',
        "PARAMS" : "",
        # "MaxPage" : util.get_eastMoney_max_page()
    },

}



#第一次爬取的 html 缺失的页面 的url 列表
#先进先出的列表
# PAGE_LIST = []
direct_update_keys = ["price_di", "price_kai", "price_gao", "price_shou", "volumn","netMoney"]
# other_update_keys = ["latest_shou","latest_volumn","latest_AvePrice_20","AvePrice_20","latest_AveVolumn_20","AveVolumn_20"]

zhangting_url = 'http://q.10jqka.com.cn/'

Stock_data = {'创业板指':'http://hq.sinajs.cn/list=s_sz399006',
              '上证指数':'http://hq.sinajs.cn/list=s_sh000001',
              '深圳成指':'http://hq.sinajs.cn/list=s_sz399001'
}

# 资源网站
# 主力金额 http://data.10jqka.com.cn/funds/ggzjl/page/2/ajax/1
# .format page+2个timestamp(间隔1秒左右，+150)
net_money_url = 'http://push2.eastmoney.com/api/qt/clist/get?pn={}&pz=50&po=1&np=1&ut=b2884a393a59ad64002292a3e90d46a5&fltt=2&invt=2&fid0=f4001&fid=f62&fs=m:0+t:6+f:!2,m:0+t:13+f:!2,m:0+t:80+f:!2,m:1+t:2+f:!2,m:1+t:23+f:!2,m:0+t:7+f:!2,m:1+t:3+f:!2&stat=1&fields=f12,f14,f2,f3,f62,f184,f66,f69,f72,f75,f78,f81,f84,f87,f204,f205,f124&rt=53215467&cb=jQuery183017742937962018934_{}&_={}'
# EasyMoney全行情

# Header
common_header = {
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': 'spversion=20130314; __utma=156575163.1163133091.1530233537.1530289428.1530369413.3; __utmz=156575163.1530369413.3.3.utmcsr=stockpage.10jqka.com.cn|utmccn=(referral)|utmcmd=referral|utmcct=/; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1530444468,1530505958,1530506333,1530516152; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1530516152; historystock=300033%7C*%7C1A0001; v=AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp',
            'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp',
            'Host': 'q.10jqka.com.cn',
            'Referer': 'http://q.10jqka.com.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'}

edge_header = {
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'Accept-Encoding': 'gzip, deflate',
            'Cache-Control': 'max-age=0',
            'Accept-Language': 'zh-Hans-CN, zh-Hans;q=0.5',
            'Upgrade-Insecure-Requests': '1',
            'Cookie': 'v=AjWOSuo0htFSyuJtU7qx53iZRL3tsunps2bNGLda8az7jlcnfwL5lEO23fhE; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1596290163; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1596290163; historystock=002613; spversion=20130314',
            'Connection': 'Keep-Alive',
            'If-Modified-Since': 'Sat, 01 Aug 2020 02:34: 19 GMT',
            'Host': 'd.10jqka.com.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.79 Safari/537.36 Edge/14.14393'
        }

# EasyMoney网站Json与需要获取数据的对应dict
index_easyMoney_name = "f12"
fieldnames = ['序号','代码','名称','现价', '最低','最高','开盘','涨跌幅', '涨跌', '涨速', '换手', '量比', '振幅',
              '成交额', '流通股',  '流通市值', '市盈率','所属行业','所属地区','所属概念','主力净流入']
map_easyMoney_dict = {
                "名称":"f14",
            "现价":"f2",
            "最低":"f16",
            "最高":"f15",
            "开盘":"f17",
            "成交额":"f6",
            "换手":"f8",
            "市盈率":"f9",
            "量比":"f10",
            "所属行业":"f100", #sector
            "所属地区":"f102", #region
            "所属概念":"f103", #concept
            "主力净流入":"f62" #netMoney
}

map_eastMoney_netMoney = {
    "主力净流入" : "f62"
}


#  -----------------Other Settings-----------
#代理池接口
PROXY_POOL_API = "http://127.0.0.1:5555/random"

headers_list = [{
                        'Accept': 'text/html, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Connection': 'keep-alive',
                        'Cookie':'log=; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361,1533998469,1533998895,1533998953; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1533998953; user=MDrAz9H9akQ6Ok5vbmU6NTAwOjQ2OTU0MjIzNDo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxLDQwOzIsMSw0MDszLDEsNDA7NSwxLDQwOzgsMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDEsNDA6Ojo6NDU5NTQyMjM0OjE1MzM5OTkwNzU6OjoxNTMzOTk5MDYwOjg2NDAwOjA6MTZmOGFjOTgwMGNhMjFjZjRkMWZlMjk0NDQ4M2FhNDFkOmRlZmF1bHRfMjox; userid=459542234; u_name=%C0%CF%D1%FDjD; escapename=%25u8001%25u5996jD; ticket=7c92fb758f81dfa4399d0983f7ee5e53; v=Ajz6VIblS6HlDX_9PqmhBV0QDdH4NeBfYtn0Ixa9SCcK4daNPkWw77LpxLZl',
                        'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp',
                        'Host': 'q.10jqka.com.cn',
                        'Referer': 'http://q.10jqka.com.cn/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
                        },
                        {
                        'Accept': 'text/html, */*; q=0.01',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh-CN,zh;q=0.8',
                        'Connection': 'keep-alive',
                        'Cookie': 'user=MDq62tH9NUU6Ok5vbmU6NTAwOjQ2OTU0MjA4MDo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxLDQwOzIsMSw0MDszLDEsNDA7NSwxLDQwOzgsMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDEsNDA6Ojo6NDU5NTQyMDgwOjE1MzM5OTg4OTc6OjoxNTMzOTk4ODgwOjg2NDAwOjA6MTEwOTNhMzBkNTAxMWFlOTg0OWM1MzVjODA2NjQyMThmOmRlZmF1bHRfMjox; userid=459542080; u_name=%BA%DA%D1%FD5E; escapename=%25u9ed1%25u59965E; ticket=658289e5730da881ef99b521b65da6af; log=; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361,1533998469,1533998895,1533998953; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1533998953; v=AibgksC3Qd-feBV7t0kbK7PCd5e-B2rBPEueJRDPEskkk8xLeJe60Qzb7jDj',
                        'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp',
                        'Host': 'q.10jqka.com.cn',
                        'Referer': 'http://q.10jqka.com.cn/',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
                        },
                        {'Accept': 'text/html, */*; q=0.01',
                         'Accept-Encoding': 'gzip, deflate, sdch',
                         'Accept-Language': 'zh-CN,zh;q=0.8',
                         'Connection': 'keep-alive',
                         'Cookie': 'user=MDq62sm9wM%2FR%2FVk6Ok5vbmU6NTAwOjQ2OTU0MTY4MTo3LDExMTExMTExMTExLDQwOzQ0LDExLDQwOzYsMSw0MDs1LDEsNDA7MSwxLDQwOzIsMSw0MDszLDEsNDA7NSwxLDQwOzgsMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDEsNDA6Ojo6NDU5NTQxNjgxOjE1MzM5OTg0NjI6OjoxNTMzOTk4NDYwOjg2NDAwOjA6MTAwNjE5YWExNjc2NDQ2MGE3ZGYxYjgxNDZlNzY3ODIwOmRlZmF1bHRfMjox; userid=459541681; u_name=%BA%DA%C9%BD%C0%CF%D1%FDY; escapename=%25u9ed1%25u5c71%25u8001%25u5996Y; ticket=4def626a5a60cc1d998231d7730d2947; log=; Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361,1533998469; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1533998496; v=AvYwAjBHsS9PCEXLZexL20PSRyfuFzpQjFtutWDf4ll0o5zbyKeKYVzrvsAz',
                         'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp',
                         'Host': 'q.10jqka.com.cn',
                         'Referer': 'http://q.10jqka.com.cn/',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
                         'X-Requested-With': 'XMLHttpRequest'
                         },
                        {'Accept': 'text/html, */*; q=0.01',
                         'Accept-Encoding': 'gzip, deflate, sdch',
                         'Accept-Language': 'zh-CN,zh;q=0.8',
                         'Connection': 'keep-alive',
                         'Cookie': 'Hm_lvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361; Hm_lpvt_78c58f01938e4d85eaf619eae71b4ed1=1533992361; user=MDq62sm9SnpsOjpOb25lOjUwMDo0Njk1NDE0MTM6NywxMTExMTExMTExMSw0MDs0NCwxMSw0MDs2LDEsNDA7NSwxLDQwOzEsMSw0MDsyLDEsNDA7MywxLDQwOzUsMSw0MDs4LDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAxLDQwOjo6OjQ1OTU0MTQxMzoxNTMzOTk4MjA5Ojo6MTUzMzk5ODE2MDo4NjQwMDowOjFlYTE2YTBjYTU4MGNmYmJlZWJmZWExODQ3ODRjOTAxNDpkZWZhdWx0XzI6MQ%3D%3D; userid=459541413; u_name=%BA%DA%C9%BDJzl; escapename=%25u9ed1%25u5c71Jzl; ticket=b909a4542156f3781a86b8aaefce3007; v=ApheKMKxdxX9FluRdtjNUdGcac08gfwLXuXQj9KJ5FOGbTKxepHMm671oBoh',
                         'hexin-v': 'AiDRI3i0b1qEZNNemO_FOZlE8SXqKQQBpg9Y4Jox7pbOH8oZQjnUg_YdKIHp',
                         'Host': 'q.10jqka.com.cn',
                         'Referer': 'http://q.10jqka.com.cn/',
                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
                         'X-Requested-With': 'XMLHttpRequest'
                         },

                        ]

#数据库部分
MONGO_URL = ''