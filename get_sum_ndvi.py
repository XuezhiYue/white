#!/Users/wxl/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
"""
  @Author  : Yxz
  @contact: 846924329@qq.com
  @Software: PyCharm
  @FileName: get_sum_ndvi.py
  @Time    : 2020/7/6 11:21
  @desc:
"""
import os
import pandas as pd
import numpy as np
from pandas.core.frame import DataFrame

def search_f(inpath):

    F_dic  = {}
    F_name = []

    for root, dir, fields in os.walk(inpath):

        for field in fields:
            if field.endswith("csv") and len(field[1:8]) == 7:
                f_fn = os.path.join(inpath, field)
                f_name = field[1:8]
                F_name.append(f_name)
                F_dic[f_name] = f_fn

    F_name.sort()
    return F_dic, F_name

def main(inpath,out_path):

    F_dic, F_name = search_f(inpath)
    n_line = len(F_name)

    data1 = np.zeros((n_line, 8))  # 最小值.
    data2 = np.zeros((n_line, 8))  # 最大值
    data3 = np.zeros((n_line, 8))  # 均值
    data4 = np.zeros((n_line, 8))  # VAR
    data5 = np.zeros((n_line, 8))  # STD

    for i in range(n_line):

        in_path = F_dic[F_name[i]]
        print("共计{0}个数据，正在计算第{1}个: {2}".format(n_line, i+1, F_name[i]))
        df = pd.read_csv(in_path, header=0, index_col=0, engine='python')
        try:
            dataframe1 = df['MIN'].values
            dataframe1.reshape((1, 8))
            data1[i, :] = dataframe1

            dataframe2 = df['MAX'].values
            dataframe2.reshape((1, 8))
            data2[i, :] = dataframe2

            dataframe3 = df['AVERAGE'].values
            dataframe3.reshape((1, 8))
            data3[i, :] = dataframe3

            dataframe4 = df['VAR'].values
            dataframe4.reshape((1, 8))
            data4[i, :] = dataframe4

            dataframe5 = df['STD'].values
            dataframe5.reshape((1, 8))
            data5[i, :] = dataframe5

        except KeyError:
            print("Error，please check the input file format")

    columns = ["西宁市", "海东市", "海北藏族自治州", "黄南藏族自治州", "海南藏族自治州", "果洛藏族自治州", "玉树藏族自治州", "海西蒙古族藏族自治州"]
    #columns = ["1", "2", "3", "4", "5", "6", "7", "8"]
    min_csv = DataFrame(data1, columns=columns, index=F_name)
    minfield = out_path + "\\" + "value_min.csv"
    min_csv.to_csv(minfield)

    max_csv = DataFrame(data2, columns=columns, index=F_name)
    maxfield = out_path + "\\" + "value_max.csv"
    max_csv.to_csv(maxfield)

    AVERAGE_csv = DataFrame(data3, columns=columns, index=F_name)
    AVERAGEfield = out_path + "\\" + "value_average.csv"
    AVERAGE_csv.to_csv(AVERAGEfield)

    VAR_csv = DataFrame(data4, columns=columns, index=F_name)
    VARfield = out_path + "\\" + "value_var.csv"
    VAR_csv.to_csv(VARfield)

    STD_csv = DataFrame(data5, columns=columns, index=F_name)
    STDfield = out_path + "\\" + "value_std.csv"
    STD_csv.to_csv(STDfield)

    print("done")

if __name__ == '__main__':
    """
    inpath:文件输入路径 路径中csv格式实例：A2016093_vi.csv
    outpah:文件输出路径 输出文件5个为csv,包括min、max、average、var和std 
    """
    inpath = r"C:\Users\marshmallow\Desktop\python\python\python\03_out1"
    outpath = r"C:\Users\marshmallow\Desktop\python\python\python\04_out2"
    main(inpath, outpath)