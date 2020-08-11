import util
import settings
import update_dict

def get_daily_zhangting():
    util.common_downloader(settings.zhangting_url)

if __name__ == '__main__':
    update_dict.update_Shanghai()
