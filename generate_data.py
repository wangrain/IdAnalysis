#!/bin/env python
# -*- coding: utf-8 -*-

'''
生成用虚拟身份证ID到result文件夹ID_list.txt文件汇总
'''
import pickle
import random
from datetime import date, datetime,timedelta

def getCreditCartNum(district_list):
    district_code = random.choice(district_list)# 地区码
    date_code = date.today() + timedelta(days=random.randint(1, 366))  # 月份和日期项
    date_code = str(random.randint(1950, 2005)) + date_code.strftime('%m%d') # 增加年份
    id_num = district_code + date_code + str(random.randint(100, 300))  # ，顺序号简单处理

    count = 0
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]  # 权重项
    checkcode = {'0': '1', '1': '0', '2': 'X', '3': '9', '4': '8', '5': '7', '6': '6', '7': '5', '8': '5', '9': '3',
                 '10': '2'}  # 校验码映射
    for i in range(0, len(id_num)):
        count = count + int(id_num[i]) * weight[i]
    idNum = id_num + checkcode[str(count % 11)]  # 算出校验码
    return idNum

def writeToTXT(id_list_file,count):
    #引入地区码字典文件
    district_pkl = pickle.load(open('pkl/district.pkl', 'rb'))
    district_list = []
    # 获取地区码列表
    for district in district_pkl:
        district_list.append(district)
    # 开始循环生成身份证号码，并存入文件中
    writer = open(id_list_file, 'wt')
    result_str = ''
    for i in range(count):
        result_str += getCreditCartNum(district_list) + '\n'
    writer.write(result_str)


starttime = datetime.now()
id_list_file = 'data/ID_list.txt' # 结果文件
count = 100000 # 生成记录数
writeToTXT(id_list_file,count) # 生成固定个数身份证号码，并写入文件中
endtime = datetime.now()
print('共生成'+str(count)+'条记录，运行时间：' + str((endtime - starttime).seconds) + '秒')