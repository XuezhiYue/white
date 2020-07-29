#!/Users/wxl/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
"""
  @Author  : Yxz
  @contact: yuexuezhi091@gmail.com
  @Software: PyCharm
  @FileName: get_mul_ref_vi.py
  @Time    : 2020/7/27 16:37
  @desc:
"""
import sys
import os
from VI import get_vi_ref
def search_f(inpath):
    F_list = []
    for root, dir, fields in os.walk(inpath):
        for field in fields:
            if field.endswith("tif") is True:
                f_fn = os.path.join(inpath, field)
                F_list.append(f_fn)

    if len(F_list) == 0:
        print("路径：{0} 未检索到 .tif 影像".format(inpath))
        sys.exit()

    return F_list

def main(input_zone_polygon,Ref_vi_out,raster_path):

    fn_list = search_f(raster_path)

    for f in fn_list:

        # 以影像日期为csv名
        Ref = f.split("\\")[-1].split(".")[0].split("_")[0] + "_ref.csv"
        VI = f.split("\\")[-1].split(".")[0].split("_")[0] + "_vi.csv"
        Ref_path = os.path.join(Ref_vi_out, Ref)
        VI_path = os.path.join(Ref_vi_out, VI)

        if os.path.exists(Ref_path) or os.path.exists(VI_path):
            print("输出文件:{0}，{1} 已存在".format(Ref_path, VI_path))
            sys.exit()

        get_vi_ref(input_zone_polygon, f, Ref_path, VI_path)

        print("done")

if __name__ == '__main__':

    #待提取影像的文件夹路径
    raster_path = r"C:\Users\marshmallow\Desktop\1\image"
    # 待提取shp绝对路径
    input_zone_polygon = r"C:\Users\marshmallow\Desktop\1\Export_Output.shp"
    # 反射率、植被指数输出位置
    Ref_vi_out = r"C:\Users\marshmallow\Desktop\1\out"

    main(input_zone_polygon, Ref_vi_out, raster_path)