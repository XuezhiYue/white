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

def main(in_path, out_path, star,end):

    # 读取气象数据
    df = pd.read_csv(in_path, header=0, index_col=0, engine='python')

    data = np.zeros((len(citys), 2))

    for i in range(len(citys)):

        pst = int(100 * (i + 1) / len(citys))
        print('\r{0}{1}{2}%'.format(("计算中".split("\\")[-1]), '▉' * int(pst / 10), (pst)), end='')

        dataframe = df[(df['站名'] == citys[i]) & (df['year'] >= star) & (df['year'] <= end)]

        # 秋季
        autumn = df[(df['站名'] == citys[i]) & (df['year'] >= star) & (df['year'] <= end) & (df['mouth'] < 10) & (df['mouth']  >=6)]

        # 春季
        dataframe = dataframe.append(autumn)
        spring = dataframe.drop_duplicates(keep=False)

        autumn = (autumn.values)[:, -1]
        spring = (spring.values)[:, -1]

        autumn_mean = (np.sum(autumn[np.where(autumn > 0)]))/(end-star+1)
        spring_mean = (np.sum(spring[np.where(spring > 0)]))/(end-star+1)

        data[i, 0] = autumn_mean
        data[i, 1] = spring_mean

    meteorology = DataFrame(data, columns=["autumn","spring"], index=citys)

    meteorology.to_csv(out_path)

if __name__ == '__main__':

    citys = ["安阳", "新乡", "三门峡", "卢氏", "孟津", "栾川", "郑州", "嵩山", "许昌", "开封", "西峡", "南阳", "宝丰", "西华", "桐柏", "驻马店", "信阳",
             "商丘", "永城", "固始"]

    star = 1990
    end = 2019

    in_path =r"C:\Users\marshmallow\Desktop\小麦成熟度\04_气象数据\PRE-13011.csv"
    out_path = r"C:\Users\marshmallow\Desktop\小麦成熟度\04_气象数据\PRE-13011-out.csv"

    main(in_path, out_path, star, end)