#!/usr/bin/env python3.7
# encoding: utf-8
"""
  @author: Yxz
  @contact: yuexuezhi091@gmail.com /qq846924329
  @file: NDVI.py
  @time: 2020/3/26 16:18
  @desc:
  """
import numpy as np
import gdal
import os

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
            if field.endswith("tif") is True:

                # 输入影像路径
                f_fn = os.path.join(inpath, field)
                F_list.append(f_fn)

                # 输出影像路径
                out_image_path = field.split(".")[0] + "_ndvi" + ".tif"
                out_fn = os.path.join(outpath,out_image_path)
                out_list.append(out_fn)

    # 列表排序（升序）
    F_list.sort()
    out_list.sort()
    return F_list, out_list

def raw2ndvi(inpath, outpath, ndwi_threshold):
    """
    :param inpath: 输入影像文件夹路径
    :param outpath: 输出影像文件夹路径
    :param ndwi_threshold: ndwi阈值
    :return:
    """
    F_list, out_list = search_image(inpath,outpath)

    for i in range(len(F_list)):

        print("开始计算",F_list[i])

        ds = gdal.Open(F_list[i])  # 打开影像
        xsize = ds.RasterXSize     # 获取xsize
        ysize = ds.RasterYSize     # 获取ysize
        geotran = ds.GetGeoTransform()  # 获取仿射矩阵
        proj = ds.GetProjection()   # 获取仿射矩阵

        # 依次获取各波段数据，将其转换为数组
        B_band = ds.GetRasterBand(1)  # 蓝
        b1 = B_band.ReadAsArray()
        # 无效值设置为0
        b1_nan_index = np.isnan(b1)
        b1[b1_nan_index] = 0

        G_band = ds.GetRasterBand(2)   # 绿
        b2 = G_band.ReadAsArray()
        # 无效值设置为0
        b2_nan_index = np.isnan(b2)
        b2[b2_nan_index] = 0

        R_band = ds.GetRasterBand(3)   # 红
        b3 = R_band.ReadAsArray()
        # 无效值设置为0
        b3_nan_index = np.isnan(b3)
        b3[b3_nan_index] = 0

        Nir_band = ds.GetRasterBand(4)  # 近红外
        b4 = Nir_band.ReadAsArray()
        # 无效值设置为0
        b4_nan_index = np.isnan(b4)
        b4[b4_nan_index] = 0

        # 计算水体指数ndwi，ndvi
        ndwi = (b2 - b4) / (b2 + b4)
        ndvi = (b4 - b3) / (b4 + b3)

        # 若有无效值，则将其转换为0
        ndwi_nan_index = np.isnan(ndwi)
        ndwi[ndwi_nan_index] = 0

        # 大于1的设置为1
        ndwi = np.where(ndwi <= 1, ndwi, 1)

        # 小于-1的设置为-1
        ndwi = np.where(ndwi >= -1, ndwi, -1)

        # ndwi写出
        ndwi_max = max(ndwi_threshold)
        ndwi_min = min(ndwi_threshold)
        NDWI_index = np.where(((ndwi <= ndwi_max) & (ndwi >= ndwi_min)))

        # 制作一个腌膜文件
        mask_np = np.ones((ysize, xsize), np.int)
        mask_np[NDWI_index] = 0

        # 裁剪
        NDVI = np.choose(mask_np, (ndvi, np.nan))

        # ndvi输出
        driver =gdal.GetDriverByName("GTiff")
        ndvi_ds = driver.Create(out_list[i], xsize, ysize, 1, gdal.GDT_Float64)
        ndvi_ds.SetProjection(proj)
        ndvi_ds.SetGeoTransform(geotran)
        NDVI_band = ndvi_ds.GetRasterBand(1)
        NDVI_band.WriteArray(NDVI)

    print("done")
if __name__ == '__main__':

    inpath = r"C:\Users\marshmallow\Desktop\ndvi\in"    # 输入路径
    outpath = r"C:\Users\marshmallow\Desktop\ndvi\out"  # 输出路径
    ndwi_threshold = (-1, 0)                            # ndwi阈值
    raw2ndvi(inpath, outpath, ndwi_threshold)
