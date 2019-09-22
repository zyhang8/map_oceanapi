# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 17:59:40 2018

@author: xwang
"""

def swan_input(filename,wind_data,rec):
    
    # =========================================================
    #    out put the wind file needed for *swn
    # =========================================================
    start_time = wind_data['ptime'][0]
    end_time = wind_data['ptime'][-1]
    ntime = len(wind_data['ptime'])
    print('==================write_output==========================')
    with open(filename, "w", encoding="UTF-8") as f:
        f.write("wind data start from: WS point\n")
        f.write("time info: %s, %s, 1:00:00\n"%(start_time.strftime('%Y-%m-%d %H:%M:%S'),end_time.strftime('%Y-%m-%d %H:%M:%S')))
        f.write("coords range: origin {:.3f} {:.3f}, number-1 {:} {:}, step {:.3f} {:.3f} \n".format(rec['lon0'], rec['lat0'], 
                rec['nbin_lon']-1,rec['nbin_lat']-1,rec['step'],rec['step']))
        for i in range(0,int(ntime+1)):   
            f.write("it: "+str(i)+" time: "+wind_data['ptime'][i].strftime('%Y-%m-%d %H:%M:%S')+"\n")
            print("it: "+str(i)+" time: "+wind_data['ptime'][i].strftime('%Y-%m-%d %H:%M:%S')+"\n")
            for nu in range(0,wind_data['U10'][i].shape[0]):
                 for nv in range(0,wind_data['U10'][i].shape[1]):
                        if wind_data['U10'][i,nu,nv]>0 and wind_data['U10'][i,nu,nv]<10:
                            f.write(" %.2f"%(wind_data['U10'][i,nu,nv]))
                        else:
                            f.write("%.2f"%(wind_data['U10'][i,nu,nv]))   
                        if nv !=wind_data['U10'][i].shape[1]-1:
                            f.write(" ")
                 f.write("\n")
            for nu in range(0,wind_data['U10'][i].shape[0]):
                 for nv in range(0,wind_data['U10'][i].shape[1]):
                        if wind_data['V10'][i,nu,nv]>0 and wind_data['V10'][i,nu,nv]<10:
                            f.write(" %.2f"%(wind_data['V10'][i,nu,nv]))
                        else:
                            f.write("%.2f"%(wind_data['V10'][i,nu,nv]))         
                        if nv !=wind_data['U10'][i].shape[1]-1:
                            f.write(" ")                            
                 f.write("\n")                        
