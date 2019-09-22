#!/home/users/oper/opt/bin/python 
import subprocess
import logging

logger = logging.getLogger(__name__)


def sub(Path, Flag, config, JobName):
    # =================== Write the PBS_Script ================
    logger.info("Write the PBS_Script for {:}".format(Flag))

    Group = config['Group']
    ppn = config['ppn']
    nodes = config[Flag]
    MPI_HOME = config['MPI_HOME']

    filepath = "{:}/PBS_Script.{:}".format(Path, Flag)

    f = open(filepath, 'w')

    # ShaBang
    f.write("#!/bin/sh\n")

    # Set the resource
    f.write("#PBS -l nodes={:}:ppn={:}\n".format(nodes, ppn))
    # Set the output
    f.write("#PBS -j oe\n")
    # Set the JobName
    f.write("#PBS -N {:}\n".format(JobName))
    # Set the Pool
    f.write("#PBS -q {:}\n\n\n".format(Group))

    f.write("MPI_HOME={:}\n".format(MPI_HOME))
    f.write("n_proc=$(cat $PBS_NODEFILE | wc -l)\n")
    f.write("echo $PBS_O_WORKDIR\n")
    f.write("cd $PBS_O_WORKDIR\n\n\n")

    if Flag == "FVCOM":
        f.write("$MPI_HOME/bin/mpirun -np $n_proc -hostfile $PBS_NODEFILE ./fvcom --casename=NCS  > ireport 2>&1\n\n")

    elif Flag == "geogrid" or Flag == "metgrid":
        f.write("$MPI_HOME/bin/mpirun -np $n_proc -hostfile $PBS_NODEFILE ./{:}.exe > ireport.{:} 2>&1\n\n".format(Flag,
                                                                                                                   Flag))

    else:
        f.write("$MPI_HOME/bin/mpirun -np $n_proc -hostfile $PBS_NODEFILE ./{:}.exe > ireport.{:} 2>&1\n\n".format(Flag,
                                                                                                                   Flag))
    f.write("\nexit 0")
    f.close()
    logger.info("PBS_Script.{:} Has been written".format(Flag))
    logger.info("PATH : {:}".format(Path))

    # ================== Submit the job =================
    logger.info("Submit the {:} task".format(Flag))

    cmd = "qsub PBS_Script.{:}".format(Flag)
    logger.info("{:} task: {:}".format(Flag, cmd))

    JobID = subprocess.check_output(cmd, shell=True)
    logger.info("qsub output: {:}".format(JobID.strip().decode()))

    return JobID.strip()
