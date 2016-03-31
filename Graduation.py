#coding:utf-8

import MySQLdb
import os
import re
import global_list
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )





def is_chinese(char):
    """判断一个unicode是否是汉字"""
    if char>=u'\u4e00' and char<=u'\u9fa5':
        return True
    else:
        return False


def rest_string(string,right_match):
    if string.find(right_match)>=0:
        string=string[:string.find(right_match)]+string[(string.find(right_match)+len(right_match)):]
    return string
    

def quote_buffer(buf):  
    """ 
    chinese to mysql 
    """  
    retstr = ''.join(map(lambda c:'%02x'%ord(c), buf))  
    retstr = "x'" + retstr + "'"  
    return retstr


def ask(foodname,material_name,material_weight,material_unit):
    judge=raw_input('信息提取是否正确？y/n：'.decode('utf-8').encode('gbk'))
    if judge!='n':
        global_list.match_right+=1                                 #发现知识中的准确率
        global_list.final_result[foodname].setdefault(material_name,[])
        global_list.final_result[foodname][material_name].append(material_weight)
        global_list.final_result[foodname][material_name].append(material_unit)
        global_list.normal_material_name.append(material_name)
        global_list.normal_material_unit.append(material_unit)
        return 0
    else:
        DO=raw_input("您希望如何修正错误？1、直接输入修正值 2、添加新的正则式 3、跳过此项：".decode('utf-8').encode('gbk'))
        if DO=='1':
            global_list.knowledge_total+=1
            ren=raw_input("您需要依次输入名称，重量，单位：".decode('utf-8').encode('gbk'))
            ren=ren.decode('gbk').split(u'，')
            material_name=ren[0]
            material_weight=ren[1]
            material_unit=ren[2]
            global_list.final_result[foodname].setdefault(material_name,[])
            global_list.final_result[foodname][material_name].append(material_weight)
            global_list.final_result[foodname][material_name].append(material_unit)
            global_list.normal_material_name.append(material_name)
            global_list.normal_material_unit.append(material_unit)
            return 1
        elif DO=='2':
            REG=eval(raw_input("请输入您需要添加的正则式：".decode('utf-8').encode('gbk')))
            regular_list.append(REG)
            f=open(r'C:\Users\81412\Desktop\GPNOW\code\regular_add.txt','w+')
            f.write(str(REG)+'\n')
            f.close()
            return 2
        else:
            return 3

def result_ask(foodname):
    DO=raw_input("您希望如何修正错误？1、输入n项修正值(输入n值) 2、添加新的正则式(输入“new”)：".decode('utf-8').encode('gbk'))
    if DO=='new':
        REG=eval(raw_input("请输入您需要添加的正则式：".decode('utf-8').encode('gbk')))
        regular_list.append(REG)
        f=open(r'C:\Users\81412\Desktop\GPNOW\code\regular_add.txt','w+')
        f.write(str(REG)+'\n')
        f.close()
        return REG
    else:
        for i in range(int(DO)):
            global_list.knowledge_total+=1
            ren=raw_input("您需要依次输入名称，重量，单位：".decode('utf-8').encode('gbk'))
            ren=ren.decode('gbk').split(u'，')
            global_list.final_result[foodname].setdefault(ren[0],[])
            global_list.final_result[foodname][ren[0]].append(ren[1])
            global_list.final_result[foodname][ren[0]].append(ren[2])
            global_list.normal_material_name.append(material_name)
            global_list.normal_material_unit.append(material_unit)
        return 2


