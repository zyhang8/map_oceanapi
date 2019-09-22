# ============================ IMPORT =====================
import os
import logging
import shutil
import re
import numpy as np

logger = logging.getLogger(__name__)


def check_mkdir(target_dir):
    try:
        os.mkdir(target_dir)
        logger.info("The Dir : {:} has been made!".format(target_dir))
    except OSError:
        logger.info("The Dir already exists, Pass!".format(target_dir))


def check_lsdir(dst):
    logger.info("**check_lsdir", dst)
    filelist = os.listdir(dst)
    filelist.sort()
    for ifile in filelist:
        logger.info("ListDir", ifile)


def check_remove(target_file):
    try:
        os.remove(target_file)
        logger.info("The old {:} file has been removed !".format(os.path.split(target_file)[1]))
        logger.info("PATH : {:}".format(os.path.split(target_file)[0]))
    except OSError:
        logger.info("No this file : {:} !".format(os.path.split(target_file)[1]))
        logger.info("PATH : {:}".format(os.path.split(target_file)[0]))


def check_purge(dir, pattern):
    flag = 0
    for f in os.listdir(dir):
        if re.search(pattern, f):
            os.remove(os.path.join(dir, f))
            flag = flag + 1
    if flag == 0:
        logger.info("No {:} file".format(pattern))
        logger.info("PATH : {:}".format(dir))
    else:
        logger.info("{:} {:} file has been removed!".format(flag, pattern))
        logger.info("PATH : {:}".format(dir))


def check_move(src, pattern, dst):
    """remove and check files that match the pattern.
    if just one file,the filename is the pattern.
    if the dst file is exist,backup the file,but just backup once.
    """

    flag = 0
    for f in os.listdir(src):

        if re.search(pattern, f):

            dstfile = os.path.join(dst, f)
            dstfile_bak = os.path.join(dst, "{:}.bak".format(f))

            if os.path.isfile(dstfile):
                if os.path.isfile(dstfile_bak):
                    check_remove(dstfile_bak)
                shutil.move(dstfile, dstfile_bak)

            shutil.move(os.path.join(src, f), dst)

            flag = flag + 1

    if flag == 0:
        logger.warning("No {:} file".format(pattern))
        logger.info("PATH : {:}".format(src))
    else:
        logger.info("Move {:} files {:} -->> {:}".format(flag, src, dst))


def check_symlink(source_file, target_file, flag="pass"):
    logger.info( "{:} >>>>> {:}".format(source_file, target_file))

    if os.path.isfile(source_file):

        try:
            os.symlink(source_file, target_file)

        # except for case : there has been the target file
        except OSError:

            if flag == "pass":
                logger.warning("There has been the {:}, pass!".format(target_file))
            elif flag == "force":
                check_remove(target_file)
                os.symlink(source_file, target_file)
                logger.warning("The old file has been removed, and the new file has been linked !")
            else:
                logger.error(ValueError, "No this flag : {:}".format(flag))
    else:
        # except for case : there is no source file
        logger.error(IOError, "No this source_file {:} !".format(source_file))


def check_exist(pattern, path):
    logger.info("PATH : {:}".format(path))

    count = 0
    for f in os.listdir(path):
        if re.search(pattern, f):
            logger.info(f)
            count = count + 1

    if count == 0:
        logger.info("No {:} file".format(pattern))
        return 1
    else:
        return 0


def sort_path(PATH_Dict):
    pathlist = []
    flaglist = []
    for key, path in PATH_Dict.items():
        pathlist.append(os.path.normpath(path))
        flaglist.append(os.path.normpath(path).count('/'))
    path_array = np.asarray(pathlist)
    flag_array = np.asarray(flaglist)

    pathlevel = flag_array.min()
    path_sort = []
    for ipath in path_array[flag_array == pathlevel]:
        path_sort.append(ipath)
        for jpath in path_array[flag_array == pathlevel + 1]:
            if ipath == os.path.split(os.path.normpath(jpath))[0]:
                path_sort.append(jpath)

    return path_sort
