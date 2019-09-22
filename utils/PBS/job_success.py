#!/usr/bin/env python2.5

# The function will check the current uid automatically, other than the given uid.
# 2016/10/12

#---------------------------------------------------------------------
#
#---------------------------------------------------------------------

#------------- Import --------------
import subprocess
import time
import getpass

def job_finished(tlimit=16.0,sleeptime=600,JobID="",job=""):
    

    # print start format str
    print("!")
    uid = getpass.getuser() 
    cmd = "qstat -u " + uid
    print("!  Command: "+ cmd)
    print("!{:}".format(">>>>>"*23))
    
    jobname,jobid =  pyqstat(JobID,machine="mgma",flag="all")
    
    cnt = 0
    
    while ( job in jobname ):
        
        slept = cnt*sleeptime/3600.0
        print("!  Waited:", slept , "(hours);")
        print("!  Job in queue: {:}".format(jobname[0]))
        print("!  ----------------------- ----------- -------- ---------------- ------ ----- ------ ------ --------- - ---------")
        
        cnt = cnt + 1
        if slept > tlimit:
            return -1
        time.sleep(sleeptime)
        jobname,jobid =  pyqstat(JobID,machine="mgma")

    # print end format str
    print("!\n!{:}".format("<<<<<"*23))

    return 0


def pyqstat(JobID,machine="",flag="normal",DBG=0):
    #Note : The input JobID is a byte-str,although i do not know why.
    if DBG:
        print("JobID",JobID)
        index=0

    uid = getpass.getuser() 
    cmd = "qstat -u " + uid
    
    p=subprocess.Popen(cmd.split(),stdout=subprocess.PIPE)

    jobid = []
    jobname = []
    for line in p.stdout.readlines():
        
        #line split by space.
        line=line.strip(b'\n')
        splitline=line.split()
        if DBG:
            print(splitline)
            index=index+1
            print(index)

        if len(splitline) != 0:
        
            #the fisrt str of line,if XX.XX,get jobid,jobname
            splitfirst = splitline[0].split(b".")
            if DBG:
                print(splitfirst)

            if flag=="all":
                print("!  {:}".format(line.decode()))

            if splitline[0].strip() == JobID:
                if flag=="normal":
                    print("!  {:}".format(line.decode()))
                jobid.append(int(splitfirst[0]))
                jobname.append(splitline[3].decode())
    print("!  ----------------------- ----------- -------- ---------------- ------ ----- ------ ------ --------- - ---------")
    if DBG:
        print(jobname,jobid)

    return (jobname,jobid)


if __name__ == "__main__":
    jobname,jobid = pyqstat(JobID="10234.mgma",machine="mgma",flag="all")
    for ind in range(len(jobid)):
        print("jobname: " + jobname[ind] + "; jobid: ",jobid[ind])
    print('jobname=',jobname,'jobid=',jobid )
