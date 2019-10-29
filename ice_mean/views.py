# -*- coding: utf-8 -*-
"""
Created on Fri May 24 14:52:16 2019

@author: maomao
"""

"""
Copyright (C) 2018 The HDF Group

This example code illustrates how to access and visualize an NSIDC AMSR_U2 L3 
SeaIce12km HDF-EOS5 Grid file in Python.

If you have any questions, suggestions, or comments on this example, please use
the HDF-EOS Forum (http://hdfeos.org/forums).  If you would like to see an
example of any other NASA HDF/HDF-EOS data product that is not listed in the
HDF-EOS Comprehensive Examples page (http://hdfeos.org/zoo), feel free to
contact us at eoshelp@hdfgroup.org or post it at the HDF-EOS Forum
(http://hdfeos.org/forums).

Usage:  save this script and run

    $python AMSR_U2_L3_SeaIce12km_B01_20181008.he5.py

The HDF-EOS5 file must be in your current working directory.

Tested under: Python 2.7.15 :: Anaconda custom (64-bit)
Last updated: 2018-10-10
"""
import io
import os

from django.http import HttpResponse

# Create your views here.
# !usr/bin/env python
# -*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: 19_ice_mean_cyao.py
@time: 2019-09-17 14:33
"""
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 16 10:14:48 2019

@author: xwang
"""

# -*- coding: utf-8 -*-
"""
Created on Fri May 24 14:52:16 2019

@author: maomao
"""

"""
Copyright (C) 2018 The HDF Group

This example code illustrates how to access and visualize an NSIDC AMSR_U2 L3 
SeaIce12km HDF-EOS5 Grid file in Python.

If you have any questions, suggestions, or comments on this example, please use
the HDF-EOS Forum (http://hdfeos.org/forums).  If you would like to see an
example of any other NASA HDF/HDF-EOS data product that is not listed in the
HDF-EOS Comprehensive Examples page (http://hdfeos.org/zoo), feel free to
contact us at eoshelp@hdfgroup.org or post it at the HDF-EOS Forum
(http://hdfeos.org/forums).

Usage:  save this script and run

    $python AMSR_U2_L3_SeaIce12km_B01_20181008.he5.py

The HDF-EOS5 file must be in your current working directory.

Tested under: Python 2.7.15 :: Anaconda custom (64-bit)
Last updated: 2018-10-10
"""
import matplotlib.pyplot as plt
from pyhdf.SD import SD, SDC
from pathlib import Path
import pyproj
import numpy as np
import pickle
import cartopy.crs as ccrs
import datetime
pro_path = os.path.split(os.path.realpath(__file__))[0] # 获取当前路径的父路径

def run(FILE_NAME):
    # start = datetime.datetime.now()
    # Identify the data field.
    DATAFIELD_NAME = 'SI_12km_NH_ICECON_DAY'
    GRID_NAME = 'NpPolarGrid12km'
    #    if FILE_NAME.split('/')[2]=='AE_SI12.003':
    #        USE = True
    #    else:
    #        USE = False
    USE = False
    if USE:
        hdf = SD(FILE_NAME, SDC.READ)
        # Read dataset.
        data2D = hdf.select(DATAFIELD_NAME)
        data = data2D[:, :].astype(np.float64)
    else:
        import h5py
        with h5py.File(FILE_NAME, mode='r') as f:
            name = '/HDFEOS/GRIDS/{0}/Data Fields/{1}'.format(GRID_NAME,
                                                              DATAFIELD_NAME)
            data = f[name][:].astype(np.float64)
    return data


