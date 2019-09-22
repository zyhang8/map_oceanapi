#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import datetime

__DATE__ = 2016 / 10 / 10
__author__ = "ban"
__email__ = "bcan@shou.edu.cn"
__version__ = "1.0"

# start_time=np.array(Ptime(time[0],'mjulian').Format('mpl'))+TimeZone/24.0
# ptime_obs=Ptime(ptime_obs.Format('mjulian')-8.0/24.0,'mjulian')


class Ptime:
    """The date time in various styles transform class.
    The core is the python datetime object , different types firstly trans to datetime object.
    Then process and output in different format.
    Vars:
        time_data : The input time data in original type.
        type      : The input time data type , this is specified by users.
        Time      : The time data in python datetime type. This is the core data
    Methods:
        parse_time: parse the time data to datetime object
                    input : time_data flag
        format    : output the time in Format.
                    input : type
    """

    def __init__(self, time_data, style='', debug=0):
        self.debug = debug
        self.time_data = time_data
        self.style = style
        self.Time = self.parse_time
        try:
            self.ntime = len(self.Time)
        except TypeError:
            self.ntime = 1

    def __repr__(self):
        return 'ptime({:})'.format(self.Time)

    def __len__(self):
        return len(self.Time)

    def __getitem__(self, position):
        return Ptime(self.Time[position])

    def __add__(self, other):
        time = np.concatenate((self.Time, other.Time))
        return Ptime(time)

    @property
    def parse_time(self, ):

        if not self.style:
            times = self.time_data

        elif self.style.find("delta") != -1:
            times = parse_delta(self.time_data)

        elif self.style.find("str") != -1 or self.style.find('%') != -1 or self.style.find("FVCOM") != -1:
            if self.style.find("str") != -1:
                fmt = "%Y-%m-%d_%H:%M:%S"
            elif self.style.find("FVCOM") != -1:
                fmt = "%Y-%m-%dT%H:%M:%S"
            else:
                fmt = self.style
            if isinstance(self.time_data, str):
                times = datetime.datetime.strptime(self.time_data, fmt)
            else:
                times = []
                for itime in self.time_data:
                    time_elem = datetime.datetime.strptime(itime, fmt)
                    times.append(time_elem)
                times = np.asarray(times)

        elif self.style.find("range") != -1:
            if isinstance(self.time_data[0], datetime.datetime):
                time_start = self.time_data[0]
            else:
                time_start = Ptime(self.time_data[0], 'str').Time

            if isinstance(self.time_data[1], datetime.datetime):
                time_stop = self.time_data[1]
            else:
                time_stop = Ptime(self.time_data[1], 'str').Time

            time_delta = datetime.timedelta(hours=float(self.time_data[2]))

            times = time_range2list(time_start, time_stop, time_delta)

        else:
            if isinstance(self.time_data, (float, np.float, np.float32, np.float64)):
                times = parse_time_from_floatformat(self.time_data, self.style)
            else:
                times = []
                for itime in self.time_data:
                    time_elem = parse_time_from_floatformat(itime, self.style)
                    times.append(time_elem)
                times = np.asarray(times)

        return times

    def format(self, style):
        """ Output date and time in different format.

        Need to specify the output style, Support these styles currently：
            str format:
                default :
                FVCOM_str :
                json-str :
                user defined by "%"
            float format:
                mjulian, matlab, mpl
                ncep, ECMWF

        Note: if you want python datetime format, just use ptime.Time.
        """

        # force all input data to array
        # TypeError: iteration over a 0-d array
        if type(self.Time) == datetime.datetime:
            times = np.array([self.Time])
        else:
            times = self.Time

        # ------------ for str format  --------------
        # the time_out array's dtype must specify the length, just like 26
        # 'S' in python3 and numpy 1.13 means bytes, for compatible with py2.
        # so the correct dtype should be U26
        if style.find('str') != -1:
            time_out = np.empty_like(times, dtype='U26')
            if style is 'FVCOM_str':
                time_str_format = "%Y-%m-%dT%H:%M:%S.%f..."
            elif style is 'json_str':
                # 2016-01-01T00:00:00.000Z
                time_str_format = "%Y-%m-%d_%H:%M:%S.%fZ"
            else:

                time_str_format = "%Y-%m-%d_%H:%M:%S..."  # '...' for [:-3]

            for i, itime in enumerate(times):
                time_out[i] = str(itime.strftime(time_str_format))[:-3]

        elif style.find('%') != -1:
            time_out = np.empty_like(times, dtype='U48')
            for i, itime in enumerate(times):
                time_out[i] = datetime.datetime.strftime(itime, style)

        else:

            time_out = np.empty_like(times, dtype=np.float64)
            for i, itime in enumerate(times):
                time_out[i] = floatformat_time(itime, style)

        if len(time_out) == 1:
            time_out = time_out[0]

        return time_out

    def format_fvcom(self, ):
        """ format the ptime to tide format.

        tide time format has 4 elements: iint,time,itime,itime2,times
        iint is the time index, just set it to zero.
        time is mjulian float format.
        itime is the int part of mjulian float time
        itime2 is the decimal part of mjulian float time

        the mjulian float format time should be doule-float,
        while the result of tide is stored by single-float data type.
        so need two int(itime,itime2) to store the mjulian time.
        """
        iint = np.zeros_like(self.Time, dtype=int)
        time = self.format('mjulian')
        itime = np.floor(time)
        # 1000 millisecond = 1 second
        itime2 = (time - itime) * 24 * 60 * 60 * 1000
        times = self.format("FVCOM_str")

        return iint, time, itime, itime2, times


