# -*- coding: utf-8 -*-
import numpy as np
from scipy.interpolate import griddata, interp2d


def select_points(x, y, r):
    """
    select nodes from unstructured-grids, just select node for enough distance,other than interp.
    
    Var List:
    Input:
    x  :  The x-axis values, 1D array.
    y  :  The y-axis values, 1D array.
    r  :  The distance. unit follows the x,y 
    
    Midput:
    r_dis  :  The distance from the current node to each node in selected nodes.
    
    Output:
    index  :  The nodes selected index pool.
    
    """

    # The first node is selected.
    index = np.array([0])

    # ----------------------------------------------------------------------------
    # A loop for each node in input nodes ,except the first one.
    # if the distances from the current node to each node selectd are longer than r.
    # select current node to index pool.
    # ----------------------------------------------------------------------------
    for i in range(1, len(x)):
        r_dis = np.sqrt((x[index] - x[i]) ** 2. + (y[index] - y[i]) ** 2.)
        if np.all(r_dis >= r):
            index = np.append(index, i)


    return index


def griddata_fvcom(lon, lat, data, nlevel=200):
    """
    Created on Thu Apr 30 11:23:31 2015
    
    @author: ban
    """
    # the max & min
    maxlon = np.ceil(max(lon))
    minlon = np.floor(min(lon))
    maxlat = np.ceil(max(lat))
    minlat = np.floor(min(lat))

    # The cordinate data
    x = np.linspace(minlon, maxlon + 1, nlevel)
    y = np.linspace(minlat, maxlat + 1, nlevel)
    loni, lati = np.meshgrid(x, y)

    data_grid = griddata((lon, lat), data, (loni, lati), method='cubic')

    return loni, lati, data_grid


def IDW_interp(x, y, z, xi, yi, num=6):
    """Inverse Distance Weighted (IDW) Interpolation.
    
    Usage:  zi=interp(x,y,z,xi,yi,num=6)
    ----------------------------------------------------
    Variable List:
    
    Input:
        x,y    : the points.
        z      : the points' values.
        xi,yi  : the point required.
        num    : the number of points uesd by interp.
    
    Self:
        RD     : reverse distance
        RD2    : RD will change , so there is RD2.
        weight : the weight of the data point
    
    Output:
        zi     : the data value of the point required
    -----------------------------------------------------
    Version:
        V1.0  2015/5/14
    
    Author :
        anbaichao@gmail.com
    -----------------------------------------------------
    """
    # ----- calc the RD of all data point -----
    RD = 1 / np.hypot(x - xi, y - yi)

    # ----- get the max RD points index (num) -----
    # --- meaning the nearest points (num)
    index = np.empty((num), dtype=int)
    for i in range(num):
        index[i] = np.argmax(RD)
        RD[index[i]] = 1. / 999999.

    # ------ calc the weight of points(num) -----
    RD2 = 1 / np.hypot(x - xi, y - yi)
    weight = RD2[index] / np.sum(RD2[index])

    # ------ check the weight and points used------
    if np.sum(weight) - 1.0 > 0.0001:
        print("Error : the sum of weight is not 1,diff is 0.0001")

    print((np.sum(1.0 / RD2[index]) / num))

    # ------ calc the point request value -----
    zi = np.sum(z[:, index] * weight, axis=1)

    return zi


def Nearest_interp(x, y, z, xi, yi):
    """Just find the nearest point and use the value .
    
    Usage:  zi=Nearest_interp(x,y,z,xi,yi)
    ----------------------------------------------------
    Variable List:
    
    Input:
        x,y    : the points.
        z      : the points' values.
        xi,yi  : the point required.
    
    Self:
        RD     : reverse distance
        RD     : RD will change , so there is RD2.
        weight : the weight of the data point
    
    Output:
        zi     : the data value of the point required
    -----------------------------------------------------
    Version:
        V1.0  2015/5/14
    
    Author :
        anbaichao@gmail.com
    -----------------------------------------------------
    """
    if type(xi) != 'numpy.ndarray':
        xi = np.array([xi]).T
        yi = np.array([yi]).T

    zi = []
    for i in range(len(xi)):
        # ------- get nearest point ------
        node_id = np.argmin(np.hypot(x - xi[i], y - yi[i]))

        if z.ndim == 1:
            zi.append(z[node_id])
        elif z.dim == 2:
            zi.append(z[:, node_id])
        #        elif z.dim==3:
        #            zi=z[:,:,node_id]

    return np.array(zi)
