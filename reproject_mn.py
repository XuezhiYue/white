#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Author: li xiaoxiang
Create date: 2018/8/23 10:17
Description:
以其中要给为基准
批量对数据进行重采样到一定的行列号
Parameters：
输入数据路径
输出数据分辨率
输出数据路径
"""
import os
import sys
import time

try:
    from osgeo import gdal, gdalconst, osr
except ImportError:
    import gdal, gdalconst, osr
try:
    progress = gdal.TermProgress_nocb
except:
    progress = gdal.TermProgress


def searchfile(inpath, file_extension):
    seach_files = []
    for dir_path, dir_name, files in os.walk(inpath):
        for file in files:
            if file.lower().endswith(file_extension):
                seach_files.append(os.path.normpath(os.path.join(dir_path, file)))
                # seach_files.append(file)
    return seach_files


def main(indir, example_file, outdir):
    files = searchfile(indir, '.tif')
    if files == []:
        files = searchfile(indir, '.dat')
        if files == []:
            sys.exit('there is no data ')
    dataset1 = gdal.Open(example_file)
    im_width1 = dataset1.RasterXSize
    im_height1 = dataset1.RasterYSize
    im_proj1 = dataset1.GetProjection()
    im_Geotransform1 = dataset1.GetGeoTransform()



    for file in files:

        dataset = gdal.Open(file)
        im_width = dataset.RasterXSize
        im_height = dataset.RasterYSize
        im_proj = dataset.GetProjection()
        im_Geotransform = dataset.GetGeoTransform()
        dtype = dataset.GetRasterBand(1).DataType
        im_data = dataset.ReadAsArray(0, 0, im_width, im_height)

        outname=os.path.split(file)[1]
        outfile=os.path.join(outdir,outname)

        # output envi file
        dst = gdal.GetDriverByName('GTiff').Create(outfile, im_width1, im_height1,1, dtype)
        dst.SetGeoTransform(im_Geotransform1)
        dst.SetProjection(im_proj1)

        gdal.ReprojectImage(dataset, dst, im_proj, im_proj, gdalconst.GRA_Bilinear)

        dst=None


if __name__ == '__main__':
    start_time = time.time()
    indir=r"\\192.168.0.234\nydsj\user\LXX\dengfengxiaomai\S2NDVI\可用\TEST"
    example_file=r"\\192.168.0.234\nydsj\user\LXX\dengfengxiaomai\S2NDVI\可用\03_vi\20191027_clip_evi.tif"
    outdir=r"\\192.168.0.234\nydsj\user\LXX\dengfengxiaomai\S2NDVI\可用"
    main(indir, example_file, outdir)
    end_time = time.time()
    print("time: %.2f min." % ((end_time - start_time) / 60))
