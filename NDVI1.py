#!/Users/wxl/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
"""
  @Author  : Yxz
  @contact: yuexuezhi091@gmail.com
  @Software: PyCharm
  @FileName: NDVI1.py
  @Time    : 2020/6/17 22:48
  @desc:
"""

try:
    from osgeo import gdal
except ImportWarning:
    import gdal
import os
import numpy as np

def search_image(inpath, outpath):
    """
    :param inpath: 输入影像路径
    :param outpath: 输出影像路径
    :return: 输入影像、输出影像的绝对路径
    """
    F_list = []  # 输入影像路径列表
    out_list = []  # 输出影像路径列表

    # 遍历文件
    for root, dir, fields in os.walk(inpath):

        # 遍历寻找找tif结尾的文件
        for field in fields:
            if field.endswith("h5") is True:
                # 输入影像路径
                f_fn = os.path.join(inpath, field)
                F_list.append(f_fn)

                # 输出影像路径
                out_image_path = field[:-2] + "_ndvi" + ".tif"
                out_fn = os.path.join(outpath, out_image_path)
                out_list.append(out_fn)

    # 列表排序（升序）
    F_list.sort()
    out_list.sort()
    return F_list, out_list


def Ca_ndvi(inpath, outpath):
    '''
    :param inpath: 输入影像路径
    :param outpath: 输出影像路径
    '''
    print("---获取影像输入、输出路径---")
    F_list, out_list = search_image(inpath, outpath)

    for i in range(len(F_list)):
        print("共{0}景正在处理第{1}景→→→".format(len(F_list), i+1), F_list[i])
        ds = gdal.Open(F_list[i])

        subdatasets = ds.GetSubDatasets()

        red_DS = gdal.Open(subdatasets[6][0])

        red = red_DS.ReadAsArray()
        nir_DS = gdal.Open(subdatasets[7][0])
        nir = nir_DS.ReadAsArray()

        xsize = red_DS.RasterXSize
        ysize = red_DS.RasterYSize
        proj = red_DS.GetProjection()
        tran = red_DS.GetGeoTransform()

        ndvi = (nir - red) / (nir + red)

        # 若有无效值，则将其转换为0
        nan_index = np.isnan(ndvi)
        ndvi[nan_index] = 0
        ndvi = ndvi.astype(np.float)
        # 大于1的设置为1
        ndvi = np.where(ndvi <= 1 , ndvi ,1)
        # 小于-1的设置为-1
        ndvi = np.where(ndvi >= -1, ndvi, -1)
        # # -0.000000改为-9999
        # NDVI = np.where(NDVI == -0.0, -9999, NDVI)

        driver = gdal.GetDriverByName('GTiff')
        out_dataset = driver.Create(out_list[i], xsize, ysize, 1, gdal.GDT_Float32)
        out_dataset.SetGeoTransform(tran)
        out_dataset.SetProjection(proj)
        out_dataset.GetRasterBand(1).WriteArray(ndvi)

    print("---done---")

    return

if __name__ == '__main__':

    inpath = r"C:\Users\marshmallow\Desktop\H5_NDVI_Cal\H5_NDVI_Cal"
    outpath =r"C:\Users\marshmallow\Desktop\H5_NDVI_Cal\out"

    Ca_ndvi(inpath, outpath)