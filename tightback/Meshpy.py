# -*- coding: utf-8 -*-
"""
Class for Model mesh.
---------------------------------------------
CLASS_VAR:
    
---------------------------------------------
CLASS_METHOD:
    
    __init__
    write_XY
    replace_XY
    replace_dep
    readGrid
    writeGrid
---------------------------------------------
History:
    
    Version 0.6  2016/12/12 23:31:00
        add method Nesting_grids and child class Nesting_mesh, \\
        thus Nesting_mesh can be used as a Mesh object in some place, \\
        just like write_FVCOM_ncDIM and write_FVCOM_ncgrid, and so on.
    
    Version 0.5  2015/10/28
        add gen_sides gen_edge. 
        
    Version 0.4   2015/10/14
        add flag FMT for node nele xc yc lonc latc nv var or not.

    Version 0.3   2015/4/9
        add the node nele xc yc lonc latc nv var
        add the nodes2elems method
        
    Version 0.2   2015/3/26
        add the screen display
        
    Version 0.1   2015/3/16
---------------------------------------------
Author:
    
    AN BAICHAO            
    anbaichao@gmail.com
---------------------------------------------
"""

# ------------------------------------------------------------------------------
#   Import 
# -------------------------
import os
import sys
import numpy as np
from utils.Fiopy import writedat, write_dat
from netCDF4 import Dataset
from matplotlib import pylab as plt


