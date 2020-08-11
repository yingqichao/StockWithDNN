import progressbar
import time
# 先定义一个进度条
# http://blog.useasp.net/
# pbar = progressbar.ProgressBar(maxval=100, \
# widgets=[progressbar.Bar('=', '[', ']'), ' ', \
# progressbar.Percentage()])
# pbar.start()
# for i in range(100):
# # 更新进度条
#     time.sleep(1)
#     pbar.update(i+1)
#
# pbar.finish()

str="http://47.push2.eastmoney.com/api/qt/clist/get?cb=jQuery112401597019051519455_1596423136116&pn=1&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:13,m:0+t:80,m:1+t:2,m:1+t:23&fields={}&1596520581125"

len = ""
for i in range(1,153):
    len+="f{},".format(i)
print(str.format(len[:-1]))