def compute(result,reg_string):
    List=list()
    if reg_string[0]==u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+、)+([\u4e00-\u9fa5]+)各(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)?([\u4e00-\u9fa5]+|g|cc|CC|oz))':
        for i in result:
            if re.match(u'(([\u4e00-\u9fa5]+、)+([\u4e00-\u9fa5]+)各(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',i[0]):
                mid=i[0].split(u'、')
                name=mid[:len(mid)-1]
                name.append(i[2])
                weight=i[3]
                unit=i[4]
                for k in name:
                    List.append((i[0],k,weight,unit))
            elif re.match(u'(([\u4e00-\u9fa5]+、)+([\u4e00-\u9fa5]+)各([\u4e00-\u9fa5]+|g|cc|CC|oz))',i[0]):
                p=i[0].split(u'、')
                num=len(p)
                t=re.compile(u'各')
                q=t.split(p[num-1])
                weight=global_list.default_weight.get(q[1])
                unit=u'克'
                name=p[:num-1]
                name.append(q[0])
                for k in name:
                    List.append((i[0],k,weight,unit))
    if reg_string[0]==u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+，)+([\u4e00-\u9fa5]+)各(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))':
        for i in result:
            mid=i[0].split(u'、')
            name=mid[:len(mid)-1]
            name.append(i[2])
            weight=i[3]
            unit=i[4]
            for k in name:
                List.append((i[0],k,weight,unit))
    if reg_string[0]==u'(([\u4e00-\u9fa5]+)(?<!各)(适量|少许|少量|微量))':  
        for i in result:
            name=i[1]
            weight=global_list.default_weight.get(i[2])
            unit=u'克'
            List.append((i[0],name,weight,unit))
    if reg_string[0]==u'(([\u4e00-\u9fa5]+:)+[\u4e00-\u9fa5]+=((\d+\.\d+|\d+):)+(\d+\.\d+|\d+))':
        for i in result:
            mid=i[0].split(u'=')
            name=mid[0].split(u':')
            weight=mid[1].split(u':')
            weight=[int(l) for l in weight]
            weight=[100*m/sum(weight) for m in weight]
            unit=u'克'
            for k in range(len(name)):
                List.append((i[0],name[k],weight[k],unit))
    if reg_string[0]==u'((?<!\d)([\u4e00-\u9fa5]+、)+([\u4e00-\u9fa5]+)（各(半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)）)':
        for i in result:
            weight=i[3]
            unit=i[4]
            mid=i[0].split(u'、')
            name=mid[:len(mid)-1]
            name.append(i[2])
            for k in name:
                List.append((i[0],k,weight,unit))
    if reg_string[0]==u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+、)+([\u4e00-\u9fa5]+)(?<!各)(适量|少许|少量|微量))':
        for i in result:
            mid=i[0].split(u'、')
            name=mid[:len(mid)-1]
            name.append(i[2])
            weight=global_list.default_weight.get(i[3])
            unit=u'克'
            for k in name:
                List.append((i[0],k,weight,unit))
    if reg_string[0]==u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+，)+([\u4e00-\u9fa5]+)各(适量|少许|少量|微量))':
        for i in result:
            mid=i[0].split(u'，')
            name=mid[:len(mid)-1]
            name.append(i[2])
            weight=global_list.default_weight.get(i[3])
            unit=u'克'
            for k in name:
                List.append((i[0],k,weight,unit))
    if reg_string[0]==u'(([\u4e00-\u9fa5]+)：(适量|少许|少量|微量))':
        for i in result:
            name=i[1]
            weight=global_list.default_weight.get(i[2])
            unit=u'克'
            List.append((i[0],name,weight,unit))
    if reg_string[0]==u'((葱姜|姜葱)各(\d+\/\d+|\d+\.\d+|\d+)克)':
        weight=result[0][2]
        List.append((result[0][0],u'葱',weight,u'克'))
        List.append((result[0][0],u'姜',weight,u'克'))
    if reg_string[0]==u'(([\u4e00-\u9fa5]+)(\d+)([\u4e00-\u9fa5]+)（每\W+(\d+\/\d+|\d+\.\d+|\d+)([\u4e00-\u9fa5]+|g|cc|CC|oz)）)':
        for i in result:
            name=i[1]
            weight=int(i[2])*int(i[4])
            unit=i[5]
            List.append((i[0],name,weight,unit))
    if reg_string[0]==u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+、)+各(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))':
        for i in result:
            mid=i[0].split(u'、')
            name=mid[:len(mid)-1]
            weight=i[2]
            unit=i[3]
            for k in name:
                List.append((i[0],k,weight,unit))
    if reg_string[0]==u'(([\u4e00-\u9fa5]+)(一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+)半)':
        DICT={u'一':1,u'二':2,u'三':3,u'四':4,u'五':5,u'六':6,u'七':7,u'八':8,u'九':9,u'十':10}
        for i in result:
            name=i[1]
            unit=i[3]
            weight=DICT.get(i[2])+0.5
            List.append((i[0],name,weight,unit))
    return List










