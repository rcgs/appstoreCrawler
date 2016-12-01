# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from  scrapy import log
import pymysql
import re
from pprint import pprint
from datetime import datetime
import os

class SiePipeline(object):
    cursor =None
    connection = None
    SerialID =None
    EvalID =None
    VerID =None
    first_open =False # パイプラインが初回起動時か同課のフラグ
    last_id = {}
    dbname = "appstore"

    filename =os.getcwd()+ "\\" + "logfile.txt"
    filestream = None

    tables_id ={
        "APT":"titledb",
        "APV":"versiondb",
        "APE":"evaluationdb",
    }

    use_tables ={
        "title":"titledb",
        "ver":"versiondb",
        "eval":"evaluationdb",
    }
    table_id_1 = "title"
    title_column =[]
    version_column = []
    evaluation_column = []

    test_column =[
        "title",
        "link"
    ]


    def __init__(self):
        #logfile設定
        self.filestream = open(self.filename,"w")        
        #SQL接続
        self.connection = pymysql.connect(
            host="localhost",
            user="root",
            password="root",
            db="appstore",
            charset ="utf8",
            autocommit=True
        )

        #ID設定と件数取得 後で削除
        self.cursor=self.connection.cursor()
        for ID_type in self.tables_id:
            sql = 'SELECT COUNT(*) FROM %s;' % self.tables_id[ID_type]
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            start_number = result[0][0]
            if ID_type == "APT":
                self.SerialID = self.get_ID(start_number,"APT")
            elif ID_type == "APV":
                self.VerID = self.get_ID(start_number,"APV")
            elif ID_type == "APE":
                self.EvalID = self.get_ID(start_number,"APE")
                
        #カラムリストの取得と保持
        for table_name in self.use_tables.values():
            sql = 'SELECT column_name FROM information_schema.columns WHERE table_name = "%s" AND table_schema = "%s";'%(table_name,self.dbname)
            log.msg(sql,level=log.DEBUG)
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            for column_name in result:
                if table_name =="titledb":                    
                    self.title_column.append(column_name[0])
                    #log.msg(pprint(result),level=log.DEBUG)
                    #log.msg(pprint(self.title_column),level=log.DEBUG)
                elif table_name == "versiondb":
                    self.version_column.append(column_name[0])
                    #log.msg(pprint(result),level=log.DEBUG)
                    #log.msg(pprint(self.version_column),level=log.DEBUG)
                elif table_name =="evaluationdb":
                    self.evaluation_column.append(column_name[0])
                    #log.msg(pprint(result),level=log.DEBUG)
                    #log.msg(pprint(self.evaluation_column),level=log.DEBUG)

    def process_item(self, item, spider):
        item["serialID"]=self.SerialID()
        item["serialVID"]=self.VerID()
        item["serialEID"]=self.EvalID()
        self.insert_data_re(item,"title")
        log.msg(pprint(self.evaluation_column),level=log.DEBUG)
        self.insert_data_re(item,"eval")


        #title = str(item["title"])
        #title = re.sub(r"[~\[\']", "", title)
        #title = re.sub(r"[\'\]$]", "", title)
        #link = str(item["link"])
        #link = re.sub(r"[~\[\']", "", link)
        #link = re.sub(r"[\'\]$]", "", link)

        #sql = ('INSERT INTO %s (title, url) VALUES ("%s","%s");' %  (use_table,title,link)).encode("utf8")


        #self.cursor.execute(sql)
        
        return item


    def update_data_re(self,item,type,*where):
        tablename = None
        columlist = None
        #テーブルにより処理を分岐
        if type == "title":
            tablename = self.use_tables["title"]
            columlist = self.title_column 
        elif type == "ver":
            tablename = self.use_tables["ver"]
            columlist = self.version_column
        elif type == "eval":
            tablename = self.use_tables["eval"]
            columlist = self.evaluation_column
        elif type == "test":
            tablename = self.use_tables["test"]
            columlist = self.test_clumn
        else:
            return false
        #SQL文生成
        sql ='UPDATE ' 
        sql += tablename
        
        sql += " SET "
        for num in range(0,len(columlist)):
            if columlist[num] == "SerialID": continue #更新処理の場合　シリアルIDの処理をスキップ
            #型判定分岐処理
            temp =None
            sql += columlist[num] + "="
            if isinstance(item[columlist[num]],str): #文字列
                temp = "'" + item[columlist[num]] + "'"
            else :
                temp = str(item[columlist[num]]) #数字
            sql += temp
            
            if num != len(columlist)-1: sql += ", "
            
                    
            #クエリ挿入処理  
        sql += " "

        sql += 'WHERE '
        for num in range(0,len(where)):
            if isinstance(item[where[num]],str): #文字列
                temp = "'" + item[where[num]] + "'"
            else :
                temp =  str(item[where[num]]) #数字        
            sql += where[num] + "=" + temp 

            if num != len(where)-1: sql += " and "   
        sql += ";"
        log.msg(" update" + sql,level = log.DEBUG)
        try:
            resultNumber=self.cursor.execute(sql)
            #if (resultNumber != 2):
                #raise Exception("error mysql")            
        except:
            
            self.filestream.write(pprint(item))
            

    def insert_data_re(self,item,type):
        tablename = None
        columlist = None
        #テーブルにより処理を分岐
        if type == "title":
            tablename = self.use_tables["title"]
            columlist = self.title_column 
        elif type == "ver":
            tablename = self.use_tables["ver"]
            columlist = self.version_column
        elif type == "eval":
            tablename = self.use_tables["eval"]
            columlist = self.evaluation_column
        elif type == "test":
            tablename = self.use_tables["test"]
            columlist = self.test_clumn
        else:
            return false
        #SQL文生成
        sql ='INSERT INTO ' 
        sql += tablename
        sql += " ("
        
        for num in range(0,len(columlist)):
            
            if num == len(columlist)-1: sql += columlist[num]
            else: sql += columlist[num] + ", "
        sql += ")"
        sql += " VALUES ("
        for num in range(0,len(columlist)):
            #型判定分岐処理
            temp =None                  
            if isinstance(item[columlist[num]],str):
                temp = "'" + item[columlist[num]] + "'"
            else :
                temp =  str(item[columlist[num]])
            #クエリ挿入処理  
            if num == len(columlist)-1:sql += temp 
            else: sql +=   temp + ", "
        sql += ");"

        log.msg("insert" + sql,level = log.DEBUG)
        try:
            resultNumber=self.cursor.execute(sql)
            #if (resultNumber != 1):
                #raise Exception("error mysql")
        except:
            self.filestream.write(pprint(sql)+"\n")
            
    def get_ID(self,last_number,IDname="AP"):#一つ前の件数を取得し代入
        num =last_number
        ID_type = IDname
        
        def closure():
            nonlocal num
            nonlocal ID_type

            max_size = 12 #桁の最大数 
            num +=1 #インクリメント

            strnum = str(num)#文字列として保存
            for var in range(0,max_size - len(strnum)): #最大桁数と現在の数字の桁数の差分の回数繰り返し、0で埋める
                strnum = "0" + strnum

            ID = ID_type+strnum
            return ID


        return closure