class Mesh:
    """
    A Class for Model mesh.
    
    """

    def __init__(self, inputfile, FMT='norm'):
        outnc_file = inputfile[0:-4] + ".nc"
        # do not use nc file by 'XXXX'
        if os.path.isfile(outnc_file+'XXXX'):
            self.load_mesh_nc(outnc_file)

        else:
            self.file = inputfile
            (ED, ND, OBID) = self.readGrid()

            self.ED = ED
            self.ND_init = ND
            self.ND = ND
            self.OBID = OBID

            self.node = len(ND)
            self.nele = len(ED)
            self.NDID = np.asarray(self.ND[:, 1], dtype=int)
            self.EDID = np.asarray(self.ED[:, 1], dtype=int)

            self.x = np.asarray(self.ND[:, 2], dtype=float)
            self.y = np.asarray(self.ND[:, 3], dtype=float)
            # if not use latlon , you should modify the lat lon
            self.lon = np.asarray(self.ND[:, 2], dtype=float)
            self.lat = np.asarray(self.ND[:, 3], dtype=float)
            self.h = np.asarray(self.ND[:, 4], dtype=float)

            self.nobc = len(self.OBID)
            self.OBC_h = self.h[self.OBID - 1]
            self.OBC_lat = self.lat[self.OBID - 1]
            self.OBC_lon = self.lon[self.OBID - 1]

            if FMT == "norm":
                # tri is node index in python format(nv-1)
                self.tri = np.asarray(self.ED[:, 2:5], dtype=int) - 1

                # nv is the node id surrounding elem
                self.nv = np.asarray(self.ED[:, 2:5], dtype=int)

                self.xc = self.N2E2D(self.x)
                self.yc = self.N2E2D(self.y)
                self.lonc = self.N2E2D(self.lon)
                self.latc = self.N2E2D(self.lat)

                self.h_center = self.N2E2D(self.h)

                self.lon_lim = [np.floor(np.min(self.lon)), np.ceil(np.max(self.lon))]
                self.lat_lim = [np.floor(np.min(self.lat)), np.ceil(np.max(self.lat))]
                self.r = (self.lat_lim[1] - self.lat_lim[0]) / (self.lon_lim[1] - self.lon_lim[0])

                # self.Neighbor()
                #
                #
                # self.save_mesh_nc(outnc_file)

                # now not in nc format mesh. !!!!!
            #            self.gen_sides()
            #            self.gen_edge()


    def N2E2D(self, field):

        # This method is not supporting luanxu
        field_list = [np.sum(field[itri[0:3]]) / 3.0 for itri in self.tri]
        field_out = np.asarray(field_list, dtype=float)

        return field_out

    def Neighbor(self, ):

        NVNB = np.zeros((self.node, 10), dtype=int)
        NTNB = np.zeros(self.node)

        for i in range(self.node):

            nNB = 0

            for j in range(3):
                jNVBH = self.EDID[self.nv[:, j] - self.NDID[i] == 0]

                for kNVBH in jNVBH:
                    NVNB[i, nNB] = kNVBH
                    nNB = nNB + 1

            NTNB[i] = nNB

        self.EV = NVNB
        self.nEV = NTNB

    def E2N2D(self, field):

        field_out = np.empty(self.node)
        for i in range(self.node):
            field_out[i] = np.sum(field[self.EV[i, 0:self.nEV[i]] - 1]) / self.nEV[i]

        return field_out

    class Nesting_mesh:
        pass

    def Nesting_grids(self, Nesting_node_id, Test=False):
        # ------------------------------------------------------------------------------
        # Gen the Nesting grids
        # --------------------------------------

        Elem_Nest_Number = 0
        nv_Nest_list = []
        EDID_list = []
        for iele in range(self.nele):
            if np.any(Nesting_node_id == self.nv[iele, 0]):
                if np.any(Nesting_node_id == self.nv[iele, 1]) and np.any(Nesting_node_id == self.nv[iele, 2]):
                    Elem_Nest_Number = Elem_Nest_Number + 1
                    nv_Nest_list.append(self.nv[iele])
                    EDID_list.append(iele + 1)

        self.Nesting_node = Nesting_node_id
        self.Nesting_elem = np.asarray(EDID_list, dtype=int)
        self.Nesting_nv = np.asarray(nv_Nest_list, dtype=int)

        self.Nesting_mesh.x = self.x[self.Nesting_node - 1]
        self.Nesting_mesh.y = self.y[self.Nesting_node - 1]
        self.Nesting_mesh.lon = self.lon[self.Nesting_node - 1]
        self.Nesting_mesh.lat = self.lat[self.Nesting_node - 1]

        self.Nesting_mesh.xc = self.xc[self.Nesting_elem - 1]
        self.Nesting_mesh.yc = self.yc[self.Nesting_elem - 1]
        self.Nesting_mesh.lonc = self.lonc[self.Nesting_elem - 1]
        self.Nesting_mesh.latc = self.latc[self.Nesting_elem - 1]

        self.Nesting_mesh.node = len(self.Nesting_node)
        self.Nesting_mesh.nele = len(self.Nesting_elem)
        self.Nesting_mesh.NDID = self.Nesting_node
        self.Nesting_mesh.EDID = self.Nesting_elem

        self.Nesting_mesh.nv = self.Nesting_nv

        self.Nesting_mesh.h = self.h[self.Nesting_node - 1]
        self.Nesting_mesh.h_center = self.h_center[self.Nesting_elem - 1]

        # Test the nesting grids
        if Test:
            for nv in self.Nesting_nv:
                plt.plot([self.lon[nv[0] - 1], self.lon[nv[1] - 1], self.lon[nv[2] - 1], self.lon[nv[0] - 1]], \
                         [self.lat[nv[0] - 1], self.lat[nv[1] - 1], self.lat[nv[2] - 1], self.lat[nv[0] - 1]], 'b-')

    def gen_sides(self, ):
        """
        """

        # change the mesh to lines array.
        lines1 = np.vstack((self.tri[:, 0:2], self.tri[:, 1:], self.tri[:, 0::2]))

        # sort each row from small t big.
        lines = np.sort(lines1)

        # change it to struct with .view . I do not kown it clearly.
        b = np.ascontiguousarray(lines).view(np.dtype((np.void, lines.dtype.itemsize * lines.shape[1])))

        # unique
        c, idx, icnt = np.unique(b, return_index=True, return_counts=True)

        # change it to origin shape.
        lines_unique = lines[idx]

        self.sides = lines_unique
        self.nodes_edge = lines_unique[icnt == 1]

    def gen_edge(self, ):
        # **************************** The Var List ******************************************
        # edge       : an array contain the node_id,two column for two node_id. At this def it changes.
        # nedge      : the edge length.
        # idx_edge   : An array contain the edge row id
        # bool_edge  : An boolean array for edge, shape(nedge).for delete row that used
        # node_start : The start node in each boundary,for check the boundary closed node. change in each init.
        # node_next  : The node to find, it will be change to the node to find in each loop or init
        # node_line  : The row number which is current node_next in.
        # bdy        : A list for boundaries
        # ibdy       : An array for one boundary.
        # nbdy       : The number of boundaries.
        # flag       : The flag for if end loop or not.
        # nline_tmp  : tmp Var.
        # nline_tmp2 : tmp_Var
        # ************************************************************************************


        # ------------------------ The first init for the first coastline -----------------------
        # init oprate for each coastline
        # 1. init the edge nedge idx_edge bool_edge :as the edge for each coastline is different.
        # 2. node_line init : the line number for node in edge
        # 3. get the node_start : for confirming the closed node
        # 4. get the node_next : for find the next node.
        # 5. store the node_start and node_next in iby
        # 6. delete the first node_line that used in edge
        edge = self.nodes_edge
        nedge = edge.shape[0]
        idx_edge = np.arange(nedge)
        bool_edge = np.ones(nedge, dtype=bool)

        node_line = 0
        node_start = edge[node_line, 0]
        node_next = edge[node_line, 1]
        bool_edge[node_line] = 0
        print((node_line, node_start, node_next))

        ibdy = []
        ibdy.append(node_start)
        ibdy.append(node_next)

        # ------------------------ The loop for finding node_next in the coastline -----------------
        # 1. init data for loop :
        #   (1) bdy  - a list for all coastlines.
        #   (2) nbdy - the counts of coastlines(boundaries)
        #   (3) flag - indicate the loop end.
        #
        # 2. find the the node_next.
        # (1)
        #   The edge must have 2 node_next, one is in the current node_line,
        #   the other is in another row ,which is the node_line we hope to find.
        #   the edge have only 2 column, so the other node in the node_line(hode) is the node_next.
        #   so have to know the current node_next in which column.
        #  for cases:
        #   1. the current node_next one in the first column,the other in the second column.
        #   2. the 2 current node_next both are in the first column
        #   3. the 2 current node_next both are in the second column
        # 3. append it to ibdy
        # 4. Delete the node_line in bool_edge
        # 5. confirm if it is the closed node.
        bdy = []
        nbdy = 0
        flag = 1

        while flag == 1:

            nline_tmp = idx_edge[edge[:, 0] == node_next]
            nline_tmp2 = idx_edge[edge[:, 1] == node_next]

            if nline_tmp.size == 1 and nline_tmp2.size == 1:
                if nline_tmp != node_line:
                    node_line = nline_tmp
                    node_next = edge[node_line, 1][0]
                elif nline_tmp2 != node_line:
                    node_line = nline_tmp2
                    node_next = edge[node_line, 0][0]
            elif nline_tmp.size == 2 and nline_tmp2.size == 0:
                node_line = nline_tmp[nline_tmp != node_line]
                node_next = edge[node_line, 1][0]

            elif nline_tmp.size == 0 and nline_tmp2.size == 2:
                node_line = nline_tmp2[nline_tmp2 != node_line]
                node_next = edge[node_line, 0][0]

            ibdy.append(node_next)

            print((node_line, node_next))

            # Delete the node_line that used in edge.
            # Note: this node_line is not the start node_line.
            #      It is the other node_line contain the start node.
            bool_edge[node_line] = 0

            # ------------------------ Confirm the closed node -------------------
            # confirm if the node is the closed node of one coastline.
            # if true,
            # 1. count nbdy and append idby to bdy
            # 2. and init the next coastline.
            if node_next == node_start:
                print("end one boundary")
                nbdy = nbdy + 1
                bdy.append(ibdy)

                # for closed node(node_next==node_start),there are two case: 
                # 1. is the coastline end but not the nodes end
                # 2. is the coastline end and the nodes end.
                if bool_edge.any():
                    # init oprate for each coastline
                    # 1. init the edge nedge idx_edge bool_edge :as the edge for each coastline is different.
                    # 2. node_line init : the line number for node in edge
                    # 3. get the node_start : for confirming the closed node
                    # 4. get the node_next : for find the next node.
                    # 5. store the node_start and node_next in iby
                    # 6. delete the first node_line that used in edge
                    edge = edge[bool_edge, :]
                    nedge = edge.shape[0]
                    idx_edge = np.arange(nedge)
                    bool_edge = np.ones(nedge, dtype=bool)

                    node_line = 0
                    node_start = edge[node_line, 0]
                    node_next = edge[node_line, 1]
                    bool_edge[node_line] = 0
                    print((node_line, node_start, node_next))

                    ibdy = []
                    ibdy.append(node_start)
                    ibdy.append(node_next)
                elif not bool_edge.any():
                    flag = 0

        self.edge = bdy

    def save_mesh_nc(self, outfile):
        ncfile = Dataset(outfile, 'w')

        ncfile.createDimension('node', self.node)
        ncfile.createDimension('nele', self.nele)
        ncfile.createDimension('three', 3)
        ncfile.createDimension('five', 5)
        ncfile.createDimension('six', 6)
        ncfile.createDimension('ten', 10)
        ncfile.createDimension('DateStrLen', 26)
        ncfile.createDimension('nobc', len(self.OBID))

        # ---------------------------- mesh axis --------------------------
        Var_x = ncfile.createVariable('x', 'f', ('node',))
        Var_x.long_name = "nodal x-coordinate"
        Var_x.units = "meters"
        Var_x[:] = self.x

        Var_y = ncfile.createVariable('y', 'f', ('node',))
        Var_y.long_name = "nodal y-coordinate"
        Var_y.units = "meters"
        Var_y[:] = self.y

        Var_lon = ncfile.createVariable('lon', 'f', ('node',))
        Var_lon.long_name = "nodal lontitude"
        Var_lon.units = "degree_east"
        Var_lon[:] = self.lon

        Var_lat = ncfile.createVariable('lat', 'f', ('node'))
        Var_lat.long_name = "nodal latitude"
        Var_lat.units = "degree_north"
        Var_lat[:] = self.lat

        Var_xc = ncfile.createVariable('xc', 'f', ('nele',))
        Var_xc.long_name = "zonal x-coordinate"
        Var_xc.units = "meters"
        Var_xc[:] = self.xc

        Var_yc = ncfile.createVariable('yc', 'f', ('nele',))
        Var_yc.long_name = "zonal y-coordinate"
        Var_yc.units = "meters"
        Var_yc[:] = self.yc

        Var_lonc = ncfile.createVariable('lonc', 'f', ('nele',))
        Var_lonc.long_name = "zonal longitude"
        Var_lonc.units = "degree_east"
        Var_lonc[:] = self.lonc

        Var_latc = ncfile.createVariable('latc', 'f', ('nele',))
        Var_latc.long_name = "zonal latitude"
        Var_latc.units = "degree_north"
        Var_latc[:] = self.latc

        # ---------------------------- mesh axis --------------------------
        Var_ED = ncfile.createVariable('ED', 'S10', ('nele', 'six'))
        Var_ED.long_name = "ED"
        Var_ED[:] = self.ED

        Var_ND = ncfile.createVariable('ND', 'S10', ('node', 'five'))
        Var_ND.long_name = "ND"
        Var_ND[:] = self.ND

        Var_NDID = ncfile.createVariable('NDID', 'i', ('node',))
        Var_NDID.long_name = "NDID"
        Var_NDID[:] = self.NDID

        Var_EDID = ncfile.createVariable('EDID', 'i', ('nele',))
        Var_EDID.long_name = "EDID"
        Var_EDID[:] = self.EDID

        Var_nv = ncfile.createVariable('nv', 'i', ('nele', 'three'))
        Var_nv.long_name = "nodes surrounding element,index"
        Var_nv[:] = self.nv

        Var_tri = ncfile.createVariable('tri', 'i', ('nele', 'three'))
        Var_tri.long_name = "nodes surrounding element, python index"
        Var_tri[:] = self.tri

        Var_EV = ncfile.createVariable('EV', 'i', ('node', 'ten',))
        Var_EV.long_name = "elements surrounding node,index"
        Var_EV[:] = self.EV

        Var_nEV = ncfile.createVariable('nEV', 'i', ('node',))
        Var_nEV.long_name = "elements surrounding node,index number"
        Var_nEV[:] = self.nEV

        # ---------------------------- mesh depth --------------------------
        Var_h = ncfile.createVariable('h', 'f', ('node',))
        Var_h.long_name = "Bathymetry"
        Var_h.standard_name = "sea_floor_depth_below_geoid"
        Var_h.units = "m"
        Var_h.positive = "down"
        Var_h.grid = "Bathymetry_Mesh"
        Var_h.coordinates = "lat lon"
        Var_h.type = "data"
        Var_h[:] = self.h

        # ---------------------------- mesh obs --------------------------

        Var_OBID = ncfile.createVariable('OBID', 'i', ('nobc',))
        Var_OBID.long_name = "OBID"
        Var_OBID[:] = self.OBID

        Var_OBC_lat = ncfile.createVariable('OBC_lat', 'f', ('nobc'))
        Var_OBC_lat.long_name = "Obc nodal latitude"
        Var_OBC_lat.units = "degree_north"
        Var_OBC_lat[:] = self.OBC_lat

        Var_OBC_lon = ncfile.createVariable('OBC_lon', 'f', ('nobc'))
        Var_OBC_lon.long_name = "Obc nodal latitude"
        Var_OBC_lon.units = "degree_north"
        Var_OBC_lon[:] = self.OBC_lon

        Var_obc_h = ncfile.createVariable('obc_h', 'f', ('nobc',))
        Var_obc_h.long_name = "open boundary depth"
        Var_obc_h.grid = "obc_grid"
        Var_obc_h[:] = self.OBC_h

        ncfile.close()

    def load_mesh_nc(self, outfile):
        ncf = Dataset(outfile, 'r')

        self.ED = ncf.variables['ED'][:]
        self.ND = ncf.variables['ND'][:]

        self.node = len(self.ND)
        self.nele = len(self.ED)
        self.NDID = ncf.variables['NDID'][:]
        self.EDID = ncf.variables['EDID'][:]
        self.tri = ncf.variables['tri'][:]
        self.nv = ncf.variables['nv'][:]
        self.EV = ncf.variables['EV'][:]
        self.nEV = ncf.variables['nEV'][:]

        self.x = ncf.variables['x'][:]
        self.y = ncf.variables['y'][:]
        # if not use latlon , you should modify the lat lon
        self.lon = ncf.variables['lon'][:]
        self.lat = ncf.variables['lat'][:]
        self.xc = ncf.variables['xc'][:]
        self.yc = ncf.variables['yc'][:]
        self.lonc = ncf.variables['lonc'][:]
        self.latc = ncf.variables['latc'][:]

        self.h = ncf.variables['h'][:]

        self.OBID = ncf.variables['OBID'][:]
        self.OBC_h = ncf.variables['obc_h'][:]
        self.OBC_lat = ncf.variables['OBC_lat'][:]
        self.OBC_lon = ncf.variables['OBC_lon'][:]

        self.lon_lim = [np.floor(np.min(self.lon)), np.ceil(np.max(self.lon))]
        self.lat_lim = [np.floor(np.min(self.lat)), np.ceil(np.max(self.lat))]
        self.r = (self.lat_lim[1] - self.lat_lim[0]) / (self.lon_lim[1] - self.lon_lim[0])

        ncf.close()

    def write_XY(self, XYfile, depth=0, Header=[]):
        if depth == 0:
            Data = [self.X, self.Y]
            Dataformat = ['20.2f', '20.2f']
        elif depth == 1:
            Data = [self.X, self.Y, self.Depth]
            Dataformat = ['20.2f', '20.2f', '8.2f']

        write_dat(XYfile, Header, Data, Dataformat)

    def replace_XY(self, X_new, Y_new):
        self.ND = np.dstack((self.ND[:, 0], self.ND[:, 1], X_new, Y_new, self.ND[:, 4]))[0]
        self.X = np.asarray(self.ND[:, 2], dtype=float)
        self.Y = np.asarray(self.ND[:, 3], dtype=float)

    def replace_dep(self, depth_new):
        self.ND = np.dstack((self.ND[:, 0], self.ND[:, 1], self.ND[:, 2], self.ND[:, 3], depth_new))[0]
        self.Depth = np.asarray(self.ND[:, 4], dtype=float)

    def readGrid(self, ):
        inputfile = self.file
        if inputfile[-4:] == '.2dm':
            [ED, ND, OBID] = self.readGridSMS()

        elif inputfile[-8:] == '_grd.dat':
            [ED, ND, OBID] = self.readGridFVCOM()

        elif inputfile[-5:] == '.mesh':
            [ED, ND, OBID] = self.readGridMIKE()
        else:
            print("uncognized format!")
            ED = []
            ND = []
            OBID = []
        #        print ND
        return (ED, ND, OBID)

    def writeGrid(self, outfile, casename='Ban'):
        """
        writeGridSMS(self,twodmfile)
        
        writeGridFVCOM(self,filename)
        
        writeGooglekml(self,outpath,kmlname="cjk_grids",name = 'ge_tri',description = '',
             lineColor = 'FFFFFF00',polyColor = '40ff833e',lineWidth = 1.0)
        """
        ED = self.ED
        ND = self.ND
        OBID = self.OBID

        if outfile[-4:] == '.2dm':
            writeGridSMS(ED, ND, OBID, outfile)
        elif outfile[-8:] == '_grd.dat':
            self.writeGridFVCOM(ED, ND, OBID, outfile, casename)
        elif outfile[-4:] == '.kml':
            self.writeGooglekml(ED, ND, outfile)
        else:
            print((outfile + ' : ' + 'can not recognized!'))


    # In[1] ######################  readGridSMS  #################################
    def readGridSMS(self):
        """
        Read GridSMS(.2dm) file and return the ED,ND,OBID.
        
            -------------------------------------------
            readGridSMS Man:
                Usage : read GridSMS(.2dm) file
            
                Input : The  GridSMS(.2dm) filepath
                
                Output : will return ED ND OBID(array(str))
                
            --------------------------------------------
            Example：
                [ED,ND,OBID]=readGridSMS(inputfile)
    
            --------------------------------------------
            Author : 
                安佰超 (anbaichao@gmail.com)
                
            --------------------------------------------
            History:
                Version V3.0: 2014/11/19 
                    change the result ED,ND,OBID to np.array.
                    delete the NDtype,for it is not used.
                Version V2.0: 2014/9/29 
                    change the prosess
                Version V1.0: 2014/9/9
                    establish this function.
            
            --------------------------------------------
        """
        # ==============================================================================
        #        print("\n")
        print("-----  Reading SMS '.2dm' file ... -----")
        inputfile = self.file
        f = open(inputfile, "r")
        Dlines = f.readlines()
        f.close()

        ##Init the data container:
        # triangles data:ED,node data:ND,open boundary data ID:OBID,
        EDlist = []
        NDlist = []
        OBIDlist = []

        for line in Dlines:
            line = line.strip()

            # ------------------------------------------------
            #  startwith 'E3T' is the ED data:the triangles
            # ------------------------------------------------
            if line.startswith('E3T'):
                EDlist.append(line.split())

            # ------------------------------------------------
            # startwith "ND" is the ND data: the nodes
            # ------------------------------------------------
            elif line.startswith('ND'):
                NDlist.append(line.split())

            # ------------------------------------------------
            # startwith "NS" is the open boudary data ID
            # ------------------------------------------------
            elif line.startswith('NS'):
                OBlinedata = line.split()
                for nodeID in OBlinedata[1:]:  # 0 is 'NS'
                    OBIDlist.append(nodeID)

        # -------------------------------------------------
        # arange to np.array
        # -------------------------------------------------
        ED = np.array(EDlist)
        ND = np.array(NDlist)
        OBID = np.array(OBIDlist, dtype=int)

        print("-----  SMS '.2dm' file has been read successfully! -----")
        print(("-----  PATH: " + inputfile + "  -----" + '\n'))

        return (ED, ND, OBID)
        ############################# End readGridSMS #################################

    # In[2]
    ############################ readGridFVCOM #####################################
    def readGridFVCOM(self, ):
        """
        Read GridFVCOM(_grd.dat,_dep.dat) file and return the ED,ND,OBID.
            Usage:
        you must have _grd.dat _dep.dat _obc.dat files
        read FVCOM mesh file:grd.dat dep.dat obc.dat
            -------------------------------------------
            readGridSMS Man:
                Usage : read GridFVCOM(_grd.dat) file.
            
                Input : The  GridFVCOM(_grd.dat) filepath
                        The FVCOM grid version, Now support V2&V3.
                
                Output : will return ED ND OBID(array(str)).
                
            --------------------------------------------
            Example：
                [ED,ND,OBID]=readGridFVCOM(inputfile,version)
    
            --------------------------------------------
            Author : 
                安佰超 (anbaichao@gmail.com)
                
            --------------------------------------------
            History:
                Version V4.0  2015/4/6
                    auto judge the FVCOM grid version.
                Version V3.0  2015/3/12
                    add the suport for FVCOM grid version 2.
                Version V2.0: 2014/11/19 
                    change the result ED,ND,OBID to np.array.
                    add the OBID(need '_obc.dat')
                Version V1.0: 2014/9/24
                    establish this function.
            
            --------------------------------------------
        """

        # ==============================================================================
        # grdfile='E:/Models.WS/CHY_FVCOM/cjk_grd.dat'
        grdfile = self.file
        depfile = grdfile[0:-7] + 'dep.dat'
        obcfile = grdfile[0:-7] + 'obc.dat'

        # read the "_grd.dat" file
        f = open(grdfile, 'r')
        Dlines = f.readlines()
        f.close()

        # read the "_dep.dat" file
        DepData = self.read_dep(depfile)
        Depnum = len(DepData)
        # -----------------------------------------
        # range the ED,ND,OBID in 2D-np.array
        # -----------------------------------------
        if Dlines[0].find('=') != -1:
            print("  The FVCOM grid file version is V3 !!!")
            NDnum = int(Dlines[0].strip().split('=')[1])
            EDnum = int(Dlines[1].strip().split('=')[1])
            #            Depnum=int(Deplines[0].strip().split('=')[1])
            # Check the file
            #            if Depnum!=NDnum:
            #                print "Error: The '_grd.dat' file NDnum and '_dep.dat' file Depnum are not equal!"
            #                sys.exit()
            if (NDnum + EDnum + 2) != len(Dlines):
                print("Error: The '_grd.dat' file 'Node Number' or 'Cell Number' is not match the file lines!")
                sys.exit()
            #            if (Depnum+1)!=len(Deplines):
            #                print "Error: The '_dep.dat' file 'Node Number' is not match the file lines!"
            #                sys.exit()

            EDlist = []
            for i in range(2, EDnum + 2):
                EDline = Dlines[i].strip().split()
                EDlist.append(['E3T '] + EDline)

            NDlist = []
            for j in range(EDnum + 2, EDnum + NDnum + 2):
                NDline = Dlines[j].strip().split()[0:3]
                NDlist.append(['ND '] + NDline + [DepData[j - EDnum - 2]])

            OBID, OBtype = self.read_obc(obcfile)

        else:
            print("  The FVCOM grid file version is V2 !!!")

            fobc = open(obcfile, 'r')
            obclines = fobc.readlines()
            fobc.close()

            NDnum = Depnum
            EDnum = len(Dlines) - NDnum
            obcnum = len(obclines) - 1

            #
            EDlist = []
            for i in range(EDnum):
                EDline = Dlines[i].strip().split()
                EDlist.append(['E3T '] + EDline)
            #
            NDlist = []
            for j in range(EDnum, EDnum + NDnum):
                NDline = Dlines[j].strip().split()[0:3]
                NDlist.append(['ND '] + NDline + [DepData[j - EDnum]])
            #
            OBIDlist = []
            for k in range(1, obcnum + 1):
                OBIDlist.append(obclines[k].strip().split()[1])
            OBID = np.array(OBIDlist, dtype=int)

        # to np.array
        ED = np.array(EDlist)
        ND = np.array(NDlist)

        print("  FVCOM '_grd,_dep,_obc' file has been read successfully!  ")
        print(("  PATH: " + grdfile))
        return (ED, ND, OBID)

    ############################ End readGridFVCOM ################################
    def read_dep(self, depfile):
        fdep = open(depfile, 'r')
        Deplines = fdep.readlines()
        fdep.close()

        if Deplines[0].find('=') != -1:
            # print("  The FVCOM grid file (dep) version is V3 !!!")
            Depnum = int(Deplines[0].strip().split('=')[1])
            Deplines = Deplines[1:]
        else:
            Depnum = len(Deplines)

        DepData = np.empty(Depnum)
        for i in range(Depnum):
            DepData[i] = Deplines[i].strip().split()[2]

        return DepData

    def read_obc(self, obcfile):
        """
        ban 2015/4/16
        Build this function for more error condition (as fvcom source).
        But just for FVCOM V3
        
        see:
        FVCOM mod_input.F
        SUBROUTINE READ_COLDSTART_OBC_GRID(OBCUNIT,MGL,IOBCN_GL,I_OBC_GL, TYPE_OBC_GL)
        
        """
        # ----------------------------------------------
        # open and read the "_obc.dat" file
        fobc = open(obcfile, 'r')
        obclines = fobc.readlines()
        fobc.close()

        # ----------------------------------------------
        # range the obc data

        # the first line has obc_number
        obcnum = int(obclines[0].strip().split('=')[1])

        # Check if the obc_number and data lines is match.
        if (obcnum + 1) != len(obclines):
            print("Error: The '_obc.dat' file 'OBC Node Number' is not match the file data lines!")
            sys.exit()

        OBIDlist = []
        OBtypelist = []
        for k in range(1, obcnum + 1):
            if len(obclines[k].strip().split()) != 3:
                print("Error: The obc.dat file has wrong format data , the data is not 3 class !")

            OBID = int(obclines[k].strip().split()[1])
            if OBID < 1:
                print("Error: The OBC_Node_ID is wrong (<1) !")

            OBtype = int(obclines[k].strip().split()[2])
            if OBtype < 1 and OBtype > 10:
                print("Error: The OBC_Node_type is wrong ,It is must be greater than 0 and less than 11!")

            OBIDlist.append(OBID)
            OBtypelist.append(OBtype)

        # to np.array

        OBIDarray = np.array(OBIDlist, dtype=int)
        OBtypearray = np.array(OBtypelist, dtype=int)

        print("  FVCOM '_obc' file has been read successfully!  ")
        print(("  PATH: " + obcfile))
        return (OBIDarray, OBtypearray)

    # In[3]
    ############################ readGridMIKE ######################################
    def readGridMIKE(self):
        print('The mesh file Wkt header:')
        print("""PROJCS["WGS_1984_GuassKruger_CM_123E",
          GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],
            PRIMEM["Greenwich",0.0],UNIT["Degree",0.017453292519943295]],
        PROJECTION["Gauss_Kruger"],
        PARAMETER["False_Easting",500000.0],
        PARAMETER["False_Northing",0.0],
        PARAMETER["Central_Meridian",123.0],
        PARAMETER["Scale_Factor",1.0],
        PARAMETER["Latitude_Of_Origin",0.0],
        UNIT["Meter",1.0]] """)

        import pyproj
        # ------------------------------------------------------------------------------
        ###Modules Setting
        print('Tranforming the geo-coordinate by pyproj.')
        meshproj = pyproj.Proj(
            "+proj=tmerc +ellps=WGS84 +datum=WGS84 +k=1.0 +lon_0=123.0 +lat_0=0 +x_0=500000 +y_0=0 +units=m")
        wgs84 = pyproj.Proj("+init=EPSG:4326")

        # -----------------------------------------------------------------------------
        # read all data
        inputfilename = self.file
        f = open(inputfilename)
        lines = f.readlines()
        f.close()

        print("The proj recorded in the data file is :")
        print((lines[0].strip().split()[1:]))
        # -----------------------------------------------------------------------------
        # arrange the data
        # The top data
        toplines = int(lines[0].strip().split()[0])
        ND = []
        linedata = []
        for i in range(1, toplines + 1):
            linedata = lines[i].strip().split()
            # convert the geo-cordition
            lon, lat = pyproj.transform(meshproj, wgs84, float(linedata[1]), float(linedata[2]))
            linedata[1] = str(lon)
            linedata[2] = str(lat)
            linedata[3] = str(-float(linedata[3]))  # 第四列转为正数
            linedata = ['ND'] + linedata[0:4]  # 第一列ND+数据(去掉最后一列)
            ND.append(linedata)
            linedata = []

        # The bottom data
        botlines = int(lines[toplines + 1].strip().split()[0])
        ED = []
        linedata = []
        for j in range(toplines + 2, toplines + 2 + botlines):
            linedata = lines[j].strip().split()
            linedata = ['E3T'] + linedata + ['1']
            ED.append(linedata)
            linedata = []
        OBID = []
        # -----------------------------------------------------------------------------
        return (ED, ND, OBID)
        ############################ End readGridMIKE #################################

    # In[5]
    ############################## writeGridFVCOM #################################
    def writeGridFVCOM(self, ED, ND, OBID, outfile, casename='An'):
        """
        -------------------------------------------
        writeGridFVCOM
        -------------------------------------------
        Usage:
            write mesh data to FVCOM mesh file: _cor.dat _dep.dat _grd.dat _obc.dat 
                and TPXO file: _obc_nodesLL.dat _obc_nodesID.dat
        
        Input:
            ED,ND,OBID,inputfile
        Output:
        will creat 4 .dat files
        --------------------------------------------
        Example：
        writeGridFVCOM(ED,ND,OBID,filename)
        --------------------------------------------
        Version: V1.0
        Date   : 2014/9/24
        Author : 安佰超 (anbaichao@gmail.com)
        --------------------------------------------
        """
        # ==============================================================================
        print("  The output Grid format is 'FVCOM Grids'")

        # filename setting for 6 kinds of files
        outpath = os.path.split(outfile)[0] + '/'
        corfilename = outpath + '/' + casename + '_cor.dat'
        depfilename = outpath + '/' + casename + '_dep.dat'
        grdfilename = outpath + '/' + casename + '_grd.dat'
        obcfilename = outpath + '/' + casename + '_obc.dat'
        obcLLfile = outpath + '/' + casename + '_obc_nodesLL.dat'
        obcIDfile = outpath + '/' + casename + '_obc_nodesID.dat'

        # headerline
        header1 = 'Node Number = ' + str(len(ND)) + '\n'
        header2 = 'Cell Number = ' + str(len(ED)) + '\n'
        obcheader = 'OBC Node Number = ' + str(len(OBID)) + '\n'

        # init the cordata,depdata,grddata
        cordata = np.empty([len(ND), 3])
        depdata = np.empty([len(ND), 3])
        grdNdata = np.empty([len(ND), 3])
        grdEdata = np.empty([len(ED), 5], dtype=int)
        obcdata = np.empty([len(OBID), 3], dtype=int)
        obcLL = np.empty([len(OBID), 2])

        # cut the ND to cordata,depdata
        for i in range(len(ND)):
            cordata[i, 0:2] = np.array(ND[i][2:4])
            cordata[i, 2] = ND[i][3]
            depdata[i, 0:3] = np.array(ND[i][2:5])
            grdNdata[i, :] = np.array(ND[i][1:4])

            # cut the ED to grdEdata
        for i in range(len(ED)):
            grdEdata[i, :] = np.array(ED[i][1:])

        # cut the OBID to obcdata
        for i in range(len(OBID)):
            obcdata[i, 0] = i + 1
            obcdata[i, 1] = np.abs(int(OBID[i]))
            obcdata[i, 2] = 1
            for NDline in ND:
                if str(OBID[i]).find(NDline[1]) != -1:
                    obcLL[i, 0] = NDline[3]
                    obcLL[i, 1] = NDline[2]

                    # ------------------------------------------------------------------------------
        # ----------write "Casename_cor.dat" for FVCOM
        writedat(corfilename, [cordata], ['%.4f %.4f %.4f'], [header1])
        # ----------write "Casename_dep.dat" for FVCOM
        writedat(depfilename, [depdata], ['%.4f %.4f %.4f'], [header1])
        # ----------write "Casenamr_grd.dat" for FVCOM
        writedat(grdfilename, [grdEdata, grdNdata], [' %d %d %d %d %d', ' %d %.4f %.4f'], [header1, header2])
        # ----------write "Casename_obc.dat" for FVCOM
        writedat(obcfilename, [obcdata], ['%5d %5d %5d'], [obcheader])
        # ----------Write "Casename_obc_nodesLL.dat" for TPXO
        writedat(obcLLfile, [obcLL[0:]], ['%10.3f %8.3f'])
        # ----------Write "Casename_obc_nodesID.dat" for TPXO
        writedat(obcIDfile, [obcdata[:, 1]], ['%5d'])

    # In[6]
    def writeGooglekml(self, ED, ND, outfile, kmlname="cjk_grids", name='ge_tri', description='',
                       lineColor='FFFFFF00', polyColor='40ff833e', lineWidth=1.0):
        """
        write Grids to a google earth kml format file.
        
            -------------------------------------------
            writeGooglekml Man:
                Usage : write Grids to a google earth kml format file.
            
                Input : 
    				ED: the triangle data
    				ND: the node data
    				outpath: specify the kml output path
    				kmlname: specify the kml file name,need no ".kml".
    				name: the kml name which will written in the kmlfile.
    				description: '' is default,you can write your description of the kml file here.
    				lineColor: 'FFFFFF00' is default
    				polyColor: '40ff833e' is default 
    				
                Output : will create a '.kml' format file in the specify dir.
                
            --------------------------------------------
            Example：
                writeGooglekml(ED,ND,outpath,kmlname="cjk_grids",name = 'ge_tri',description = '',
                       lineColor = 'FFFFFF00',polyColor = '40ff833e',lineWidth = 1.0)
    
            --------------------------------------------
            Author : 
                安佰超 (anbaichao@gmail.com)
                
            --------------------------------------------
            History:
                Version V1.0: 2014/11/18
                    establish this function.
            
            --------------------------------------------
        
        """
        outfile = outfile[0:-4] + '.kml'
        #    ED=self.ED
        #    ND=self.ND
        #    OBID=self.OBID
        f = open(outfile, 'w')
        print("Writing to '.kml' format file...")
        # ------------------------------------------------------------------------------
        #  File_Header
        # ------------------------------------------------------------------------------
        fileheader = '<?xml version="1.0" encoding="UTF-8"?>' + '\n' + \
                     '<kml xmlns="http://earth.google.com/kml/2.1">' + '\n' + \
                     '<Document>' + '\n' + \
                     '<name>' + '\n' + kmlname + '\n' + '</name>' + '\n'
        #  Write_fileheader
        f.writelines(fileheader)

        # ------------------------------------------------------------------------------
        #  polygons
        # ------------------------------------------------------------------------------
        for i, elem in enumerate(ED):
            # ------------ arange the nodes data -----------
            node1 = (
            [float(ND[int(ED[i, 2]) - 1, 2]), float(ND[int(ED[i, 2]) - 1, 3]), float(ND[int(ED[i, 2]) - 1, 4])])
            node2 = (
            [float(ND[int(ED[i, 3]) - 1, 2]), float(ND[int(ED[i, 3]) - 1, 3]), float(ND[int(ED[i, 3]) - 1, 4])])
            node3 = (
            [float(ND[int(ED[i, 4]) - 1, 2]), float(ND[int(ED[i, 4]) - 1, 3]), float(ND[int(ED[i, 4]) - 1, 4])])

            # ----------- set the polygon_header ----------
            # give the vars value
            idstr = 'triangle'
            idTag = 'id'
            #    name = 'ge_tri'
            #    description = ''
            timeStamp = ' '
            timeSpanStart = ' '
            timeSpanStop = ' '
            visibility = 1
            #    lineColor = 'FFFFFF00'#'ffffffff'
            #    msgToScreen = 0
            #    polyColor = '40ff833e'#'ffffffff'
            #    lineWidth = 1.0
            snippet = ' '
            #    altitude = 1.0
            extrude = 1
            tessellate = 0
            altitudeMode = 'clampToGround'

            # arange the poly_strs
            id_chars = idTag + '="' + idstr + '"'
            poly_id_chars = idTag + '="poly_' + idstr + '"'
            name_chars = '<name>' + '\n' + name + '\n' + '</name>' + '\n'
            description_chars = '<description>' + '\n' + '<![CDATA[' + description + ']]>' + '\n' + '</description>' + '\n'
            visibility_chars = '<visibility>' + '\n' + str(visibility) + '\n' + '</visibility>' + '\n'
            lineColor_chars = '<color>' + '\n' + lineColor + '\n' + '</color>' + '\n'
            polyColor_chars = '<color>' + '\n' + polyColor + '\n' + '</color>' + '\n'
            lineWidth_chars = '<width>' + '\n' + '{:.2f}'.format(lineWidth) + '\n' + '</width>' + '\n'
            altitudeMode_chars = '<altitudeMode>' + '\n' + altitudeMode + '\n' + '</altitudeMode>' + '\n'
            extrude_chars = '<extrude>' + str(extrude) + '</extrude>' + '\n'
            tessellate_chars = '<tessellate>' + str(tessellate) + '</tessellate>' + '\n'
            if snippet == ' ':
                snippet_chars = ''
            else:
                snippet_chars = '<Snippet>' + snippet + '</Snippet>' + '\n'
            if timeStamp == ' ':
                timeStamp_chars = ''
            else:
                timeStamp_chars = '<TimeStamp><when>' + timeStamp + '</when></TimeStamp>' + '\n'
            if timeSpanStart == ' ':
                timeSpan_chars = ''
            else:
                if timeSpanStop == ' ':
                    timeSpan_chars = '<TimeSpan><begin>' + timeSpanStart + '</begin></TimeSpan>' + '\n'
                else:
                    timeSpan_chars = '<TimeSpan><begin>' + timeSpanStart + '</begin><end>' + timeSpanStop + '</end></TimeSpan>' + '\n'

                    # gen the poly header using the poly_strs
            header = '<Placemark ' + id_chars + '>\n' + \
                     name_chars + \
                     timeStamp_chars + \
                     timeSpan_chars + \
                     visibility_chars + \
                     snippet_chars + \
                     description_chars + '\n' + \
                     '<Style>' + '\n' + \
                     '<LineStyle>' + '\n' + \
                     lineColor_chars + \
                     lineWidth_chars + \
                     '</LineStyle>' + '\n' + \
                     '<PolyStyle>' + '\n' + \
                     polyColor_chars + \
                     '</PolyStyle>' + '\n' + \
                     '</Style>' + '\n' + \
                     '<Polygon ' + poly_id_chars + '>' + '\n' + \
                     extrude_chars + \
                     altitudeMode_chars + \
                     '<outerBoundaryIs>' + '\n' + \
                     '<LinearRing>' + '\n' + \
                     extrude_chars + \
                     tessellate_chars + \
                     altitudeMode_chars + \
                     '<coordinates>' + '\n'

            # ----------- set the poly_footer ----------
            footer = '</coordinates>\n</LinearRing>\n</outerBoundaryIs>\n</Polygon>\n</Placemark>\n'

            # ----------- set the poly_coordinate ----------
            str_format = '{0:.6f},{1:.6f},{2:.6f}'.format
            coordinates = str_format(node1[0], node1[1], node1[2]) + '\n' + \
                          str_format(node2[0], node2[1], node2[2]) + '\n' + \
                          str_format(node3[0], node3[1], node3[2]) + '\n' + \
                          str_format(node1[0], node1[1], node1[2]) + '\n'

            # ----------- write poly header coordinates footer -------------
            f.writelines(header)
            f.writelines(coordinates)
            f.writelines(footer)

        # ------------------------------------------------------------------------------
        #  File_Footer
        # ------------------------------------------------------------------------------
        filefooter = '\n' + '</Document>' + '\n' + \
                     '</kml>'

        f.writelines(filefooter)

        f.close()
        print(("'.kml' format file has been written successfully! Path: " + outfile))


