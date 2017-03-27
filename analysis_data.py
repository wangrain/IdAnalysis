#!/bin/env python
# -*- coding: utf-8 -*-

import pickle
import fileinput
import datetime
import sys
sys.path.append('./libs')
import xlrd
from xlutils.copy import copy


class Address:
    province_id = ''
    province_name = ''
    city_id = ''
    city_name = ''
    district_id = ''
    district_name = ''
    def __init__(self, province_id, province_name,city_id,city_name,district_id,district_name):
        self.province_id = province_id
        self.province_name = province_name
        self.city_id = city_id
        self.city_name = city_name
        self.district_id = district_id
        self.district_name = district_name
    def to_string(self):
            return self.province_name + '\t' + self.city_name + '\t' + self.district_name

class IdInfo:
    count = 1
    def __init__(self, id_num,valid, sex,age,birth,address):
        self.id_num = id_num
        self.valid = valid
        self.sex = sex
        self.age = age
        self.birth = birth
        self.address = address
    def add_count(self,i):
        self.count += i
    def to_string(self):
        if(self.valid):
            return '<合法>\t' + str(self.count) + '\t' + self.id_num + '\t' + self.sex + '\t' + self.age + '\t' + self.birth + '\t' + self.address.to_string()
        else:
            return '<不合法>\t' + self.id_num

class IdAnalyseResult:
    valid_sum = {}
    sex_sum = {}
    age_sum = {}
    age_interval_sum = {}
    province_sum = {}
    city_sum = {}

def calculateIdInfo(i):
    id_num = i.lower().strip()
    if len(id_num) == 18:
        #计算身份证号码的的合法性
        tmpsum = int(id_num[0])*7 + int(id_num[1])*9 + int(id_num[2])*10 + int(id_num[3])*5 + int(id_num[4])*8 \
                + int(id_num[5])*4 + int(id_num[6])*2 + int(id_num[7])*1 + int(id_num[8])*6 + int(id_num[9])*3 \
                + int(id_num[10])*7 + int(id_num[11])*9 + int(id_num[12])*10 + int(id_num[13])*5 \
                + int(id_num[14])*8 + int(id_num[15])*4 + int(id_num[16])*2
        remainder = tmpsum % 11
        maptable = {0: '1', 1: '0', 2: 'x', 3: '9', 4: '8', 5: '7', 6: '6', 7: '5', 8: '4', 9: '3', 10: '2'}
        isvalid = maptable[remainder] == id_num[17]
    else:
        isvalid = False
    if isvalid:
        #计算性别
        sex = int(id_num[16]) % 2
        sex = '男' if sex == 1 else '女'
        #计算生日
        birth = datetime.date(int(id_num[6:10]),int(id_num[10:12]),int(id_num[12:14]))
        age = datetime.date.today().year - int(id_num[6:10])
        #找到身份证号码对应的省、市、地区
        province_id = id_num[:2]
        city_id = id_num[:4]
        district_id = id_num[:6]
        #根据地区码取出地区名
        province_name = province_list[province_id] if province_list.get(province_id) else '-'
        city_name = city_list[city_id] if city_list.get(city_id) else '-'
        district_name = district_list[district_id] if district_list.get(district_id) else '-'
        address = Address(province_id,province_name,city_id,city_name,district_id,district_name)
        idInfo = IdInfo(id_num, True, sex, str(age), str(birth), address)
        return idInfo
    else :
        idInfo = IdInfo(id_num, False, '', '', '', '')
        return idInfo

def getAgeInterval(age):
    age = int(age)
    if age < 15:
        return '15岁以下'
    elif age >=15 and age < 20:
        return '15-20岁'
    elif age >=20 and age < 25:
        return '20-25岁'
    elif age >=25 and age < 30:
        return '25-30岁'
    elif age >=30 and age < 35:
        return '30-35岁'
    elif age >=35 and age < 40:
        return '35-40岁'
    elif age >=40 and age < 45:
        return '40-45岁'
    elif age >=45 and age < 50:
        return '45-50岁'
    elif age >=50 and age < 55:
        return '50-55岁'
    elif age >=55 and age < 60:
        return '55-60岁'
    elif age >=60 and age < 65:
        return '60-65岁'
    else :
        return '65岁以上'

