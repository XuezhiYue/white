#！/usr/bin/env python3
# -*- coding:utf -8 -*-
"""
多进程处理 S2
time：2020/4/2
author：LXX
注意文件名字和解压后的文件名一样，缺少。SAFE
调用Sen2Cor 多进程处理S2，结果包括10m和20m的结果
input：下载的原始数据文件所放的文件夹路径（包括哨兵2官网下载的数据格式和usgs下载的数据格式）
output：输出文件路径
"""
import zipfile
import os
import multiprocessing as mp
import subprocess
try:
    import gdal
except ImportError:
    from osgeo import gdal
import shutil
try:
    process=gdal.TermProgress
except:
    process=gdal.TermProgress_nocb
import time

def search_file(folder_path, file_extension):
    """检索文件"""
    search_files = []
    for dir_path, dir_names, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(file_extension):
                search_files.append(os.path.normpath(os.path.join(dir_path, file)))

    return search_files




def get_10tif(filelist):
    #  对10m的数据进行排序，后续波段叠加使用
    jp2s =  ['B02', 'B03', 'B04', 'B08']
    outfilelist = []
    for jp2 in jp2s:
        for file in filelist:
            filename = os.path.basename(file)
            if jp2 in filename:
                outfilelist.append(file)
    file_first = outfilelist[0][:-11]

    return outfilelist, file_first




def JP2totif(L2A10dirs,outdir):
    fold_10mdir = search_file(L2A10dirs, ".jp2")
    file10dir, firstname10 = get_10tif(fold_10mdir)
    filevrt_10m = os.path.join(outdir, firstname10 + ".vrt")
    gdal.BuildVRT(filevrt_10m, file10dir, separate=True)
    # 查询清楚VRT
    filename=os.path.split(firstname10)[1]
    driver = gdal.GetDriverByName("GTiff")
    file_10m = os.path.join(outdir, filename + "_layer.tif")
    outds10 = driver.CreateCopy(file_10m, gdal.Open(filevrt_10m))
    outds10 = None
if __name__=="__main__":
    starttime=time.time()
    L2A10dirs=r"\\192.168.0.234\nydsj\user\LXX\chongqing\1\1out\S2A_MSIL1C_20191210T033131_N0208_R018_T48RYU_20191210T062339.SAFE\GRANULE\L1C_T48RYU_A023324_20191210T033505\IMG_DATA"
    outdir=r"\\192.168.0.234\nydsj\user\LXX\chongqing\1\2"
    JP2totif(L2A10dirs,outdir)
    endtime=time.time()
    print("the total time is %s minute"%((endtime-starttime)/60))