# In[4]
############################ writeGridSMS######################################
def writeGridSMS(ED, ND, OBID, twodmfile):
    """
    -------------------------------------------
    write2dm
    -------------------------------------------
    Usage:
    write the SMS Grid .2dm file .
        Now can only write the ED ND data .
        Will add the OBID data. 
    
    Input:
        ED,ND,twodmfile 
    Output:
        will creat a .2dm file
        
    --------------------------------------------
    Example：
    writeGridSMS(ED,ND,twodmfile)
    
    --------------------------------------------
    Version: V1.0
    Date   : 2014/9/24
    Author : 安佰超 (anbaichao@gmail.com)
    
    ---------------------------------------
    
    """

    # ==============================================================================
    # Main
    # =================

    header = ['MESH2D\n']

    footer = ['''BEGPARAMDEF
    GM  Mesh
    SI  0
    DY  0
    TD  0  0
    NUME  2
    ENDPARAMDEF
    BEG2DMBC
    END2DMBC''']

    # twodmfile='testwrite2dm.2dm'
    f = open(twodmfile, 'w')

    f.writelines(header)

    for i in range(len(ED)):
        f.write(' '.join(ED[i]) + '\n')

    for i in range(len(ND)):
        f.write(' '.join(ND[i]) + '\n')

    # -- The Key thought of OBID writing:
    # 1. write the OBID
    # 2. Each line starts with the 'NS '
    # 3. a Each ten IDs need a line break,means the iobid%10.==0,write a line break
    #    b Each minus ID need a line break,means sometime we need a line break but the iobid is not enough to n*ten(iobid%10!=0).
    #        After that the index need to be reset to start another tens loop(for tens' line break).
    #      we need another flag which both record the ten loop for given a tens' line break(each loop add 1)
    #        and when minus ID occurs,it is reset to start another ten loop immediately(set to zero). 
    #    c the best way is each line break reset index to zero.
    # WorkFlow:
    #    1.Given a index=0, 
    #    2.when the index==0,write 'NS '
    #    3.write OBID
    #    4.index++
    #    5. when the next iobid is the tens ID,write line break. the index reset to zero
    #       When the first not ten but minus ID occurs, write line break and the index reset to zero.
    #    6.to 1.   
    index = 0
    for iobid in range(len(OBID)):

        if index == 0:
            f.write('NS ')

        f.write("{0:10d}".format(OBID[iobid]))
        index = index + 1

        if (index) % 10. == 0 or iobid in np.arange(len(OBID))[OBID < 0]:
            f.write('\n')
            index = 0

    f.writelines(footer)
    f.close()
    print("-----  The SMS '.2dm' file has been created successfully!  -----")
    print(('-----  PATH : ' + twodmfile + '  -----\n'))