def writeResultToTxt(result,analyse_result_file):
    writer = open(analyse_result_file, 'wt')
    result_str = '身份证列表分析结果\n'
    #遍历有效性
    result_str += '\t证件号码有效性分析\n'
    result.valid_sum= sorted(result.valid_sum.items(), key=lambda d:d[1], reverse = True)
    for d in result.valid_sum:
        if d[0]:
            result_str += "\t\t有效数"+ str(d[1]) + '\n'
        else:
            result_str += "\t\t无效数"+ str(d[1]) + '\n'
    result.sex_sum= sorted(result.sex_sum.items(), key=lambda d:d[1], reverse = True)
    result_str += '\t性别分析\n'
    for d in result.sex_sum:
        result_str += '\t\t' + d[0] + '\t:\t' + str(d[1]) + '\n'
    result_str += '\t年龄区间分析\n'
    for d in result.age_interval_sum:
        result_str += '\t\t' + d + '\t:\t' + str(result.age_interval_sum[d]) + '\n'
    result.age_sum= sorted(result.age_sum.items(), key=lambda d:d[1], reverse = True)
    result_str += '\t年龄分析\n'
    for d in result.age_sum:
        result_str += '\t\t' + d[0] + '岁\t:\t' + str(d[1]) + '\n'
    result.province_sum= sorted(result.province_sum.items(), key=lambda d:d[1], reverse = True)
    result_str += '\t省份分析\n'
    for d in result.province_sum:
        result_str += '\t\t' + d[0] + '\t:\t' + str(d[1]) + '\n'
    result.city_sum= sorted(result.city_sum.items(), key=lambda d:d[1], reverse = True)
    result_str += '\t城市分析\n'
    for d in result.city_sum:
        if d[0] == '-':
            continue
        result_str += '\t\t' + d[0] + '\t:\t' + str(d[1]) + '\n'
    writer.write(result_str)

def writeResultToExcel(result,excel_file):
    excel_r = xlrd.open_workbook(excel_file)
    excel_w = copy(excel_r)
    sheet_data = excel_w.get_sheet('数据')
    #有效性分析
    for d in result.valid_sum:
        if d[0]:
            sheet_data.write(1, 1, d[1]) # B2-有效数
        else:
            sheet_data.write(2,1, d[1]) #B3-无效数
    #性别分析
    for d in result.sex_sum:
        if d[0] == '男':
            sheet_data.write(1,3,d[1])#D2-男性人数
        else:
            sheet_data.write(2,3,d[1]) #D3-女性人数
    #年龄区间分析
    sheet_data.write(1,5, result.age_interval_sum['15岁以下'] if result.age_interval_sum.get('15岁以下') else 0)
    sheet_data.write(2,5 ,result.age_interval_sum['15-20岁'] if result.age_interval_sum.get('15-20岁') else 0)
    sheet_data.write(3,5 ,result.age_interval_sum['20-25岁'] if result.age_interval_sum.get('20-25岁') else 0)
    sheet_data.write(4,5 ,result.age_interval_sum['25-30岁'] if result.age_interval_sum.get('25-30岁') else 0)
    sheet_data.write(5,5 ,result.age_interval_sum['30-35岁'] if result.age_interval_sum.get('30-35岁') else 0)
    sheet_data.write(6,5 ,result.age_interval_sum['35-40岁'] if result.age_interval_sum.get('35-40岁') else 0)
    sheet_data.write(7,5 ,result.age_interval_sum['40-45岁'] if result.age_interval_sum.get('40-45岁') else 0)
    sheet_data.write(8,5 ,result.age_interval_sum['45-50岁'] if result.age_interval_sum.get('45-50岁') else 0)
    sheet_data.write(9,5 ,result.age_interval_sum['50-55岁'] if result.age_interval_sum.get('50-55岁') else 0)
    sheet_data.write(10,5,result.age_interval_sum['55-60岁'] if result.age_interval_sum.get('55-60岁') else 0)
    sheet_data.write(11,5,result.age_interval_sum['60-65岁'] if result.age_interval_sum.get('60-65岁') else 0)
    sheet_data.write(12,5,result.age_interval_sum['65岁以上'] if result.age_interval_sum.get('65岁以上') else 0)
    #省份Top10
    i = 1
    for d in result.province_sum:
        sheet_data.write(i,6, d[0])
        sheet_data.write(i,7, d[1])
        i += 1
    #城市Top10
    i = 1
    for d in result.city_sum:
        if d[0] == '-':
            continue
        sheet_data.write(i,8,d[0])
        sheet_data.write(i,9,d[1])
        i += 1
    #全部年龄
    i = 1
    for d in result.age_sum:
        sheet_data.write(i,10, d[0])
        sheet_data.write(i,11, d[1])
        i += 1
    excel_w.save(excel_file)

