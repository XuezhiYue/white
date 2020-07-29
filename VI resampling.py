#!/usr/bin/env python3.7
# encoding: utf-8
"""
  @author: Yxz
  @contact: yuexuezhi091@gmail.com
  @file: test.py
  @time: 2020/1/14 10:11
  @desc:
  利用scipy库中的interpolate.Rbf函数对提取后的植被指数进行插值
  """
import pandas as pd
import numpy as np
from scipy import interpolate

def vi_insert(VI_path,VI_out,day_step):

    # csv读为dataframe
    VI = pd.read_csv(VI_path, header=0, index_col=0, engine='python')

    # 读取dataframe的表头
    header = VI.columns

    # 待插值指数的列数
    columns_n = len(header)-1

    # dataframe转数组
    meteorology_array = VI.values

    # 年积日
    x = meteorology_array[:, 0]

    # 最大年积日
    x_max = int(np.max(x))

    # 插值后的日期列表
    new_x = []
    for i in range(1, x_max+1, day_step):
        new_x.append(i)

    # 行数
    rows_n = len(new_x)

    # 日期转数组
    new_x = np.array(new_x).reshape(rows_n, 1)

    Y = np.zeros((rows_n, columns_n))
    for i in range(1, columns_n+1):

        yi = meteorology_array[:, i]

        # 利用nterpolate.Rbf函数进行插值处理，其中kind = ['multiquadric','gaussian','linear']，这里用'multiquadric'
        kind = 'multiquadric'
        f = interpolate.Rbf(x, yi, kind=kind)

        # 插值后的yi_new追加至Y
        yi_new = np.array(f(new_x))
        Y[:, i-1] = yi_new[:, 0]

    Y = np.array(Y).reshape(rows_n, columns_n)

    # 数组合并
    df = np.hstack((new_x, Y))
    df = pd.DataFrame(df, columns=header)

    df.to_csv(VI_out)

if __name__ == '__main__':

    VI_path = r"C:\Users\marshmallow\Desktop\小麦成熟度\07_out\vi33.csv"
    VI_out= r"C:\Users\marshmallow\Desktop\小麦成熟度\07_out\vi_inset33.csv"
    day_step = 3
    vi_insert(VI_path,VI_out,day_step)
