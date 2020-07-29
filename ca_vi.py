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

def search_f(inpath,outpath):

    # 输入文件路径，输出文件路径
    F_list = []
    ndvi_out_list = []
    osavi_out_list = []
    rvi_out_list = []
    evi_out_list = []
    ndwi_out_list = []

    for root,dir,fields in os.walk(inpath):
        for field in fields:
            if field.endswith("tif") is True:
                # 获取10m分辨率的影响
                # if field[-7:-4] == '10m':
                #     # 输入影像路径
                #     f_fn = os.path.join(inpath,field)
                #     F_list.append(f_fn)
                #     # 输出影像路径
                #     out_image_path = field.split(".")[0] + "_ndvi" + ".tif"
                #     out_fn = os.path.join(outpath,out_image_path)
                #     out_list.append(out_fn)
                # else :
                #     pass
                f_fn = os.path.join(inpath, field)
                F_list.append(f_fn)

                # NDVI输出影像路径
                out_image_path = field.split(".")[0] + "_ndvi" + ".tif"
                out_fn = os.path.join(outpath,out_image_path)
                ndvi_out_list.append(out_fn)

                # OSAVI输出影像路径
                out_image_path1 = field.split(".")[0] + "_osavi" + ".tif"
                out_fn1 = os.path.join(outpath,out_image_path1)
                osavi_out_list.append(out_fn1)

                # RVI输出影像路径
                out_image_path2 = field.split(".")[0] + "_rvi" + ".tif"
                out_fn2 = os.path.join(outpath,out_image_path2)
                rvi_out_list.append(out_fn2)

                # EVI输出影像路径
                out_image_path3 = field.split(".")[0] + "_evi" + ".tif"
                out_fn3 = os.path.join(outpath,out_image_path3)
                evi_out_list.append(out_fn3)

                # ndwi输出影像路径
                out_image_path4 = field.split(".")[0] + "_ndwi" + ".tif"
                out_fn4 = os.path.join(outpath,out_image_path4)
                ndwi_out_list.append(out_fn4)


    return F_list, ndvi_out_list, osavi_out_list, rvi_out_list, evi_out_list, ndwi_out_list

def main(inpath,outpath):

    F_list, ndvi_out_list, osavi_out_list, rvi_out_list, evi_out_list, ndwi_out_list = search_f(inpath, outpath)

    # 算一下数量
    print("共",len(F_list) ,"组影像需要计算")

    for i in range(len(F_list)):
        print("开始计算第：", i+1, "组影像")

        ds = gdal.Open(F_list[i])
        if ds is None:
            print('Could not open the file ')
        else:
            # 大小、仿射矩阵、投影
            xsize = ds.RasterXSize
            ysize = ds.RasterYSize
            geotran = ds.GetGeoTransform()
            proj = ds.GetProjection()

        # 获取波段，转为反射率
        B_band = ds.GetRasterBand(1)
        b = B_band.ReadAsArray() * 0.0001 # blue
        G_Band = ds.GetRasterBand(2)
        g = G_Band.ReadAsArray() * 0.0001 # green
        R_band = ds.GetRasterBand(3)
        red = R_band.ReadAsArray() * 0.0001 # red
        Nir_Band = ds.GetRasterBand(4)
        nir = Nir_Band.ReadAsArray() * 0.0001 # nir

        # 计算植被指数
        try:
            NDVI = ((nir - red)/(nir + red)).astype(np.float)
            OSAVI = 1.16 * (nir - g) / (nir + g + 0.16)
            RVI = nir / red
            EVI = 2.5 * (nir - red) / (nir + 6.0 * red - 7.5 * b + 1)
            NDWI = (g - nir) / (g + nir)

        except RuntimeWarning:
            print(F_list[i], "数据异常")

        # 若有无效值，则将其转换为0
        nan_index = np.isnan(NDVI)
        NDVI[nan_index] = 0
        # 转为浮点型
        NDVI = NDVI.astype(np.float)
        # 大于1的设置为1
        NDVI = np.where(NDVI <= 1 , NDVI ,1)
        # 小于-1的设置为-1
        NDVI = np.where(NDVI >= -1, NDVI, -1)
        # # -0.000000改为-9999
        # NDVI = np.where(NDVI == -0.0, -9999, NDVI)

        # 驱动
        driver =gdal.GetDriverByName("GTiff")

        # ndvi写出
        outimage_ndvi =  ndvi_out_list[i]
        out_NDVI = driver.Create(outimage_ndvi, xsize, ysize,1, gdal.GDT_Float32)
        out_NDVI.SetProjection(proj)
        out_NDVI.SetGeoTransform(geotran)
        out_NDVI_band = out_NDVI.GetRasterBand(1)
        out_NDVI_band.WriteArray(NDVI)

        # osavi写出
        outimage_osavi =  osavi_out_list[i]
        out_NDVI = driver.Create(outimage_osavi,xsize,ysize,1, gdal.GDT_Float32)
        out_NDVI.SetProjection(proj)
        out_NDVI.SetGeoTransform(geotran)
        out_NDVI_band = out_NDVI.GetRasterBand(1)
        out_NDVI_band.WriteArray(OSAVI)

        # rvi写出
        outimage_rvi = rvi_out_list[i]
        out_NDVI = driver.Create(outimage_rvi, xsize, ysize, 1, gdal.GDT_Float32)
        out_NDVI.SetProjection(proj)
        out_NDVI.SetGeoTransform(geotran)
        out_NDVI_band = out_NDVI.GetRasterBand(1)
        out_NDVI_band.WriteArray(RVI)

        # evi写出
        outimage_evi = evi_out_list[i]
        out_NDVI = driver.Create(outimage_evi, xsize, ysize, 1, gdal.GDT_Float32)
        out_NDVI.SetProjection(proj)
        out_NDVI.SetGeoTransform(geotran)
        out_NDVI_band = out_NDVI.GetRasterBand(1)
        out_NDVI_band.WriteArray(EVI)

        # NDWI写出
        outimage_ndwi = ndwi_out_list[i]
        out_NDVI = driver.Create(outimage_ndwi, xsize, ysize, 1, gdal.GDT_Float32)
        out_NDVI.SetProjection(proj)
        out_NDVI.SetGeoTransform(geotran)
        out_NDVI_band = out_NDVI.GetRasterBand(1)
        out_NDVI_band.WriteArray(NDWI)

    print("VI计算完成")

if __name__ == '__main__':

    inpath = r"\\192.168.0.234\nydsj\user\LXX\dengfengxiaomai\S2NDVI\可用\02_clip"
    outpath = r"\\192.168.0.234\nydsj\user\LXX\dengfengxiaomai\S2NDVI\可用\03_vi"
    main(inpath, outpath)