conn=MySQLdb.connect("localhost","root","loveqi0726","caipu",use_unicode = 1, charset='utf8')
cursor=conn.cursor()
sql="select 原料 from cookbook where 菜谱ID>%d and 菜谱ID<=%d;"% (6000,6195)
cursor.execute(sql)
material=cursor.fetchall()
sql="select 菜谱名称 from cookbook where 菜谱ID>%d and 菜谱ID<=%d;"% (6000,6195)
cursor.execute(sql)
food_name=cursor.fetchall()
sql="select 原料名称 from material;"
cursor.execute(sql)
normal_mname=cursor.fetchall()
sql="select 单位 from material;"
cursor.execute(sql)
normal_uname=cursor.fetchall()


#首项为正则表达式，随后依次是：是否需要进一步计算标志位（为0不需要，为1需要）、名称、重量、单位        水一杯半     
regular_list=[[u'((?<!\d)([\u4e00-\u9fa5]+)，([\u4e00-\u9fa5]+，)*([\u4e00-\u9fa5]+)?(\d+\.\d+|\d+)([\u4e00-\u9fa5]+))',0,1,4,5],\
              [u'((?<!\d)([\u4e00-\u9fa5]+)(?<!细碎)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)(?!\d)(（\W+）)?)',0,1,2,3],\
              [u'((?<!\d)([\u4e00-\u9fa5]+)(细碎)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+)(?!\d)(（\W+）)?)',0,1,3,4],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+)-(\d+\/\d+|\d+\.\d+|\d+)([\u4e00-\u9fa5]+))',0,1,2,4],\
              [u'(([\u4e00-\u9fa5]+)约(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|ml|g|cc|CC|oz))',0,1,2,3],\
              [u'(([\u4e00-\u9fa5]+)：(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|ml|g|cc|CC|oz))',0,1,2,3],\
              [u'(([\u4e00-\u9fa5]+) ... (\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',0,1,2,3],\
              [u'(([\u4e00-\u9fa5]+)…(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',0,1,2,3],\
              [u'(([\u4e00-\u9fa5]+)或([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',0,2,3,4],\
              [u'(([\u4e00-\u9fa5]+)(\d+[\u4e00-\u9fa5])(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',0,1,3,4],\
              [u'(([\u4e00-\u9fa5]+)(（[\u4e00-\u9fa5]+）)(\d+\/\d+|\d+\.\d+|\d+|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',0,1,3,4],\
              [u'(([\u4e00-\u9fa5]+)\([\u4e00-\u9fa5]+\)(\d+\/\d+|\d+\.\d+|\d+|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',0,1,2,3],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+)\([\u4e00-\u9fa5]+\)(\d+\/\d+|\d+\.\d+|\d+)([\u4e00-\u9fa5]+))',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)（(\d+\/\d+|\d+\.\d+|\d+)([\u4e00-\u9fa5]+|g|cc|CC|oz)）)',0,1,2,3],\
              [u'(([\u4e00-\u9fa5]+)(（(半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+)）))',0,1,3,4],\
              [u'(([\u4e00-\u9fa5]+)(半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+))',0,1,2,3],\
              [u'((\d+\/\d+|\d+\.\d+|\d+|一)(克|两|毫升|只|g|大撮|汤匙|个|粒|大勺|小勺|杯|盎司|份|茶匙|磅|大汤匙)([\u4e00-\u9fa5]+))',0,3,1,2],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz))',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)（[\u4e00-\u9fa5]+(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz)）)',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)\([\u4e00-\u9fa5]+(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz)\))',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)（(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz)[\u4e00-\u9fa5]+）)',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)\((\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz)[\u4e00-\u9fa5]+\))',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)（[\u4e00-\u9fa5]+(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz)[\u4e00-\u9fa5]+）)',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)\([\u4e00-\u9fa5]+(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz)[\u4e00-\u9fa5]+\))',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)（(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz)）)',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)\((\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz)\))',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)，重约(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz))',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)约(\d+\/\d+|\d+\.\d+|\d+)(克|公斤|斤|g|cc|CC|oz))',0,1,4,5],\
              [u'(([\u4e00-\u9fa5]+)（\w+）(\d+|\d+/\d+)(oz))',0,1,2,3],\
              [u'(([\u4e00-\u9fa5]+)：(适量|少许|少量|微量))',1,0,0,0],\
              [u'((葱姜|姜葱)各(\d+\/\d+|\d+\.\d+|\d+)克)',1,0,1,0],\
              [u'(([\u4e00-\u9fa5]+)(?<!各)(适量|少许|少量|微量))',1,0,0,0],\
              [u'(([\u4e00-\u9fa5]+)(一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+)半)',1,0,0,0],\
              [u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+、)+([\u4e00-\u9fa5]+)各(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)?([\u4e00-\u9fa5]+|g|cc|CC|oz))',1,0,0,0],\
              [u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+，)+([\u4e00-\u9fa5]+)各(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',1,0,0,0],\
              [u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+，)+([\u4e00-\u9fa5]+)各(适量|少许|少量|微量))',1,0,0,0],\
              [u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+、)+各(\d+\/\d+|\d+\.\d+|\d+|半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz))',1,0,0,0],\
              [u'((?<!\d)(?<![\u4e00-\u9fa5])([\u4e00-\u9fa5]+、)+([\u4e00-\u9fa5]+)(?<!各)(适量|少许|少量|微量))',1,0,0,0],\
              [u'(([\u4e00-\u9fa5]+:)+[\u4e00-\u9fa5]+=((\d+\.\d+|\d+):)+(\d+\.\d+|\d+))',1,0,0,0],\
              [u'(([\u4e00-\u9fa5]+)(\d+)([\u4e00-\u9fa5]+)（每\W+(\d+\/\d+|\d+\.\d+|\d+)([\u4e00-\u9fa5]+|g|cc|CC|oz)）)',1,0,0,0],\
              [u'((?<!\d)([\u4e00-\u9fa5]+、)+([\u4e00-\u9fa5]+)（各(半|一|二|三|四|五|六|七|八|九|十)([\u4e00-\u9fa5]+|g|cc|CC|oz)）)',1,0,0,0]]

