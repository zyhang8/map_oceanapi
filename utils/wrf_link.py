#!/home/users/oper/opt/bin/python
# -------
# Should add the check codes for files exist status
#
import os
import logging
import subprocess
from datetime import datetime, timedelta
from doms.utils import check_purge

logger = logging.getLogger(__name__)


def link_grib(Data_Path, WPS_Path, TR, case='GFS', run_Para=12):
    # -----------------------------------------------------------
    # The Data path example:
    #
    # Forecast : gfs.t12z.pgrb2.0p25.f000
    # Hindcast : fnl_20170423_00_00.grib2
    # -----------------------------------------------------------

    alpha = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
             'V', 'W', 'X', 'Y', 'Z']

    check_purge(WPS_Path, r"GRIBFILE\.\w{3}")

    sdate = TR.start
    edate = TR.end
    if case == "GFS":
        dtime = TR.delta_6H
    elif case == "GFS_Forecast":
        dtime = TR.delta_6H

    idate = sdate

    i1 = 0
    i2 = 0
    i3 = 0

    index = 0
    while idate <= edate:

        if case == "GFS":
            filename = 'fnl_{:}.grib2'.format(idate.strftime('%Y%m%d_%H_%M'))
        elif case == "GFS_Forecast":
            filename = '{:}UTC/gfs.t{:0>2d}z.pgrb2.0p25.f{:0>3d}'.format(TR.start_flag, run_Para,
                                                                         index * 6 + TR.start.hour - run_Para)

        logger.info("link_grib: {:}".format(filename))

        idate = idate + dtime

        linkname = "GRIBFILE.{:}{:}{:}".format(alpha[i3], alpha[i2], alpha[i1])

        i1 = i1 + 1

        if i1 > 25:
            i1 = 0
            i2 = i2 + 1

        if i2 > 25:
            i2 = 0
            i3 = i3 + 1

        if i3 > 25:
            print("RAN OUT OF GRIB FILE SUFFIXES!")

        Source_path = "{:}/{:}".format(Data_Path, filename)

        if os.path.isfile(Source_path):
            os.symlink("{:}/{:}".format(Data_Path, filename), "{:}/{:}".format(WPS_Path, linkname))
        else:
            # print("There are no these files,check your path or time range !")
            raise FileExistsError("There are no these files,check your path or time range !")

        index = index + 1

    logger.info("The Init files has been linked !")
    logger.info(Data_Path)
    logger.info(WPS_Path)


def link_met(Data_Path, WRF_Path, TR, domain_num=2):
    # purge the old links in DST_path
    # met_em.d01.2014-09-01_00:00:00.nc
    check_purge(WRF_Path, r"met_em\.d0.+\.nc")

    sdate = TR.start
    edate = TR.end
    dtime = TR.delta_6H

    idate = sdate

    while idate <= edate:

        for i in list(range(1, domain_num + 1)):

            filename = 'met_em.d0{:}.{:}:00:00.nc'.format(i, idate.strftime('%Y-%m-%d_%H'))
            logger.info(filename)

            Source_path = os.path.join(Data_Path, TR.start_flag, filename)
            if os.path.isfile(Source_path):
                os.symlink(Source_path, os.path.join(WRF_Path, filename))
            else:
                print("No these files,check your path or time range !")

        idate = idate + dtime
    logger.info("The met_em files has been linked !")