def parse_time_from_floatformat(time_data, kind='mjulian'):
    if kind is 'mjulian':
        """mjulian dates are relative to 1858/11/17 00:00:00 and stored in days.
        """
        time_zero = datetime.datetime(1858, 11, 17, 0, 0, 0)
        time_delta = datetime.timedelta(days=np.float64(time_data))

    elif kind is 'matlab':
        """MATLAB's dates are relative to 0000/01/00 00:00:00 and stored in days.
        as python datetime minyear=1.trans it to mjulian , the diff is 678942.0
        """
        time_zero = datetime.datetime(1858, 11, 17, 0, 0, 0)
        time_delta = datetime.timedelta(days=np.float64(time_data - 678942.0))

    elif kind is 'gregorian':
        time_zero = datetime.datetime(1950, 1, 1, 0, 0, 0)
        time_delta = datetime.timedelta(days=np.float64(time_data))

    elif kind is 'excel':
        """ excel dates are relative to 1900/01/01 00:00:00 and stored in days.
        """
        time_zero = datetime.datetime(1900, 1, 1, 0, 0, 0)
        time_delta = datetime.timedelta(days=np.float64(time_data))

    elif kind is 'ncep':
        """ncep dates are relative to 1800/01/01 00:00:00 and stored in hours.
        """
        time_zero = datetime.datetime(1800, 1, 1, 0, 0, 0)
        time_delta = datetime.timedelta(hours=np.float64(time_data))

    elif kind is 'ECMWF':
        """ ECMWF dates are relative to 1900/01/01 00:00:00 and stored in hours.
        """
        time_zero = datetime.datetime(1900, 1, 1, 0, 0, 0)
        time_delta = datetime.timedelta(hours=np.float64(time_data))

    elif kind is 'noaa':
        time_zero = datetime.datetime(1981, 1, 1, 0, 0, 0)
        time_delta = datetime.timedelta(seconds=np.float64(time_data))

    else:
        """default is mjulian"""
        time_zero = datetime.datetime(1858, 11, 17, 0, 0, 0)
        time_delta = datetime.timedelta(days=np.float64(time_data))

    return time_zero + time_delta


def parse_delta(time_data):
    time_delta = datetime.timedelta(hours=time_data)
    # Time_delta = datetime.timedelta(days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0)
    return time_delta


def time_range2list(time_start, time_end, time_delta):
    times_list = []
    itime = time_start
    while itime <= time_end:
        times_list.append(itime)
        itime = itime + time_delta
    times = np.array(times_list, dtype=datetime.datetime)

    return times


def floatformat_time(time_data, kind):
    if kind.startswith('m'):
        # give the modify julian time_zero
        time_zero = datetime.datetime(1858, 11, 17, 0, 0, 0)
        times_m = float((time_data - time_zero).days) + \
                  ((float((time_data - time_zero).seconds) / 3600.0) / 24.0)
        if kind is 'matlab':
            times = times_m + 678942.0
        elif kind is 'mpl':
            times = times_m + 678576.0
        else:
            times = times_m

    elif kind.startswith('ncep'):
        time_zero = datetime.datetime(1800, 1, 1, 0, 0, 0)
        times = (time_data - time_zero).days * 24. + (time_data - time_zero).seconds / 3600.0

    elif kind.startswith('ECMWF'):
        time_zero = datetime.datetime(1900, 1, 1, 0, 0, 0)
        times = (time_data - time_zero).days * 24. + (time_data - time_zero).seconds / 3600.0
    else:
        times = time_data

    return times


def get_coincide_time(ptime_model, ptime_obs, debug=0):

    index_model = []
    index_obs = []
    coincide_time = []
    for i, itime_model in enumerate(ptime_model.Time):
        for j, jtime_obs in enumerate(ptime_obs.Time):
            if itime_model == jtime_obs:
                index_model.append(i)
                index_obs.append(j)
                coincide_time.append(itime_model)


    index_model = np.asarray(index_model)
    index_obs = np.asarray(index_obs)
    coincide_time = np.asarray(coincide_time)

    return index_model, index_obs, coincide_time


def get_match_time(ptime_model, ptime_obs, method='datetime'):

    if method == 'datetime':
        time_start = max(ptime_model.Time[0], ptime_obs.Time[0])
        time_stop = min(ptime_model.Time[-1], ptime_obs.Time[-1])

        bool_model = np.all([ptime_model.Time > time_start, ptime_model.Time < time_stop], axis=0)
        bool_obs = np.all([ptime_model.Time > time_stop + 0.003, ptime_model.Time < time_stop - 0.003], axis=0)

        index_model = np.arange(len(ptime_model.Time))[bool_model]
        index_obs = np.arange(len(ptime_obs.Time))[bool_obs]

        time_wanted = ptime_model.Time[bool_model]

    elif method == 'mjulian':
        time_model = ptime_model.format('mjulian')
        time_obs = ptime_obs.format('mjulian')

        times = max(time_model[0], time_obs[0])
        time_stop = min(time_model[-1], time_obs[-1])

        # 0.0015 for model time single precision
        #    bool_model=np.all([time_model>=times,time_model<=timee], axis=0)
        #    bool_obs=np.all([time_obs>=times,time_obs<=timee], axis=0)

        bool_model = np.all([time_model > times + 0.003, time_model < time_stop - 0.003], axis=0)
        bool_obs = np.all([time_obs > times + 0.003, time_obs < time_stop - 0.003], axis=0)

        index_model1 = np.arange(len(time_model))
        index_obs1 = np.arange(len(time_obs))

        index_model = index_model1[bool_model]
        index_obs = index_obs1[bool_obs]

        time_wanted = time_model[bool_model]

    else:
        index_model = index_obs = time_wanted = []

    return index_model, index_obs, time_wanted
