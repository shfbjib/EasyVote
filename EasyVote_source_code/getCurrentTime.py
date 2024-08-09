from datetime import datetime,timedelta
from  encryption_decryption import *
def curr_time():
    '''
    此函数可以实现获取当前时间的所有信息的功能
    :return: 包含当前时间全部信息的时间对象
    '''
    current_datetime = datetime.now()  # 获取当前日期和时间
    current_date = current_datetime.date()  # 提取当前日期
    current_time = current_datetime.time()  # 提取当前时间
    # 整合成一个特殊的时间对象time
    Time = datetime(current_date.year, current_date.month, current_date.day, current_time.hour, current_time.minute,
                    current_time.second)
    return Time