##f_regular=open(r'C:\Users\81412\Desktop\GPNOW\code\regular_add.txt')
##a=f_regular.readlines()
##for qq in a:
##    regular_list.append(qq.strip())
    

for i in normal_mname:
    global_list.normal_material_name.append(i[0])
for i in normal_uname:
    global_list.normal_material_unit.append(i[0])

string=[i[0] for i in material]
FoodName=[i[0] for i in food_name]
#*************************循环分析每一句原料文本***************************************************
for i in range(len(string)):
    s=string[i]
    if s==None:
        continue
    startlen=len(s)
    foodname=FoodName[i]
    global_list.final_result.setdefault(foodname,{})    #利用字典模拟一个二维数组，存储每个菜式对应原料的属性，例如final_result[馄饨][馄饨皮]对应记录了“馄饨皮”
                                                        #的重量和单位
    print '\n'+s.decode('utf-8').encode('gbk','ignore')+'\n'
    reg=[m for m in regular_list]                       #待匹配的正则式队列
    right_match_part=list()
    while True:
        if len(reg)==0:                                 #没有待匹配的正则式则跳出循环
            if len(s)==startlen:
                break
            sign=0
            for char in s:
                if is_chinese(char):
                    sign=1
                    break
            if sign==0:                                 #如果剩余字符中没有中文字符则默认匹配工作完成
                break
            else:
                print u"还未匹配的字符串：".decode('utf-8').encode('gbk','ignore')+s.decode('utf-8').encode('gbk','ignore')
                J=raw_input("此文本提取是否完结？y/n：".decode('utf-8').encode('gbk'))
                if J!='n':
                    break
                else:
                    num=result_ask(foodname)                    #询问用户下一步操作
                    if num==2:
                        break
                    else:
                        reg.append(num)
                        continue
            
        else:
            reg_string=reg.pop()
            result=re.compile(reg_string[0]).findall(s)
            temp=list()
            if len(result)>0:
