#!/Users/wxl/anaconda3/bin/python3.7
# -*- coding: utf-8 -*-
"""
  @Author  : Yxz
  @contact: yuexuezhi091@gmail.com
  @Software: PyCharm
  @FileName: docker_test.py
  @Time    : 2020/5/26 18:26
  @desc:
"""
import os
from pyodm import Node
import time
from tqdm import tqdm

image_dir = r"D:\datasets\project\images"
result_path = image_dir.split('/')[0] + '_results'
ip = 'localhost'  # 改为自己的ip
port = 3000

start = time.time()
images_name = os.listdir(image_dir)
images_name = [image_dir + image_name for image_name in images_name]
print(images_name)

n = Node(ip, port)
print("Node连接成功，{}张图开始处理".format(len(images_name)))

task = n.create_task(images_name, {'orthophoto-resolution': 0.0274, "min-num-features": 35000})
print("任务创建完成")
pbar = tqdm(total=100)
processing = 0
while True:
    info = task.info()
    if info.progress == 100:
        break
    pbar.update(info.progress - processing)
    processing = info.progress
    if info.last_error != '':
        print("error ", info.last_error)

    time.sleep(0.1)
pbar.close()

print("处理完成")
# task.wait_for_completion()
task.download_assets(result_path)

print("{}张图消耗{}秒".format(len(images_name), time.time() - start))
