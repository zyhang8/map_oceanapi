# -*- coding: utf-8 -*-
"""
Created on Sun Jun 28 23:20:12 2015

@author: ban
"""

import os
import numpy as np


# --------------------------------------------------------------------------------------
#    Write ASCII file functions
# --------------------------------------------------------------------------------------

def write_dat(Datfile, Header, Data, Dataformat):
    """
    a simple program for write ASCII (.dat) file.
   
        -------------------------------------------
        write_dat Man:
            write_dat(Datfile,Header,Data,Dataformat)
            
            Input  :
            Output : 
            
        --------------------------------------------
        Example：
            write_dat(Datfile,Header,Data,Dataformat)
            Data=[Times,dep,sid0,sid2]
            Format=['20s','8.3f','8.3f','8.3f']

        --------------------------------------------
        Author : 
            安佰超 (anbaichao@gmail.com)
            
        --------------------------------------------
        History:
          Version 3         2015/2/24
          Version 2         2014/12/12
          Version 1         2014/ 
        
        --------------------------------------------
    """

    # ========================================================================
    # open the file
    f = open(Datfile, 'w')

    # ========================================================================
    #  write the headerlines
    # =============================
    # Algorithm
    # ********************************************************
    # *The headerlines are always strs,
    # *so if headerlines is not empty, write them line by line
    # ********************************************************
    if Header:
        for i in Header:
            f.write(i)

    # ========================================================================
    #  Write the data
    # =============================
    # Algorithm
    # ************************************************************************
    # *The Data col always has the same format and has the same properties.
    # *So arrange the data in a list, which can contain different datatype,
    # *just like :
    # *   Data=[Times,dep,sid0,sid2],Format=['20s','8.3f','8.3f','8.3f']
    # *And write the data by row.
    # ************************************************************************
    # The j is the index of row , which may be the time series.
    # The i is the index of col ,which may be the number of the element.
    # write data row by row
    for j in range(len(Data[1])):
        Form_str = ''
        # range one row in one Form_str, by the Format
        for i in range(len(Dataformat)):
            # form the str's format
            Strform = "{:>" + Dataformat[i] + "}"
            Form_str = Form_str + Strform.format(Data[i][j])
        f.write(Form_str + '\n')
    # ========================================================================
    # Close the file and give the success signal.
    f.close()


"""
-----------------------------------------------------------
writedat_v2.py

Created on Wed Nov 12 02:57:06 2014

@author: AnBC
-----------------------------------------------------------
"""


def writedat_V2(filename, datalist, dataformat, header=[]):
    # open the file
    f = open(filename, 'w')

    # write the headerlines
    # if header is not empty, write them line by line
    if header:
        for i in header:
            f.write(i)

    for j, data in enumerate(datalist):
        for k in range(len(datalist[j])):
            strfor = "{:>" + dataformat[j] + "}"
            str_format = strfor.format
            f.write(''.join(map(str_format, datalist[j][k, :])) + '\n')
    f.close()
    print((filename + " has been creadted successfully!"))


#    str_format= "{:>10.3f}".format
#    f_out.write(' '.join(map(str_format,HCamp[iout,:]))+'\n')
#    f_out.write(' '.join(map(str_format,HCph[iout,:]))+'\n')

"""
------------------------------------------------------------
writedat_v1.py

Created on Fri Sep 13 13:18:35 2014

@author: anbc
------------------------------------------------------------
"""


def writedat(filename, datalist, dataformat=[], header=[]):
    f = open(filename, 'w')

    if header:
        for i in header:
            f.write(i)

    if dataformat:
        if isinstance(dataformat, str):
            np.savetxt(f, datalist, dataformat)
        else:
            for j, data in enumerate(datalist):
                np.savetxt(f, data, dataformat[j])

    else:
        np.savetxt(f, datalist)

    f.close()


def writedata(filename, data):
    f = open(filename, 'w')
    for i in data:
        f.write('  '.join(i) + '\n')
    f.close()


def parsedat(adatfile):
    """
    -------------------------------------------
    parse_dat
    -------------------------------------------
    Usage:
    for parse standerd dat file but now not finish
    
    Input:

    Output:

    --------------------------------------------
    Example：
    [data,header]=parse_dat(adatfile)
    --------------------------------------------
    
    --------------------------------------------
    History:
    --------------------------------------------
    Version: V3.0  2015/4/5
        change the header as dict.    
    Version: V2.0  2015/3/15
        support the header element is empty.
    Version: V1.0  2014/10/6

    Author : 安佰超 (anbaichao@gmail.com)
    --------------------------------------------
    """
    # ==============================================================================

    # ------------------------------------------------------------------------------
    # open the SBE CTDfile and read all lines
    f = open(adatfile, 'r')
    Dlines = f.readlines()
    f.close()

    # ------------------------------------------------------------------------------
    # arange the Dlines
    dataflag = 0
    headerline = []
    datalist = []
    # put in data list and header list
    for line in Dlines:
        # data line
        if dataflag == 1:
            datalist.append(line.strip().split())
        # header line
        elif dataflag == 0:
            headerline.append(line)
        # if this line find *END*,the next line is the data start.
        if line.find('* END *') != -1:
            dataflag = 1

    # datalist to np.array
    data = np.asarray(datalist)

    return [data, headerline]


# import numpy as np

def read_dat(datafile, HeaderNum=0):
    """
    a simple read function just for read numbers 
    add support for skip headerlines
    
    Version 0.2   2015/3/25
        add read the headerline
    Version 0.1   2015/3/16
    anbaichao@gmail.com
    """

    f = open(datafile, 'r')
    lines = f.readlines()
    f.close()

    headlist = []
    for line in lines[0:HeaderNum]:
        headlist.append(line.strip().split())

    datalist = []
    for line in lines[HeaderNum:]:
        # using if to del the empty list
        if line.strip().split():
            datalist.append(line.strip().split())
    #    print datalist
    data = np.asarray(datalist, dtype=float)

    return data, headlist


def read_dat2list(datafile, HeaderNum=0):
    """
    a simple read function just for read numbers 
    add support for skip headerlines
    
    Version 0.1   2015/3/25
        midify the read_dat to this function
        for the data file which element number in lines is different. 

    anbaichao@gmail.com
    """

    f = open(datafile, 'r')
    lines = f.readlines()
    f.close()

    headlist = []
    for line in lines[0:HeaderNum]:
        headlist.append(line.strip().split())

    datalist = []
    for line in lines[HeaderNum:]:
        # using if to del the empty list
        if line.strip().split():
            datalist.append(line.strip().split())
    #    print datalist

    return datalist, headlist
