#!/usr/bin/env python3.7
# encoding: utf-8
"""
  @author: Yxz
  @contact: yuexuezhi091@gmail.com
  @file: get_ref_vi.py
  @time: 2019/12/20 20:30
  @desc:
  利用shp图层批量提取各生育时期实验小区反射率和植被指数
  """
import numpy as np
from numpy import sqrt, log
import gdal
import ogr
import osr
import sys
import shapefile
from pandas.core.frame import DataFrame

def Getshp_FID(shp_fn):
    """获取要素FID、实验小区字段名称"""

    # 打开矢量
    try:
        file = shapefile.Reader(shp_fn)
    except shapefile.ShapefileException:
        print("路径:{0} 不存在shp文件".format(shp_fn))
        sys.exit()

    # 获取要素属性、要素数量
    features = file.records()
    features_number = len(file.records())

    # 获取要素FID、实验小区名称列表
    FID_list = []
    Feature_name_list = []

    for i in range(features_number):
        feature = str(features[i])
        # 从Feature中获取FID
        feature_id = int(feature.split("#")[1].split(":")[0])
        FID_list.append(feature_id)
        # 从Feature中获取FID对应的数字
        feature_name = eval(str(features[i]).split(":")[1].split("[")[1].split("]")[0])
        Feature_name_list.append(feature_name)

    return FID_list, Feature_name_list, features_number

def zonal_stats(feat, input_zone_polygon, raster_paths):
    """统计shp图中要素反射率"""

    # 创建空列表，用于存储计算后的反射率值
    zonal_average = []

    # 打开影像
    raster = gdal.Open(raster_paths)

    # 打开图层
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    # Get raster georeference info
    transform = raster.GetGeoTransform()
    band = raster.RasterCount

    if band != 5:
        print("非5波段影像，代码不可用")
        sys.exit()

    # 左上角坐标；影像分辨率
    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

    """
    矢量重投影为与栅格相同的投影
    CoordinateTransformation 坐标转换
    """
    sourceSR = lyr.GetSpatialRef()
    targetSR = osr.SpatialReference()
    targetSR.ImportFromWkt(raster.GetProjectionRef())
    coordTrans = osr.CoordinateTransformation(sourceSR, targetSR)
    # feat = lyr.GetNextFeature()
    geom = feat.GetGeometryRef()
    geom.Transform(coordTrans)

    # Get extent of feat
    geom = feat.GetGeometryRef()
    if (geom.GetGeometryName() == "MULTIPOLYGON"):
        count = 0
        pointsX = []
        pointsY = []
        for polygon in geom:
            geomInner = geom.GetGeometryRef(count)
            ring = geomInner.GetGeometryRef(0)
            numpoints = ring.GetPointCount()
            for p in range(numpoints):
                lon, lat, z = ring.GetPoint(p)
                pointsX.append(lon)
                pointsY.append(lat)
            count += 1
    elif (geom.GetGeometryName() == 'POLYGON'):
        ring = geom.GetGeometryRef(0)
        numpoints = ring.GetPointCount()
        pointsX = []
        pointsY = []
        for p in range(numpoints):
            lon, lat, z = ring.GetPoint(p)
            pointsX.append(lon)
            pointsY.append(lat)

    else:
        sys.exit("ERROR: Geometry needs to be either Polygon or Multipolygon")

    xmin = min(pointsX)
    xmax = max(pointsX)
    ymin = min(pointsY)
    ymax = max(pointsY)

    # Specify offset and rows and columns to read
    xoff = int((xmin - xOrigin) / pixelWidth)
    yoff = int((yOrigin - ymax) / pixelWidth)

    xcount = int((xmax - xmin) / pixelWidth) + 1
    ycount = int((ymax - ymin) / pixelWidth) + 1

    # Create memory target raster
    target_ds = gdal.GetDriverByName("MEM").Create('', xcount, ycount, 5, gdal.GDT_Byte)
    target_ds.SetGeoTransform((xmin, pixelWidth, 0, ymax, 0, pixelHeight,))

    # Create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())

    # Rasterize zone polygon to raster
    raster_bandlist = list(range(band, 0, -1))
    b_v = [1]*band
    gdal.RasterizeLayer(target_ds, raster_bandlist, lyr, burn_values=b_v)

    for i in range(band):
        banddataraster = raster.GetRasterBand(i + 1)
        dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(np.float)
        bandmask = target_ds.GetRasterBand(i + 1)
        datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(np.float)

        # Mask zone of raster
        zoneraster = np.ma.masked_array(dataraster, np.logical_not(datamask))

        # Calculate statistics of zonal raster
        zonal_average.append(np.average(zoneraster))
        #zonal_average.append(np.var(zoneraster))

    return zonal_average


