# -*- coding: utf-8 -*-
"""
Functions for FVCOM node_nest_file.
---------------------------------------------
History:
    
    Version 0.2   2016/12/12 20:23:00
    add the def parse_Node_log, which can read the node_id from a simple Node_log file. 
        
    Version 0.1   2016/12/09 21:50:00
    Created.
---------------------------------------------
Author:
    
    AN BAICHAO            
    anbaichao@gmail.com

---------------------------------------------
Notes:

    Comments about node_nest_file from FVCOM Manual V3.1.6 
    
    8. Casename_node_nest.dat
    
    Node_Nest_ Number = xxxx 
    No. Node_ID Node_Type 
    1 x x 
    2 x x 
    ......
    NOB x x
    
    Node_Nest_Number: Total number of nodes on the nesting boundary.
    
    No.: Counting number of the open boundary node from 1 to OBC Node_Number.
    
    Node_ID: Node ID on the nesting boundary.
    
    Node Type: Always keep an integer of “1”. Not used in the program, but required to read in.
    
    
    Example:
    
    Node_Nest Number = 5 
    1 34760  1
    2 34268  1
    3 34269  1
    4 33767  1
    5 33259  1
    
    9. Casename_node_nest_wave.dat
    The data content and structure of this wave nesting input file are the same as in the casename_node_nest.dat.

=============================================================================
"""
import numpy as np


def write_Nesting_file(NESTING_FILE,Nesting_node_id):
        
    Node_Nest_Number=len(Nesting_node_id)
    
    f=open(NESTING_FILE,'w')
    
    f.write("Node_Nest_Number = {}\n".format(Node_Nest_Number))
    
    for i in range(Node_Nest_Number):
        f.write("{:3d}  {:8d}  {:3d}\n".format(i+1,Nesting_node_id[i],1))
    
    f.close()
    
    print(("\n----- The NESTING_FILE has been writen : {} -----\n".format(NESTING_FILE)))

    
def parse_Nesting_file(NESTING_FILE):
    
    f=open(NESTING_FILE,'r')
    Dlines=f.readlines()
    
    Node_Nest_Number=int(Dlines[0].strip().split("=")[1])
    print(("\n----- Node_Nest_Number = {} -----\n".format(Node_Nest_Number)))
    
    Nesting_node_id=[]
    for iline in Dlines[1:]:
        Nesting_node_id.append(int(iline.strip().split()[1]))
    
    if Node_Nest_Number != len(Nesting_node_id):
        print(("\n----- len(Nesting_node_id) = {} -----\n".format(len(Nesting_node_id))))
        print("\n----- There are somethine wrong ! Node_Nest_Number != len(Nesting_node_id) -----\n")
        
    return np.asarray(Nesting_node_id,int)

def parse_Node_log(Node_log):
    
    f=open(Node_log,'r')
    Dlines=f.readlines()
    
    Nesting_node_id=[]
    for iline in Dlines:
        for inode in iline.strip().split(',')[:]:
            if inode:
                Nesting_node_id.append(int(inode))
    
    print(("\n----- The Node_log has been read : {} -----\n".format(Node_log)))

    return Nesting_node_id
    
    
if __name__=="__main__":
    
    #Example for usage:
        
    NESTING_NODE_FILE="/Users/ban/Models/Test_Files/Nesting_node_file.dat"  

    #1. read Nesting_file
    #Nesting_node_id=parse_Nesting_file(NESTING_NODE_FILE)
    

    #2. write Nesting_file
    
    #read from Node_log
    Node_log_file="/Users/ban/Models/Test_Files/Node_log_file.dat"
    Nesting_node_id1=parse_Node_log(Node_log_file)
    
    #add the obc-1 to the node list
    #Sometimes,the one of obc is part of the nesting nodes,
    #The simple way is add it to the nodelist directly.
    Nesting_node_id=Nesting_node_id1+list(range(1,146))+[147,146]+list(range(148,291))
    
    write_Nesting_file(NESTING_NODE_FILE,Nesting_node_id)