#*************************从匹配式中提取文本信息**************************************************
                if reg_string[1]==0:                        #不需要进一步计算，直接提取信息
                    for p in result:
                        match_string=p[0]
                        material_name=p[reg_string[2]]
                        material_weight=p[reg_string[3]]
                        material_unit=p[reg_string[4]]
                        temp.append((match_string,material_name,material_weight,material_unit))
                    
                else:                                       #需要进一步计算
                    temp.extend(compute(result,reg_string))
            else:
                continue
#*************************判断信息是否正确********************************************************
            for t in temp:
                global_list.knowledge_find+=1                 #发现的知识量
                global_list.knowledge_total+=1
                match_string=t[0]
                material_name=t[1]
                material_weight=t[2]
                material_unit=t[3]
                if material_name[-2:]==u'少许':
                    continue
                if material_name in global_list.normal_material_name and material_unit in global_list.normal_material_unit and material_weight!=None:
                    num=0
                    global_list.match_right+=1                                 #发现知识中的准确率
                    global_list.final_result[foodname].setdefault(material_name,[])
                    global_list.final_result[foodname][material_name].append(material_weight)
                    global_list.final_result[foodname][material_name].append(material_unit)
                else:
                    print u'当前匹配的正则式：%s'%(reg_string)
                    print u'当前匹配的字符串：%s'%(match_string)
                    print u'当前提取的信息：名称：%s 重量：%s 单位：%s'%(material_name,material_weight,material_unit)
                    num=ask(foodname,material_name,material_weight,material_unit)
                if num==0 or num==1:
                    s=rest_string(s,match_string)
                print '\n'
    print '\n\n'
#*************************提取信息的输出和统计***************************************************
    a=open(r'C:\Users\81412\Desktop\GPNOW\code\result5.txt','a')
    for k in global_list.final_result[foodname].keys():
        material_name=k
        material_weight=global_list.final_result[foodname][material_name][0]
        material_unit=global_list.final_result[foodname][material_name][1]
        a.write(str(foodname)+'\t'+str(material_name)+'\t'+str(material_weight)+'\t'+str(material_unit)+'\n')
        cursor.execute("insert into material(菜谱名称,原料名称,重量,单位) values(%s,%s,%s,%s);",(foodname,material_name,material_weight,material_unit))
        conn.commit()
    b=open(r'C:\Users\81412\Desktop\GPNOW\code\ratio.txt','w')
    b.write(str(global_list.knowledge_total)+'\t'+str(global_list.knowledge_find)+'\t'+str(global_list.match_right)+'\n')
    a.close()
    b.close()
    

cursor.close()
conn.close()






##a=open(r'C:\Users\81412\Desktop\GPNOW\code\result.txt','w+')
##for i in global_list.final_result.keys():
##    food_name=i
##    for j in global_list.final_result[i].keys():
##        global_list.knowledge_total+=1
##        material_name=j
##        material_weight=global_list.final_result[i][j][0]
##        material_unit=global_list.final_result[i][j][1]
##        a.write(str(food_name)+'\t\t'+str(material_name)+'\t\t'+str(material_weight)+'\t\t'+str(material_unit)+'\n')
##b=open(r'C:\Users\81412\Desktop\GPNOW\code\ratio.txt','w+')
##b.write(str(global_list.knowledge_total)+'\t'+str(global_list.knowledge_find)+'\t'+str(global_list.match_right)+'\n')
##a.close()
##b.close()
            
    

        






