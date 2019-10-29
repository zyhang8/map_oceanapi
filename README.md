# Map Ocean Api

ocean map server base on django web.

***

## Project setup

```python
pip install -r requirements.txt
```

路径更换

在views里已经注释了linux、mac的路径代码，总共有三处，分别有win和linux的路径版本

## Compiles

局域网内访问

settings/ALLOW_HOSTS加上ip地址

```python
python manage.py runserver 0.0.0.0:8000
```

## 主函数

该例子为处理2019年9月海冰数据
19_ice_mean_cyao 画图 使用方法：修改数据路径，其中timestr，month 需要变为变量
输入文件：
1 ice_con_grid.pkl 网格文件
2 data  数据
输出文件
3 output 例图

## test_url

### ice_ocean

http://127.0.0.1:8000/ice_ocean/latitude1/120/latitude2/122/longitude1/26.5/longitude2/28.5/

method:GET

### ocean_mean

http://127.0.0.1:8000/ice_mean/latitude1/-180/latitude2/180/longitude1/60/longitude2/90/

method:GET

## 所需依赖包

cartopy
matplotlib
pyhdf

根目录下的conda.txt

[参考](https://hdfeos.org/zoo/index_openNSIDC_Examples.php)

## 算法优化问题

### ice_mean

.viws
```python
ax.pcolormesh(lon, lat, record, cmap='Blues', transform=ccrs.PlateCarree(central_longitude=0))
```

AMSR调用了三次读取了三次文件，改成先调用文件，再把文件传递给函数，减少了0.04s

主要是ice_mean这个函数花费时间长，占了一半时间，查了资料后，显示scatter（）也可以画，但是貌似会慢更多，加上pcolormesh这个在可视化里面还算是比较常用的，所以就没改了，总程序在本机运行大概1.1s

### ice_ocean

.views
```python
meshfile = Mesh(file)
```

在运行这个函数前只花了0.08s，运行完就有2s出头。进入了Meshpy.py脚本，其中，def N2E2D这个函数运行时间久且运行了5次，其中field_list运行比较久

```python
[np.sum(field[itri[0:3]]) / 3.0 for itri in self.tri]
```

itri为二维数组，field为一维数组,tri为3列62069行的二维数组,因为每次遍历都需要读取2dm文件并且遍历，所以就把遍历过程放在调取函数前，存在一个field——lists列表，这样就只需调取一次2dm的数据，该程序原本运行时间2s，现在为1s

