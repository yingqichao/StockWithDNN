import queries
import settings
import update_dict
import spider
import util

if __name__ =="__main__":
    #获取当日实时数据
    update_dict.update_Shanghai()
    # 更新到batch
    # update_dict.update_daily_data()
