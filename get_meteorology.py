#!/Users/wxl/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
"""
  @Author  : Yxz
  @contact: yuexuezhi091@gmail.com
  @Software: PyCharm
  @FileName: get_meteorology.py
  @Time    : 2020/5/18 9:46
  @desc:
"""
import pandas as pd
from pandas.core.frame import DataFrame
import numpy as np

def get_AT(start_time,end_time,t_path,out_path):
    # start_time = "20191027"# 小麦种植时间
    # end_time = "20191226" # 截至时间
    # t_path ="C:\Users\marshmallow\Desktop\小麦成熟度\气象数据1227.csv"
    # out_path = "C:\Users\marshmallow\Desktop\小麦成熟度\气象数据.csv"

    year = int(start_time[0:4])
    month = int(start_time[4:6])
    day = int(start_time[6:8])
    hour = 0

    year1 = int(end_time[0:4])
    month1 = int(end_time[4:6])
    day1 = int(end_time[6:8])
    hour1 = 0

    # 转儒略日
    if month <= 2:
        JD = int(365.25 * (year - 1)) + int(30.6001 * (month + 13)) + day + hour / 24 + 1720981.5
    else:
        JD = int(365.25 * year) + int(30.6001 * (month + 1)) + day + hour / 24 + 1720981.5

    if month1 <= 2:
        JD2 = int(365.25 * (year1 - 1)) + int(30.6001 * (month1 + 13)) + day1 + hour1 / 24 + 1720981.5
    else:
        JD2 = int(365.25 * year1) + int(30.6001 * (month1 + 1)) + day1 + hour1 / 24 + 1720981.5

    # 年积日
    l_day = JD2 - JD+1

    # 读取气象数据
    df = pd.read_csv(t_path,header=0, index_col=0, engine='python')
    data = df.values

    # 读取气象数据获取标准日期
    df2 = pd.read_csv(t_path, header=0, engine='python')
    s_day = df2.loc[:, "采集时间"]
    #print((s_day[0])[0:10])
    Tm_mean= []
    JDay_list = []
    Day_list = []
    GA_sum = []
    WS_mean = []
    RH_mean = []
    for i in range(int(l_day)):
        i = i+1
        # 第i天
        star_day = i-1
        end_day = i

        # 记录年积日
        JDay_list.append(star_day+1)

        # 起始行号
        start_loc = star_day*48
        end_loc = end_day*48

        # 温度所在列号
        tm_loc = 5

        # 挑选温度大于0
        tm_data = data[start_loc:end_loc, tm_loc]
        TM = tm_data[np.where(tm_data > 0)]

        # 计算日温度均值
        tm_mean = np.mean(TM)
        Tm_mean.append(tm_mean)

        # 太阳辐射所在列号
        ga_loc = 8

        # 计算日太阳辐射
        ga_data = data[start_loc:end_loc, ga_loc]
        ga_sum = np.sum(ga_data)
        GA_sum.append(ga_sum)

        # 风速所在列号
        ws_loc = 2

        # 计算日平均风速
        ws_data = data[start_loc:end_loc, ws_loc]
        ws_sum = np.mean(ws_data)
        WS_mean.append(ws_sum)

        # 风速所在列号
        rh_loc = 6

        # 计算日平均湿度
        rh_data = data[start_loc:end_loc, rh_loc]
        rh_sum = np.mean(rh_data)
        RH_mean.append(rh_sum)
        #print(s_day)
        #print(start_loc)
        # 标准日期
        time = (s_day[start_loc])[0:10]
        print(start_loc,time)
        Day_list.append(time)

    Tm_mean = np.array(Tm_mean)
    JDay_list = np.array(JDay_list)
    GA_sum = np.array(GA_sum)
    WS_mean = np.array(WS_mean)
    RH_mean = np.array(RH_mean)

    a = np.vstack((JDay_list,Tm_mean,GA_sum,WS_mean,RH_mean)).transpose()
    out_data = DataFrame(a, columns=["年积日", "日积温", "日太阳辐射", "日平均风速", "日平均湿度"], index=Day_list)

    # 输出为CSV
    out_data.to_csv(out_path)
    print("提取完成")

    return

if __name__ == '__main__':

    start_time = "20191027"  # 小麦种植时间
    end_time = "20200510"    # 截至时间
    t_path =r"C:\Users\marshmallow\Desktop\小麦成熟度\04_气象数据\气象数据0529.csv"
    out_path = r"C:\Users\marshmallow\Desktop\小麦成熟度\04_气象数据\气象数据0529out.csv"
    get_AT(start_time, end_time, t_path, out_path)

# time = "2019/10/9 0:00:30"
# dt = datetime.strptime(time, '%Y/%m/%d %H:%M:%S')
# # fmt = '%Y.%m.%d'
# print(dt)
# #jd = dt.strftime(fmt)
#print(jd)