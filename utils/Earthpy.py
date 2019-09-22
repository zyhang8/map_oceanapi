#!/usr/bin/env python
# -*- coding: utf-8 -*-

__Date__ = "2016/08/15 12:34 AM"
__Author__ = "An Baichao"
__Email__ = "anbaichao@gmail.com"
__Version__ = "1.0"

import logging
import numpy as np

logger = logging.getLogger(__name__)


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
    if np.all(np.abs(lat1 - lat2) < 0.00001) and np.all(np.abs(long1 - long2) < 0.00001):
        logger.debug("! message | distance : The same point ")
        logger.debug("! message | distance : lon {:} , lat {:}".format(long1 - long2, lat1 - lat2))
        logger.debug("! message | distance : lon {:} , {:}".format(long1, long2))
        logger.debug("! message | distance : lat {:} , {:}".format(lat1, lat2))
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

        # process the numpy bug: floating point inaccuracy, which will give 1.0000000000000002.
        if np.any(cos11 > 1.0):
            if not np.any((cos11 - 1.0) > 0.001):
                cos11[cos11 > 1.0] = 1.0
            else:
                raise ValueError("The input value of np.arccos greater than 1.0 !")
        arc = np.arccos(cos11)

        # Remember to multiply arc by the radius of the earth
        # in your favorite set of units to get length.
        rho = 6371004.
        distance = rho * arc

    return distance


class LatLonRange:
    def __init__(self, longitude, latitude, int_step, expand=0):

        lat_ceil = np.ceil(np.amax(latitude) / int_step) * int_step + expand
        lat_floor = np.floor(np.amin(latitude) / int_step) * int_step - expand
        lon_ceil = np.ceil(np.amax(longitude) / int_step) * int_step + expand
        lon_floor = np.floor(np.amin(longitude) / int_step) * int_step - expand

        self.latlonRange = [lat_floor, lat_ceil, lon_floor, lon_ceil]

    def match(self, source):

        latitude8 = np.arange(-90., 90., 0.125)
        longitude8 = np.arange(0., 360., 0.125)

        latitude10 = np.arange(-90., 90., 0.1)
        longitude10 = np.arange(0., 360., 0.1)

        if source == '1/8':
            source = {'latitude': latitude8, 'longitude': longitude8}
        elif source == '1/10':
            source = {'latitude': latitude10, 'longitude': longitude10}

        lat_floor = source['latitude'][np.argmin(np.absolute(source['latitude'] - self.latlonRange[0]))]
        lat_ceil = source['latitude'][np.argmin(np.absolute(source['latitude'] - self.latlonRange[1]))]
        lon_floor = source['longitude'][np.argmin(np.absolute(source['longitude'] - self.latlonRange[2]))]
        lon_ceil = source['longitude'][np.argmin(np.absolute(source['longitude'] - self.latlonRange[3]))]

        logger.debug(np.argmin(np.absolute(source['latitude'] - self.latlonRange[0])))
        logger.debug(np.argmin(np.absolute(source['latitude'] - self.latlonRange[1])))

        self.latlonRange = [lat_floor, lat_ceil, lon_floor, lon_ceil]

    def grid(self, step):
        if step == 1/10:
            self.match('1/10')
        elif step == 1/8:
            self.match('1/8')

        x = np.arange(self.latlonRange[2], self.latlonRange[3], step)
        y = np.arange(self.latlonRange[0], self.latlonRange[1], step)

        x2d, y2d = np.meshgrid(x, y)

        return x, y, x2d, y2d
