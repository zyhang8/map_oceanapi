# Create your views here.
import base64
import os
import io
import json
from django.shortcuts import render
import cv2
import cartopy.crs as ccrs
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.tri import Triangulation
from django.http import JsonResponse, HttpResponse
from .Meshpy import Mesh
from PIL import Image

def gen_mat(request, para1, para2, para3 ,para4):
    # !usr/bin/env python
    # -*- coding:utf-8 _*-
    """
    @author:yaochenyang
    @file: 1_16basemap+grid.py
    @time: 2019-07-15 16:45
    """
    # 类型名称
    # type_name = request.POST['type_name']
    type_name = request.POST.get('type_name')
    # 类型排序
    type_sort = request.POST.get('type_sort')

    current_path = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.abspath(os.path.join(current_path, '../'))
    # print(project_path)

    # https://plot.ly/python/surface-triangulation/
    # https://www.hatarilabs.com/ih-en/triangular-mesh-for-groundwater-models-with-modflow-6-and-flopy-tutorial
    """
        param extent : 确定显示区域
        param file   :  输入文件
    """
    extent = [120, 122, 26.5, 28.5]
    # 根据显示范围对图像长宽进行调整
    x_length = extent[0] - extent[1]
    y_length = extent[2] - extent[3]
    rat = x_length / y_length
    f1 = plt.figure(figsize=(5, 5 * rat))
    ax = f1.add_subplot(111, projection=ccrs.PlateCarree())
    canvas = f1.canvas
    # 窗口调整
    ax.axis('off')
    ax.set_position([0, 0, 1, 1])
    ax.set_extent(extent)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.background_patch.set_visible(False)
    ax.outline_patch.set_visible(False)
    ax.set_xlim(extent[0], extent[1])
    ax.set_ylim(extent[2], extent[3])
    ax.patch.set_alpha(0.)
    # 首先需要了解的是，加在特定的环境进行数据读取
    triangles_2dm = []
    position = []
    file = 'data_depth/NSwz_001E.2dm'
    meshfile = Mesh(file)
    for index in range(0, len(meshfile.ED)):
        xx = [int(values) - 1 for values in meshfile.ED[index][2:5]]
        triangles_2dm.append(xx)
    tri = Triangulation(meshfile.lon, meshfile.lat, triangles=triangles_2dm)
    # 调整水深
    levels = np.arange(0., 120., 10.0)
    # 颜色调整
    cmap = cm.get_cmap(name='Blues', lut=None)
    # 画图
    cntr2 = ax.tricontourf(tri, meshfile.h, levels=levels, cmap=cmap, transform=ccrs.PlateCarree())

    # 第一种保存方式（直接对plt 进行保存）
    # 保存图片
    plt.savefig("tightback\\media\\07192.png", dpi=144, bbox_inches=0.0, transparent=True, profile='tiny')
    # 第二种保存方式（获取Plt的数据并使用cv2进行保存）
    buffer = io.BytesIO()  # 获取输入输出流对象
    canvas.print_png(buffer)  # 将画布上的内容打印到输入输出流对象
    data = buffer.getvalue()  # 获取流的值
    print("plt的二进制流为:\n", data)
    # buffer.write(data)  # 将数据写入buffer
    # img = Image.open(buffer) # 使用Image打开图片数据
    # img = np.asarray(img)
    # print("转换的图片array的尺寸为:\n", img.shape)
    # print("转换的图片array为:\n", img)
    # print(img)
    # cv2.imwrite("02.jpg", img)
    # file = open('media\\01792.png','rb')
    # d = os.path.dirname(__file__)
    # print("d="+str(d))
    # imagepath = os.path.join(d, "media\\07192.png")
    # imagepath = os.path.join(d, "media\\" + str(news_id) + ".png")
    # result = open(imagepath, "rb").read()
    # result = base64.b64encode(result)
    # imagedata = base64.b64encode(result)
    # print(str(badata)
    #     # return HttpResponse("dase64_data))
    # print(imageta:image/png;base64," + base64.encodebytes(result).decode(),
    #                     content_type="image/png")\
    buffer.close()
    print(base64.encodebytes(data).decode())
    # 先解码二进制再加密到base64供前端解码
    ret = {
        'para1': para1,
        'para2': para2,
        'para3': para3,
        'para4': para4,
    }
    print(ret)
    return HttpResponse(base64.encodebytes(data).decode(), content_type='image/png')
    # return HttpResponse(json.dumps(result,ensure_ascii=False), content_type="application/json,charset=utf-8")
    # ret = {
    #     'data': str(base64_data),
    #     'result': result,
    # }
    # return JsonResponse(ret)

    # return render(request, 'tightback.html', {"data": result})
