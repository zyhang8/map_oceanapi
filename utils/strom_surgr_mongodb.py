#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@author:yaochenyang
@file: strom_surgr_mongodb.py
@time: 2019-07-20 14:36
"""
from netCDF4 import Dataset
import datetime
from datetime import timedelta
from bson.objectid import ObjectId
from pymongo import MongoClient
import json

# ------------------------------------------
#   读取mongodb相关数据
#
# ------------------------------------------
def write2json(filename, particle):
    with open(filename, "w", encoding="UTF-8") as f_dump:
        s_dump = json.dump(particle, f_dump)
    print(" !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", "\n", "   successful complete the task ", "\n",
          "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    return None

def get_mongdodb():
    user = "dev"
    pwd = "Shou2013o6"
    server = "58.198.131.182"
    port = "5088"
    # mongodb://[username:password@]host1[:port1][,host2[:port2],...[,hostN[:portN]]][/[database][?options]]
    # user = "***"
    # pwd = "***"
    # server = "***"
    # port = "***"
    db_name = "portal"
    url = 'mongodb://' + user + ':' + pwd + '@' + server + ':' + port + '/' + db_name
    client = MongoClient(url)
    db = client.portal
    return db

def insert_mongodb(particle):
    db = get_mongdodb()
    my_collection = db.saresults
    my_collection.insert(particle)
    return None


def read_sarobjects_mongodb(sarobject):
    db = get_mongdodb()
    my_collection = db.sarobjects
    data = my_collection.find({'name': sarobject})
    sarobjects_info = next(data, None)
    return sarobjects_info


def read_mongodb():
    db = get_mongdodb()
    my_collection = db.tasks
    data = my_collection.find({"type": "storm", 'status': 'init'})
    task_init = next(data, None)
    if task_init is None:
        pass
    else:
        # 处理结构
        task_init['casename'] = task_init['name']
    return task_init

def production_Particle():
    task_init = read_mongodb()
    # 经度不变，纬度变10
    length = 11
    parameter_poition = [ (-1.2+j*0.2)/111000 for j in range(1, 12)]
    ori_latitude = task_init['location'][0]['latitude']
    longitude = [task_init['location'][0]['longitude']]*length
    # 默尔深度都是0
    depth = [0]*length
    latitude = [ori_latitude + obj for obj in parameter_poition]
    itlag = [0 + index for index in range(1, 12)]
    particle = [itlag, longitude, latitude, depth]
    return particle


def update_status(taskStatus, task_id):
    db = get_mongdodb()
    my_collection = db.tasks
    my_collection.update({"_id": task_id}, {"$set": {"status": "alive"}})
    #data = my_collection.find_one({'_id': task_id})
    # data = my_collection.find_one({'_id': task_id})

    #print(type(task_id))
    #print(data['_id'])
    if taskStatus == 500:
        # data.update({"_id": task_id}, {"$set": {"status": "alive"}})
        my_collection.update({"_id": task_id}, {"$set": {"status": "alive"}})

    elif taskStatus == 200:
        #data.update({"_id": task_id}, {"$set": {"status": "success"}})
        my_collection.update({"_id": task_id}, {"$set": {"status": "success"}})


def insert_result_mongodb(particle):
    db = get_mongdodb()
    my_collection = db.saresults
    my_collection.insert(particle)


def insert_figure_mongodb(picture_infomation_dict, task_id):
    db = get_mongdodb()
    my_collection = db.saresults
    my_collection.update({"taskid": task_id}, {"$set": {"chart": picture_infomation_dict}})