def AMSR(roots_url, x,y):
    # 输入部分
    # roots = Path('../data/seaice')
    roots = Path(roots_url)
    # pkl_file = open(pro_path+"/ice_con_grid.pkl", 'rb')
    # print(pro_path+"/ice_con_grid.pkl")
    # pkl_file = open(pro_path + '\\ice_con_grid.pkl', 'rb')
    # 处理数据 加载网格数据
    # 输入:pkl 这数据是自己生成的，保存成了pkl格式
    # 输出：lon 经读 lat 纬度
    # 这部分数据是用与画图 与hdf数据的·位置信息相互对应
    # spatial_grid = pickle.load(pkl_file)
    # landmask = spatial_grid['landmask']
    xv, yv = np.meshgrid(x, y)
    pstereo = pyproj.Proj("+init=EPSG:3411")
    wgs84 = pyproj.Proj("+init=EPSG:4326")
    lon, lat = pyproj.transform(pstereo, wgs84, xv, yv)
    # 输出路径
    # 图片输出路径
    #    if os.path.exists(output_dir) is not True:
    #        os.makedirs(output_dir)
    # 加载数据部分
    # roots：给数据所在上层文件路径
    record = []
    count = 0
    # '*/*.he5'
    # 数据的路径存放方式：seaice/id/data.he5
    # 由于root 存的是到seaice 所以 这里需要 '*/*.he5' .来确定所有的he5文件
    #    print(list(roots.glob('*.he5')))
    #    print(glob.glob(roots_url+'*'))
    #    pdb.set_trace()
    for index, file in enumerate(list(roots.glob('*.he5'))):
        timestr = file.name.split('_')[-1]
        # 根据文件名 确定年份，此处需要修改成变量
        if int(timestr[0:4]) != 2019:
            continue
        # 根据文件名 确定月份，此处需要根据时间修改成变量
        month = int(timestr[4:6])
        if month != 9:
            continue
        # 转换成字符串
        filename = str(file.absolute())
        data = run(filename)
        if len(record) == 0:
            record = np.copy(data)
        else:
            record = record + np.copy(data)
        count = count + 1
    record = record / count
    record[(record > 100.0)] = 0
    #  >15 海冰密度小于15 不记
    record[(record < 15)] = np.nan
    record[(record >= 15)] = 100
    lon = lon % 360
    return lon, lat, record


def get_map(request, *configs):
    start = datetime.datetime.now()
    """
    example URL:     example URL: http://127.0.0.1:8000/ice_ocean
    :param request:The page sent the GET content request
    :return:HttpResponse object
    """
    if request.method == 'GET':
        if configs:
            pkl_file = open(pro_path+"/ice_con_grid.pkl", 'rb')
            data_url = str(pro_path)+'/data/sea_ice/'
            spatial_grid = pickle.load(pkl_file)
            x = spatial_grid['x']
            y = spatial_grid['y']
            lon, lat, record = AMSR(data_url, x, y)
            print('totally time is ' + str(datetime.datetime.now() - start))
            print(lon)
            print('success')
            print(lat)
            # print(record)
            # 创建窗口1，无白色背景，透明，使用时注释创建窗口2
            # fig = plt.figure("Image", frameon=False, dpi=100, figsize=(36.07, 3.06))
            # fig = plt.figure("Image", figsize=(3.5 * 10, 2.8), dpi=100, frameon=False,)
            # canvas = fig.canvas

            # ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
            # ax.set_extent([float(configs[0]), float(configs[1]), float(configs[2]), float(configs[3])],
            #               crs=ccrs.PlateCarree(central_longitude=0))

            extent = [float(configs[0]), float(configs[1]), float(configs[2]), float(configs[3])]
            x_length = extent[0] - extent[1]
            y_length = extent[2] - extent[3]
            rat = abs(y_length) / abs(x_length)
            # print(rat)
            # 创建窗口2，有白色背景，使用时注释创建窗口1
            fig = plt.figure(figsize=(3.5 * 10, 10 * rat * 3.5), dpi=100)
            canvas = fig.canvas

            ax = plt.axes(projection=ccrs.PlateCarree(central_longitude=0))
            ax.set_extent(extent, crs=ccrs.PlateCarree(central_longitude=0))
            print('totally time is ' + str(datetime.datetime.now() - start))
            ax.pcolormesh(lon, lat, record, cmap='Blues', transform=ccrs.PlateCarree(central_longitude=0))
            print('totally time is ' + str(datetime.datetime.now() - start))
            ax.axis('off')
            for spine in ax.spines.values():
                spine.set_visible(False)
            # print('totally time is ' + str(datetime.datetime.now() - start))
            ax.background_patch.set_visible(False)
            ax.outline_patch.set_visible(False)
            ax.patch.set_alpha(0.)
            plt.gca().xaxis.set_major_locator(plt.NullLocator())
            plt.gca().yaxis.set_major_locator(plt.NullLocator())
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0,
                                hspace=0, wspace=0)
            # plt.savefig("ice_mean.png", transparent=True, dpi=600, bbox_inches=0.0)
            buffer = io.BytesIO()  # 获取输入输出流对象
            canvas.print_png(buffer)  # 将画布上的内容打印到输入输出流对象
            data = buffer.getvalue()  # 获取流的值
            buffer.close()
            result = ""

            # print("{0}".format(result))

            return HttpResponse(data, content_type='image/png')
        else:
            return HttpResponse('configs are wrong.')
    elif request.method == 'POST':
        return HttpResponse('Method is wrong.')
    else:
        return HttpResponse('What are you doing?')