def analysisIdInfosFromFile(id_list_files,id_result_file):
    reader = fileinput.input(id_list_files)
    result_str = ''
    result = IdAnalyseResult()
    for line in reader:
        idInfo = calculateIdInfo(line)
        result_str += idInfo.to_string() + '\n'
        #统计有效性总数
        if result.valid_sum.get(idInfo.valid):
            result.valid_sum[idInfo.valid] += 1
        else:
            result.valid_sum[idInfo.valid] = 1
        #跳过无效身份证号
        if not idInfo.valid :
            continue
        #统计性别总数
        if result.sex_sum.get(idInfo.sex):
            result.sex_sum[idInfo.sex] += 1
        else:
            result.sex_sum[idInfo.sex] = 1
        #统计年龄总数
        if result.age_sum.get(idInfo.age):
            result.age_sum[idInfo.age] += 1
        else:
            result.age_sum[idInfo.age] = 1
        #统计年龄区间
        age_interval = getAgeInterval(idInfo.age)
        if result.age_interval_sum.get(age_interval):
            result.age_interval_sum[age_interval] += 1
        else:
            result.age_interval_sum[age_interval] = 1
        #统计省份总数
        if result.province_sum.get(idInfo.address.province_name):
            result.province_sum[idInfo.address.province_name] += 1
        else:
            result.province_sum[idInfo.address.province_name] = 1
        #统计城市总数
        if result.city_sum.get(idInfo.address.city_name):
            result.city_sum[idInfo.address.city_name] += 1
        else:
            result.city_sum[idInfo.address.city_name] = 1
    # 每条记录结果存入文件中
    writer = open(id_result_file, 'wt')
    writer.write(result_str)
    return result

starttime = datetime.datetime.now()
#引入字典文件
province_list = pickle.load(open('pkl/province.pkl', 'rb'))
city_list = pickle.load(open('pkl/city.pkl', 'rb'))
district_list = pickle.load(open('pkl/district.pkl', 'rb'))
#传入身份证列表及返回值列表
id_list_files = ['data/ID_list.txt']
id_result_file = 'result/ID_result.txt'
analyse_result_file = 'result/analyse_result.txt'
analyse_excel_file = 'result/analyse_data.xlsx'

#从文件中获取身份证号码，将每条分析结果存入id_result_file中，并将分析后Map返回
result = analysisIdInfosFromFile(id_list_files,id_result_file)

writeResultToTxt(result,analyse_result_file)
writeResultToExcel(result,analyse_excel_file)

print('共' + str(result.valid_sum[0][1] + result.valid_sum[1][1]) + '条数据')
endtime = datetime.datetime.now()
print('运行时间：' + str((endtime - starttime).seconds) + '秒')