# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 00:57:07 2015

@author: ban
"""
import os
import logging

import numpy as np
import subprocess
from doms.utils.Fiopy import write_dat

logger = logging.getLogger(__name__)


class TPXO:
    def __init__(self, mesh, ptime, casename='Ban', mode="predict", TPXO_Path="default"):

        self.mesh = mesh
        self.ptime = ptime
        self.CaseName = casename
        self.mode = mode
        if TPXO_Path == 'default':
            self.TPXO_Path = "/home/users/ban/ocean/TPXO_models/TPXO7.2_Chinasea"
        else:
            self.TPXO_Path = TPXO_Path

        self.TPXO_LL = os.path.join(self.TPXO_Path, '{:}_TPXOLL.dat'.format(casename))
        self.TPXO_setup = os.path.join(self.TPXO_Path, '{:}_TPXO.setup'.format(casename))
        self.TPXO_time = os.path.join(self.TPXO_Path, '{:}_TPXOtime.dat'.format(casename))
        self.TPXO_output = os.path.join(self.TPXO_Path, '{:}_obc_elj.out'.format(self.CaseName))

        if self.mode == 'predict':
            self.runTPXO_predict()
            [self.Lat, self.Lon, self.elev, self.DateTimelist] = self.parseTPXOelev(self.TPXO_output)
        elif self.mode == 'extract':
            self.runTPXO_extract()
            [self.Lat, self.Lon, self.HC] = self.parseTPXOHC(self.TPXO_output)

    def runTPXO_extract(self, ):
        logger.info("Start the TPXO extract_HC")

        self.writeTPXOsetup(self.TPXO_setup, self.CaseName)
        self.writeTPXOlatlon(self.TPXO_LL, self.mesh)

        Cur_PATH = os.getcwd()
        os.chdir(self.TPXO_Path)

        CMD = "./extract_HC<{:}".format(self.TPXO_setup)
        p = subprocess.call(CMD, shell=True)

        os.chdir(Cur_PATH)

        # print((U.strbase.footer1.format("Finished the TPXO extract_HC")))

    def runTPXO_predict(self, ):
        logger.info("Start the TPXO predict_tide")

        self.writeTPXOsetup(self.TPXO_setup, self.CaseName)
        self.writeTPXOlatlon(self.TPXO_LL, self.mesh)
        self.writeTPXOtime(self.TPXO_time, self.ptime)

        Cur_PATH = os.getcwd()
        os.chdir(self.TPXO_Path)
        CMD = "./predict_tide -t{:}<{:}".format(self.TPXO_time, self.TPXO_setup)
        p = subprocess.call(CMD, shell=True)

        os.chdir(Cur_PATH)

    def writeTPXOsetup(self, filename, CaseName):
        lines = []

        lines.append("{:20s}  ! 1. tidal model control file\n".format("DATA/Model_tpxo7.2"))
        lines.append("{:20s}  ! 2. latitude/longitude/<time> file\n".format(CaseName + "_TPXOLL.dat"))
        lines.append("{:20s}  ! 3. z/U/V/u/v\n".format("z"))
        lines.append("{:20s}  ! 4. tidal constituents to include\n".format(" "))
        lines.append("{:20s}  ! 5. AP/RIi\n".format("AP"))
        lines.append("{:20s}  ! 6. oce/geo\n".format("geo"))
        lines.append("{:20s}  ! 7. 1/0 correct for minor constituents\n".format("1"))
        lines.append("{:20s}  ! 8. output file (ASCII)\n".format(CaseName + "_obc_elj.out"))

        f = open(filename, 'w')
        f.writelines(lines)
        f.close()

    def writeTPXOtime(self, filename, ptime):

        """
        The TPXO time file:
        2002      3     18      4     29     18
        2002      3     28      2     28     22
        2002      4      7      0     26     43
        2002      5      6     18     21     48
        2002      5     16     16     20     52
        2001      9     18      7     39     51
        2001      9     28      5     38     54
        2001     10      8      3     37     16
        2001     10     18      1     35     38
        2001     10     27     23     33     59
        2002      4     24     11     18     31
        2002      5      4      9     16     53
        2002      5     14      7     15     14
        2002      5     24      5     14     18
        2002      6      3      3     12     39
        """
        f = open(filename, 'w')
        for Date in ptime.Time:
            f.write("{0:<6}{1:<4}{2:<4}{3:<4}{4:<4}{5:<4}\n".format
                    (Date.year, Date.month, Date.day, Date.hour, Date.minute, Date.second))

        # The TPXO predict_tide program will minus the last time,so add one step.
        Date = ptime.Time[-1] + (ptime.Time[-1] - ptime.Time[-2])
        f.write("{0:<6}{1:<4}{2:<4}{3:<4}{4:<4}{5:<4}\n".format
                (Date.year, Date.month, Date.day, Date.hour, Date.minute, Date.second))

        f.close()

    def writeTPXOlatlon(self, filename, mesh):
        obcLL = [mesh.lat[mesh.OBID - 1], mesh.lon[mesh.OBID - 1]]
        write_dat(filename, [], obcLL, ['12.4f', '12.4f'])

    def parseTPXOHC(self, HCfile):
        """
        Read TPXO HC outfile and return the Lat,Lon,HCamp,HCph,HCname
        Example：
            [Lat,Lon,HCamp,HCph,HCname]=parseTPXOHC(inputfile)
        """
        # read all lines to a list
        fHC = open(HCfile, 'r')
        datalist = []
        for line in fHC:
            datalist.append(line.strip().split())
        fHC.close()

        # the 3rd line is the data name:lon lat HCx_amp HCx_ph...
        HCname = [amp_name[0:2].upper() for amp_name in datalist[2][2::2]]

        # other line is the HCdata
        dataarray = np.array(datalist[3:], dtype=float)

        # The 1st column is lat, the 2en column is lon ,others is HCx_amp HCx_ph...
        Lat = dataarray[:, 0]
        Lon = dataarray[:, 1]
        HCamp = dataarray[:, 2::2]
        HCph = dataarray[:, 3::2]

        HC = {}
        HC['name'] = HCname
        HC['amp'] = HCamp
        HC['pha'] = HCph

        return Lat, Lon, HC,

    def parseTPXOelev(self, elevfile):
        """
        Read TPXO elev outfile and return the Lat,Lon,elev,DateTimelist
        --------------------------------------------
        Example：
            [Lat,Lon,elev,DateTimelist]=parseTPXOelev(inputfile)
        --------------------------------------------
        """
        f = open(elevfile)
        Dlist = []
        for line in f:
            Dlist.append(line.strip().split())
        f.close()

        datalist = Dlist[6:]

        Lat = []
        Lon = []
        DateTimelist = []
        elevlist = []
        elevnode = []
        for data in datalist:
            if len(data) == 2:
                Lat.append(data[0])
                Lon.append(data[1])
                if elevnode:
                    elevlist.append(elevnode)
                    DateTimelist = []
                    elevnode = []
            elif len(data) == 4:
                DateTimelist.append([data[0], data[1]])
                elevnode.append(data[2])
            elif len(data) != 2 and len(data) != 4:
                elevlist.append(elevnode)
                elevnode = []
                for itime in range(len(self.ptime.Time)):
                    elevnode.append(0)
                # print("***** Your elev data has bugs! *****")
        # For the last node, there is no (if len(data)==2) to append data. so add a append.
        elevlist.append(elevnode)
        Lat = np.array(Lat, dtype=float)
        Lon = np.array(Lon, dtype=float)
        elev = np.transpose(np.array(elevlist, dtype=float))
        return Lat, Lon, elev, DateTimelist


