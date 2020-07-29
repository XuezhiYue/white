#!/usr/bin/env python3.7
# encoding: utf-8
"""
  @author: Yxz
  @contact: yuexuezhi091@gmail.com
  @file: text.py
  @time: 2019/12/20 20:30
  @desc:
  对各时期提取后的植被指数进行合并
  """

from pandas.core.frame import DataFrame
import os
import pandas as pd
import numpy as np

def day2dy(end_time,start_time):
    """将标准日期转为年积日
        start_time 起始日期（如小麦种植日期）
        end_time   终止日期（如某个取样日期）
    """
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

    # 转年积日
    l_day = JD2 - JD+1

    return l_day

def search_f(inpath):

    F_list = []
    D_list = []
    Dy_list = []

    # 小麦播种日期
    start_time = "20191027"

    for root, dir, fields in os.walk(inpath):
        for field in fields:
            # 挑选vi.csv
            if field.endswith(".csv") is True:
                if field.split("_")[1][0:2] == "vi":
                    f_fn = os.path.join(inpath, field)
                    F_list.append(f_fn)
                    # 标准日期
                    day = field.split("_")[0]
                    D_list.append(day)
                    # 年积日
                    end_time = day
                    dy = day2dy(end_time, start_time)
                    Dy_list.append(dy)
    # 按升序排列
    F_list.sort()
    D_list.sort()
    Dy_list.sort()

    return F_list, D_list, Dy_list

def main(inpath, poin_number, outpath):

    F_list, D_list, Dy_list = search_f(inpath)

    N = int(len(D_list))

    point = poin_number

    VI = np.zeros((N, point))

    for i in range(N):

        df = pd.read_csv(F_list[i], header=0, index_col=0, engine='python')
        header = df.columns.tolist()
        header.insert(0, "年积日")

        data = df.values

        # 第一行NDVI
        ndvi = data[0, :]
        VI[i, :] = ndvi

    # 日期转数组
    Dy_list = np.array(Dy_list).reshape(N, 1)
    outcsv = np.hstack((Dy_list, VI))

    # 输出
    VI_csv = DataFrame(outcsv, index=D_list, columns = header)
    VI_csv.to_csv(outpath)
    print("done")
    return

if __name__ == '__main__':

    # 提取后的VI路径
    inpath = r"C:\Users\marshmallow\Desktop\小麦成熟度\06_vi_ref - 副本"
    # 汇总后VI输出路径
    outpath = r"C:\Users\marshmallow\Desktop\小麦成熟度\07_out - 副本\vi_stack.csv"
    # 矢量个数
    poin_number = 20

    main(inpath, poin_number, outpath)