def get_vi_ref(input_zone_polygon, raster_paths, Ref_out, VI_out):

    """统计矢量范围均值"""

    # 第一步：获取要素FID和对应小区名的列表
    FID_list, Feature_name_list, features_number = Getshp_FID(input_zone_polygon)
    FID_number = len(FID_list)

    # 打开图层
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    # 第二步：依次获取反射率Ref、NDIV和OSAVI
    Ref = []
    VI_array = np.zeros((FID_number, 65))
    print("正在提取", raster_paths)

    for i in range(FID_number):
        FID = FID_list[i]
        feat = lyr.GetFeature(FID)
        Ref_meanValue = zonal_stats(feat, input_zone_polygon, raster_paths)

        # 获取各波段反射率值
        b0 = Ref_meanValue[0]  # blue
        b1 = Ref_meanValue[1]  # green
        b2 = Ref_meanValue[2]  # red
        b3 = Ref_meanValue[3]  # red_eage
        b4 = Ref_meanValue[4]  # nir

        #GRVI = float(b4) / b1
        VI_array[i, 0] = float(b4) / b1

        # GDVI
        GDVI = b4 - b1

        # GNDVI
        GNDVI = (float(b4) - b1) / (b4 + b1)
        VI_array[i, 1] = GNDVI

        # GWDRVI
        VI_array[i, 2] = (0.12 * b4 - b1) / (0.12 * b4 + b1)

        # CIg
        VI_array[i, 3] = float(b4) / b1 - 1

        # MSR_G
        VI_array[i, 4] = (float(b4) / b1 - 1) / sqrt((float(b4) / b1 + 1))

        # GSAVI
        VI_array[i, 5] = 1.5 * ((b4 - b1) / (b4 + b1 + 0.5))

        # MGSAVI
        VI_array[i, 6] = 0.5 * (2.0 * b4 + 1 - sqrt((2 * b4 + 1) ** 2 - 8.0 * (b4 - b1)))

        # GOSAVI
        GOSAVI = 1.16 * (b4 - b1) / (b4 + b1 + 0.16)
        VI_array[i, 7] = GOSAVI

        # GRDVI
        VI_array[i, 8] = (b4 - b1) / sqrt(float(b4) + b1)

        # NDVI
        VI_array[i, 9] = (float(b4) - b2) / (b4 + b2)

        # RVI
        VI_array[i, 10] = float(b4) / b2

        # OSAVI
        VI_array[i, 11] = 1.16 * (b4 - b2) / (b4 + b2 + 0.16)

        # WDRVI
        VI_array[i, 12] = (0.12 * b4 - b2) / (0.12 * b4 + b2)

        # SAVI
        VI_array[i, 13] = 1.5 * (float(b4) - b2) / (b4 + b2 + 0.5)

        # MSAVI
        VI_array[i, 14] = 0.5 * (2.0 * b4 + 1 - sqrt((2.0 * b4 + 1) ** 2 - 8.0 * (b4 - b2)))

        # DVI
        VI_array[i, 15] = b4 - b2

        # RDVI
        VI_array[i, 16] = (b4 - b2) / sqrt(float(b4 + b2))

        # TNDVI
        VI_array[i, 17] = sqrt((float(b4) - b2) / (b4 + b2) + 0.5)

        # MSR
        VI_array[i, 18] = (float(b4) / b2 - 1) / sqrt(float(b4) / b2 + 1)

        # VIopt
        VI_array[i, 19] = 1.45 * (b4 ** 2 + 1.0) / (b2 + 0.45)

        # MERIS
        VI_array[i, 20] = (b2 + b4) / 2.0

        # RERVI
        VI_array[i, 21] = float(b4) / b3

        # REDVI
        VI_array[i, 22] = float(b4) - b3

        # NDRE
        NDRE  = (float(b4) - b3) / (b4 + b3)
        VI_array[i, 23] = NDRE

        # RERDVI
        VI_array[i, 24] = (float(b4) - b3) / sqrt(float(b4) + b3)

        # REWDRVI
        VI_array[i, 25] = (0.12 * b4 - b3) / (0.12 * b4 + b3)

        # VIopt1
        VI_array[i, 26] = 100 * (log(b4) - log(b3))

        # CIre
        VI_array[i, 27] = float(b4) / b3 - 1

        # MSR_RE
        VI_array[i, 28] = (float(b4) / b3 - 1) / sqrt(float(b4) / b3 + 1)

        # RESAVI
        VI_array[i, 29] = 1.5 * ((b4 - b3) / (float(b4) + b3 + 0.5))

        # MRESAVI
        VI_array[i, 30] = 0.5 * (2 * b4 + 1 - sqrt((2 * b4 + 1) ** 2 - 8 * (b4 - b3)))

        # REOSAVI
        REOSAVI = 1.16 * (float(b4) - b3) / (b4 + b3 + 0.16)
        VI_array[i, 31] = REOSAVI

        # NDRE/REOSAVI
        VI_array[i, 32] = NDRE / REOSAVI

        # SR
        VI_array[i, 33] = float(b3) / b2

        # RDVI1
        VI_array[i, 34] = b3 - b2

        # RENDVI
        VI_array[i, 35] = (float(b3) - b2) / (b3 + b2)

        # REGRVI
        VI_array[i, 36] = float(b3) / b1

        # REGDVI
        VI_array[i, 37] = b3 - b1

        # REGNDVI
        VI_array[i, 38] = (float(b3) - b1) / (b3 + b1)

        # MTCI
        VI_array[i, 39] = (float(b4) - b3) / (b3 - b2)

        # DATT
        VI_array[i, 40] = (float(b4) - b3) / (b4 - b2)

        # NGI
        VI_array[i, 41] = float(b1) / (b4 + b3 + b1)

        # NREI
        VI_array[i, 42] = float(b3) / (b4 + b3 + b1)

        # NRI
        VI_array[i, 43] = float(b2) / (b4 + b3 + b2)

        # NNIR
        VI_array[i, 44] = float(b4) / (b4 + b3 + b1)

        # MDD
        VI_array[i, 45] = b4 - 2 * b3 + b1

        # MNDI
        VI_array[i, 46] = (float(b4) - b3) / (b4 - b1)

        # MEVI
        VI_array[i, 47] = 2.5 * (b4 - b3) / (b4 + 6 * b3 - 7.5 * b1 + 1)

        # MNDRE
        VI_array[i, 48] = (b4 - (b3 - 2.0 * b1)) / (b4 + (b3 - 2 * b1))

        # MCARI1
        MCARI1 = ((b4 - b3) - 0.2 * (b4 - b1)) * (float(b4) / b3)
        VI_array[i, 49] = MCARI1

        # MCARI2
        MCARI2 = 1.5 * (2.5 * (float(b4) - b3) - 1.3 * (b4 - b1)) / sqrt(
            (2 * b4 + 1) ** 2 - (6 * b4 - 5 * sqrt(b3)) - 0.5)
        VI_array[i, 50] = MCARI2

        # MCARI1/REOSAVI
        VI_array[i, 51] = MCARI1 / REOSAVI

        # MCARI2/REOSAVI
        VI_array[i, 52] = MCARI2 / REOSAVI

        # MTCARI
        MTCARI = 3 * ((b4 - b3) - 0.2 * (b4 - b1) * (float(b4) / b3))
        VI_array[i, 53] = MTCARI

        # MTCARI/REOSAVI
        VI_array[i, 54] = MTCARI / REOSAVI

        # RETVI
        VI_array[i, 55] = 0.5 * (120 * (b4 - b1) - 200 * (b3 - b1))

        # MRETVI
        MRETVI = 1.2 * (1.2 * (b4 - b1) - 2.5 * (b3 - b1))
        VI_array[i, 56]= MRETVI

        # NDRE/GOSAVI
        VI_array[i, 57] = NDRE / GOSAVI

        # MCCCI
        VI_array[i, 58] = NDRE / GNDVI

        # MTCARI/MRETVI
        VI_array[i, 59] = MTCARI / MRETVI

        # MTCARI/GOSAVI
        VI_array[i, 60] = MTCARI / GOSAVI

        # MCARI2/GOSAVI
        VI_array[i, 61] = MCARI2 / GOSAVI

        # MCARI1/MRETVI
        VI_array[i, 62] = MCARI1 / MRETVI

        # MCARI1/GOSAVI
        VI_array[i, 63] = MCARI1 / GOSAVI

        #GRVI
        VI_array[i, 64] = float(b4)/b1

        Ref.append(Ref_meanValue)

    VI_list = ['GRVI', 'GDVI', 'GNDVI', 'GWDRVI', 'CIg', 'MSR_G', 'GSAVI', 'MGSAVI', 'GOSAVI', 'GRDVI', 'NDVI', 'RVI',
               'OSAVI', 'WDRVI', 'SAVI', 'MSAVI', 'DVI', 'RDVI', 'TNDVI', 'MSR', 'VIopt', 'MERIS', 'RERVI', 'REDVI',
               'NDRE', 'RERDVI', 'REWDRVI', 'VIopt1', 'CIre', 'MSR_RE', 'RESAVI', 'MRESAVI', 'REOSAVI', 'NDRE_REOSAVI',
               'SR', 'RDVI1', 'RENDVI', 'REGRVI', 'REGDVI', 'REGNDVI', 'MTCI', 'DATT', 'NGI', 'NREI', 'NRI', 'NNIR',
               'MDD', 'MNDI', 'MEVI', 'MNDRE', 'MCARI1', 'MCARI2', 'MCARI1_REOSAVI', 'MCARI2_REOSAVI', 'MTCARI',
               'MTCARI_REOSAVI', 'RETVI', 'MRETVI', 'NDRE_GOSAVI', 'MCCCI', 'MTCARI_MRETVI', 'MTCARI_GOSAVI',
               'MCARI2_GOSAVI', 'MCARI1_MRETVI', 'MCARI1_GOSAVI']

    if np.max(Ref) >= 255:
        print("警告：波段反射率数据异常，请将影像转换为反射率后重新提取")

    # 第三步：Ref VI 输出dataframe
    VI = DataFrame(VI_array, columns=VI_list, index=Feature_name_list)
    Ref = DataFrame(Ref, columns=['blue', 'green', 'red', "red_edge", 'nir'], index=Feature_name_list)

    # Ref VI 输出为CSV
    Ref.to_csv(Ref_out)
    VI.to_csv(VI_out)

    print("{0}：提取完成".format(raster_paths))

    return

if __name__ == '__main__':

    # 待提取影像的文件夹路径
    raster_path = sys.argv[1]
    # 待提取shp绝对路径
    input_zone_polygon = sys.argv[2]
    # 反射率、植被指数输出位置
    Ref_out = sys.argv[3]
    VI_out = sys.argv[4]
    get_vi_ref(input_zone_polygon, raster_path, Ref_out, VI_out)

