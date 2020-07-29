#!/Users/wxl/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
"""
  @Author  : Yxz
  @contact: yuexuezhi091@gmail.com
  @Software: PyCharm
  @FileName: lyt.py
  @Time    : 2020/5/20 14:31
  @desc:
  批量波段合并
"""
import os
try:
    from osgeo import gdal, gdalconst, osr
except ImportError:
    import gdal,  gdalconst, osr

def search_f(inpath,outpath):

    ndvi_out_list = []
    osavi_out_list = []
    rvi_out_list = []
    evi_out_list = []
    ndwi_out_list = []

    for root, dirs, fields in os.walk(inpath):
        for field in fields:
            if field.endswith("tif") is True:
                if field.split("_")[-1].split(".")[0]== 'ndvi':
                    # 输入影像路径
                    ndvi_fn = os.path.join(inpath,field)
                    ndvi_out_list.append(ndvi_fn)
                    # 输出影像路径
                    out_ndvi_path = field.split(".")[0] + "_lyt" + ".tif"
                    out_ndvi_fn = os.path.join(outpath,out_ndvi_path)
                    ndvi_out_list.append(out_ndvi_fn)
                elif field.split("_")[-1].split(".")[0] == 'osavi':
                    # 输入影像路径
                    osavi_fn = os.path.join(inpath, field)
                    osavi_out_list.append(osavi_fn)
                    # 输出影像路径
                    out_osavi_path = field.split(".")[0] + "_lyt" + ".tif"
                    out_osavi_fn = os.path.join(outpath, out_osavi_path)
                    osavi_out_list.append(out_osavi_fn)
                elif field.split("_")[-1].split(".")[0] == 'rvi':
                    # 输入影像路径
                    rvi_fn = os.path.join(inpath, field)
                    rvi_out_list.append(rvi_fn)
                    # 输出影像路径
                    out_rvi_path = field.split(".")[0] + "_lyt" + ".tif"
                    out_rvi_fn = os.path.join(outpath, out_rvi_path)
                    rvi_out_list.append(out_rvi_fn)
                elif field.split("_")[-1].split(".")[0] == 'evi':
                    # 输入影像路径
                    evi_fn = os.path.join(inpath, field)
                    evi_out_list.append(evi_fn)
                    # 输出影像路径
                    out_evi_path = field.split(".")[0] + "_lyt" + ".tif"
                    out_evi_fn = os.path.join(outpath, out_evi_path)
                    evi_out_list.append(out_evi_fn)
                elif field.split("_")[-1].split(".")[0] == 'ndwi':
                    # 输入影像路径
                    ndwi_fn = os.path.join(inpath, field)
                    ndwi_out_list.append(ndwi_fn)
                    # 输出影像路径
                    out_ndwi_path = field.split(".")[0] + "_lyt" + ".tif"
                    out_ndwi_fn = os.path.join(outpath, out_ndwi_path)
                    ndwi_out_list.append(out_ndwi_fn)
                else:
                    pass

        if len(ndvi_out_list)*len(osavi_out_list)*len(rvi_out_list)*len(evi_out_list)*len(ndwi_out_list) == 0:
            print("未检索到影像，请修改检索条件")
            break

        else:
            # 列表排序
            ndvi_out_list.sort()
            osavi_out_list.sort()
            rvi_out_list.sort()
            evi_out_list.sort()
            ndwi_out_list.sort()

    # for i in ndwi_out_list:
    #     print(i)
    # #print(ndwi_out_list)
    return ndvi_out_list, osavi_out_list, rvi_out_list, evi_out_list, ndwi_out_list

def main(inpath,outpath):

    # 影像路径列表

    ndvi_out_list, osavi_out_list, rvi_out_list, evi_out_list, ndwi_out_list = search_f(inpath, outpath)
    fn_list = [ndvi_out_list, osavi_out_list, rvi_out_list, evi_out_list, ndwi_out_list]

    # 打开其中一景影像,作为参考影像
    try :
        example_file = ndvi_out_list[1]
    except :
        IndexError
        print("未检索到影像，请修改检索条件")
    dataset1 = gdal.Open(example_file)
    im_width1 = dataset1.RasterXSize
    im_height1 = dataset1.RasterYSize
    im_proj1 = dataset1.GetProjection()
    im_Geotransform1 = dataset1.GetGeoTransform()

    driver =gdal.GetDriverByName("GTiff")

    band_number = int(len(ndvi_out_list) / 2)

    for f in fn_list:
        outimage = f[-1]

        # 创建影像
        out_NDVI = driver.Create(outimage, im_width1, im_height1, band_number, gdal.GDT_Float32)
        out_NDVI.SetProjection(im_proj1)
        out_NDVI.SetGeoTransform(im_Geotransform1)

        for i in range(band_number):

                # 进度条
                pst = int(100*(i+1)/band_number)
                print('\r{0}{1}{2}%'.format((outimage.split("\\")[-1]),'▉' * int(pst/10), (pst)), end='')

                # 获取影像路径
                file = f[i]

                # 打开影像
                dataset = gdal.Open(file)
                im_proj = dataset.GetProjection()
                dtype = dataset.GetRasterBand(1).DataType

                # 在内存中创建影像
                dst = gdal.GetDriverByName('MEM').Create("", im_width1, im_height1, 1, dtype)
                dst.SetGeoTransform(im_Geotransform1)
                dst.SetProjection(im_proj1)

                # 影像重投影(gdal.ReprojectImage(old, new, old.GetProjection(),model.GetProjection(), gdal.GRA_NearestNeighbour))
                gdal.ReprojectImage(dataset, dst, im_proj, im_proj1, gdalconst.GRA_Bilinear)

                # 获取内存中影像将其转为数组
                bandmask = dst.GetRasterBand(1)
                datamask = bandmask.ReadAsArray()

                out_NDVI.GetRasterBand(i + 1).WriteArray(datamask)

    print("完成")

if __name__ == '__main__':

    inpath = r"\\192.168.0.234\nydsj\user\YXZ\13_forcast\03_vi"
    outpath = r"\\192.168.0.234\nydsj\user\YXZ\13_forcast\04_vi_lys"

    main(inpath, outpath)
