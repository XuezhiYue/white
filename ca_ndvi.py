#!/usr/bin/env python3.7
# encoding: utf-8
"""
  @author: Yxz
  @contact: QQ:846924329
  @file: Ca_ndvi.py
  @time: 2019/12/20 20:30
  @desc:
  利用shp图层提取实验小区反射率和植被指数
  """
import numpy
import gdal
import ogr
import osr
import sys
import shapefile
from pandas.core.frame import DataFrame
import os

def search_f(inpath):
    # 输入文件路径
    F_list = []
    for root, dir, fields in os.walk(inpath):
        for field in fields:
            if field.endswith("tif") is True:
                f_fn = os.path.join(inpath, field)
                F_list.append(f_fn)

    return F_list

def Getshp_FID(shp_fn):
    """获取要素FID、实验小区字段名称"""

    file = shapefile.Reader(shp_fn)

    features = file.records()
    features_number = len(file.records())

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

    zonal_min = []
    zonal_max = []
    zonal_average = []
    zonal_var = []
    zonal_std = []

    raster = gdal.Open(raster_paths)
    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    transform = raster.GetGeoTransform()
    band = raster.RasterCount

    xOrigin = transform[0]
    yOrigin = transform[3]
    pixelWidth = transform[1]
    pixelHeight = transform[5]

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
    target_ds = gdal.GetDriverByName("MEM").Create('', xcount, ycount, 1, gdal.GDT_Byte)
    target_ds.SetGeoTransform((xmin, pixelWidth, 0, ymax, 0, pixelHeight,))

    # Create for target raster the same projection as for the value raster
    raster_srs = osr.SpatialReference()
    raster_srs.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(raster_srs.ExportToWkt())

    # Rasterize zone polygon to raster
    gdal.RasterizeLayer(target_ds, [1], lyr, burn_values=[1])

    banddataraster = raster.GetRasterBand(1)
    dataraster = banddataraster.ReadAsArray(xoff, yoff, xcount, ycount).astype(numpy.float)
    bandmask = target_ds.GetRasterBand(1)
    datamask = bandmask.ReadAsArray(0, 0, xcount, ycount).astype(numpy.float)

    # Mask zone of raster
    zoneraster = numpy.ma.masked_array(dataraster, numpy.logical_not(datamask))
    #print(zoneraster)
    # Calculate statistics of zonal raster
    zonal_min.append(numpy.min(zoneraster))
    zonal_max.append(numpy.max(zoneraster))
    zonal_average.append(numpy.mean(zoneraster))
    zonal_var.append(numpy.var(zoneraster))
    zonal_std.append(numpy.std(zoneraster))
    #print(zonal_min, zonal_max, zonal_average, zonal_var, zonal_std)
    return zonal_min, zonal_max, zonal_average, zonal_var, zonal_std

def get_vi_ref(input_zone_polygon, raster_paths, VI_out):

    FID_list, Feature_name_list, features_number = Getshp_FID(input_zone_polygon)

    shp = ogr.Open(input_zone_polygon)
    lyr = shp.GetLayer()

    NDVI_MIN = []
    NDVI_MAX = []
    NDVI_AVERAGE = []
    NDVI_VAR = []
    NDVI_STD = []

    for FID in FID_list:
        feat = lyr.GetFeature(FID)
        zonal_min, zonal_max, zonal_average, zonal_var, zonal_std = zonal_stats(feat, input_zone_polygon, raster_paths)

        NDVI_MIN.append(zonal_min)
        NDVI_MAX.append(zonal_max)
        NDVI_AVERAGE.append(zonal_average)
        NDVI_VAR.append(zonal_var)
        NDVI_STD.append(zonal_std)

    NDVI_MIN = numpy.array(NDVI_MIN)
    NDVI_MAX = numpy.array(NDVI_MAX)
    NDVI_AVERAGE = numpy.array(NDVI_AVERAGE)
    NDVI_VAR = numpy.array(NDVI_VAR)
    NDVI_STD = numpy.array(NDVI_STD)

    VI = numpy.hstack((NDVI_MIN, NDVI_MAX, NDVI_AVERAGE, NDVI_VAR, NDVI_STD))
    Ndvi = DataFrame(VI, columns=["MIN", "MAX", "AVERAGE", 'VAR', "STD"], index=Feature_name_list)
    Ndvi.to_csv(VI_out)
    return

def main(input_zone_polygon, Ref_vi_out, raster_path):

    fn_list = search_f(raster_path)
    Number = len(fn_list)
    for i in range(Number):
        print("共{0}景影像，正在提取第{1}景：{2}".format(Number, i+1, fn_list[i]))
        name = fn_list[i].split("\\")[-1].split("_")[0] + "_vi.csv"
        VI_path = os.path.join(Ref_vi_out, name)

        get_vi_ref(input_zone_polygon, fn_list[i], VI_path)
    print("done")
if __name__ == '__main__':

    input_zone_polygon = r"C:\Users\marshmallow\Desktop\Ca_ndvi\shp\市Z.shp"
    Ref_vi_out = r"C:\Users\marshmallow\Desktop\python\python\python\03_out1"
    raster_path = r"C:\Users\marshmallow\Desktop\Ca_ndvi\ndvi"
    main(input_zone_polygon, Ref_vi_out, raster_path)
