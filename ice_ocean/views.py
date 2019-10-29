# Create your views here.
import io
import os

import cartopy.crs as ccrs
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import numpy as np
from django.http import HttpResponse
from matplotlib.tri import Triangulation

from .Meshpy import Mesh
import datetime


def gen_map(request, *configs):
    start = datetime.datetime.now()
    """
    example URL: http://127.0.0.1:8000/ice_oceanapi/120/122/26.5/28.5/
    :param request:The page sent the GET content request
    :return:HttpResponse object
    """
    if request.method == 'GET':
        if configs:
            # 类型名称
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
            extent = [float(configs[0]), float(configs[1]), float(configs[2]), float(configs[3])]
            # extent = [120, 122, 26.5, 28.5]
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
            # print('totally time is ' + str(datetime.datetime.now() - start))
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
            # plt.savefig("ice_ocean\\media\\07192.png", dpi=144, bbox_inches=0.0, transparent=True, profile='tiny')
            # 第二种保存方式（获取Plt的数据并使用cv2进行保存）
            buffer = io.BytesIO()  # 获取输入输出流对象
            canvas.print_png(buffer)  # 将画布上的内容打印到输入输出流对象
            data = buffer.getvalue()  # 获取流的值
            # print("plt的二进制流为:\n", data)
            # buffer.write(data)  # 将数据写入buffer
            # img = Image.open(buffer)  # 使用Image打开图片数据
            # img = np.asarray(img)
            # print("转换的图片array为:\n", img)
            buffer.close()
            result = ""
            print('totally time is ' + str(datetime.datetime.now() - start))
            print("{0}".format(result))
            return HttpResponse(data, content_type='image/png')
        else:
            return HttpResponse('configs are wrong.')

    elif request.method == 'POST':
        return HttpResponse('Method is wrong.')
    else:
        return HttpResponse('What are you doing?')
