# -*- coding: utf-8 -*-
"""
Fiopy -- File in & out python functions

write_dat
parse_dat
read_dat
parse_bathymetry_xyz


2015/2/24 add write_dat
            write_dat(Datfile,Header,Data,Dataformat):
2015/3/15 add parse_dat
            parse_dat(adatfile)
2015/3/16 add read_dat
            read_dat(datafile,HeaderNum=0):
          a simple read function just for read numbers,add support for skip headerlines
2015/3/20 add parse_bathymetry_xyz
            parse_bathymetry_xyz(datafile,HeaderNum=0):
          read the coastlines data in xyz format from GEODAS
"""

from ._Basic_IO import write_dat
from ._Basic_IO import writedat_V2
from ._Basic_IO import writedat
from ._Basic_IO import writedata

from ._Basic_IO import parsedat
from ._Basic_IO import read_dat
from ._Basic_IO import read_dat2list
