# -*- coding: utf-8 -*-
"""
Created on Wed Jun 17 12:32:57 2015

@author: ban
"""
import numpy as np
from matplotlib.path import Path


def contain_points(Area_range, points, flag='true'):
    """ return the bool_index of points in path
    
    """
    APath = Path(Area_range)
    bool_index = APath.contains_points(points)
    if flag == 'true':
        index = np.where(bool_index)
    elif flag == 'false':
        index = np.where(np.logical_not(bool_index))
    return index


def get_range_LL(lon, lat, LLrange):
    # LLrange : [LonMin,LonMax,LatMin,LatMax]
    # index = get_coincide([lon,lat],[mesh.lon,mesh.lat])


    index = np.where(np.all([lon >= LLrange[0], lon <= LLrange[1], lat >= LLrange[2], lat <= LLrange[3]], axis=0))[0]

    return index


def distance_on_sphere(long1, lat1, long2, lat2, ):
    """
    Function for calc the distance between two locations on earth.
    
    Codes From : http://www.johndcook.com/blog/python_longitude_latitude/
    
    reference : http://www.movable-type.co.uk/scripts/latlong.html
    
                https://pypi.python.org/pypi/geopy
    # Convert latitude and longitude to 
    # spherical coordinates in radians.
    degrees_to_radians = np.pi/180.0
         
    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians
         
    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians
         
    # Compute spherical distance from spherical coordinates.
         
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
     
    cos11 = (np.sin(phi1)*np.sin(phi2)*np.cos(theta1 - theta2) + 
           np.cos(phi1)*np.cos(phi2))
    arc = np.acos( cos11 )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
 
    rho=6371000.
    distance=rho*arc
    
    """
    # todo : I think the method above is error, check it
    # no, It has 90-lat, so it is correct

    if (np.all(np.abs(lat1 - lat2) < 0.00001) and np.all(np.abs(long1 - long2) < 0.00001)):
        print("! message | distance : The same point ")
        print("! message | distance : lon {:} , lat {:}".format(long1 - long2, lat1 - lat2))
        print("! message | distance : lon {:} , {:}".format(long1, long2))
        print("! message | distance : lat {:} , {:}".format(lat1, lat2))
        distance = 0.

    else:
        # phi = 90 - latitude
        phi1 = np.deg2rad(90.0 - lat1)
        phi2 = np.deg2rad(90.0 - lat2)

        # theta = longitude
        theta1 = np.deg2rad(long1)
        theta2 = np.deg2rad(long2)

        # Compute spherical distance from spherical coordinates.

        # For two locations in spherical coordinates 
        # (1, theta, phi) and (1, theta', phi')
        # cosine( arc length ) = 
        #    sin(phi)*sin(phi')*cos(theta-theta') + cos(phi)*cos(phi')
        # distance = rho * arc length

        cos11 = (np.sin(phi1) * np.sin(phi2) * np.cos(theta1 - theta2) +
                 np.cos(phi1) * np.cos(phi2))
        # cos11 = (np.cos(phi1) * np.cos(phi2) * np.cos(theta1 - theta2) +
        #          np.sin(phi1) * np.sin(phi2))
        arc = np.arccos(cos11)

        # Remember to multiply arc by the radius of the earth 
        # in your favorite set of units to get length.

        rho = 6371004.
        distance = rho * arc

    return distance


def lim(x, flag='int'):
    if flag == 'int':
        xlim = [np.floor(min(x)), np.ceil(max(x))]
    elif flag == 'orig':
        xlim = [min(x), max(x)]

    return xlim


def find_nearest(array, value):
    idx = (np.abs(array - value)).argmin()
    return idx, array[idx]


def nearest_point(lon, lat, lon_sta, lat_sta):
    # ------- get nearest point ------
    node_id = np.argmin((lat - lat_sta) ** 2 + (lon - lon_sta) ** 2)
    return node_id
