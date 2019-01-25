# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
from openpyxl import Workbook
from openpyxl.compat import range
import time
from .utils import sendEmail


class ArticlePipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return

    def spider_closed(self):
        self.file.close()


class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path
        return item
        pass


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'azjieqw1', 'article_spider', charset='utf8', use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(url_object_id,title,url,create_date,fav_nums) values (%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql,
                            (item["url_object_id"], item["title"], item["url"], item["create_date"], item["fav_nums"]))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MYSQL_USER"],
            password=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider)  # 处理异常

    def handle_error(self, faliure, item, spider):
        # 处理异步插入的异常
        print(faliure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        #根据不同的item构建不同的sql并插入mysql
        insert_sql,params = item.get_insert_sql()
        #print (insert_sql,params)
        cursor.execute(insert_sql,params)


#油化品竞价拍卖
class auctionPipeline(object):
    table_values = []

    def close_spider(self, spider):
        from openpyxl import Workbook
        wb = Workbook()
        sheet = wb.active
        sheet.title = "Sheet"
        tableTitle = ['产品名称', '数量', '仓库', '地区', '竞拍单价', '当前最低报价', '当前最高报价', '总成交数量', '链接','产品名称ID']
        for col in range(len(tableTitle)):
            c = col + 1
            sheet.cell(row=1, column=c).value = tableTitle[col]

        for row in range(len(self.table_values)):
            sheet.append(self.table_values[row])

        if time.localtime(time.time()).tm_hour == 11 and time.localtime(time.time()).tm_min>=50:
            name = time.strftime("%Y-%m-%d") + '神华油化品竞拍上午' + str(time.localtime(time.time()).tm_hour) + '点50分.xlsx'
            wb.save(r"D://share//神华早上文件//" + name)

        elif time.localtime(time.time()).tm_hour == 10 and time.localtime(time.time()).tm_min<50:
            name = time.strftime("%Y-%m-%d") + '神华油化品竞拍上午' + str(time.localtime(time.time()).tm_hour) + '点.xlsx'
            wb.save(r"D://share//神华早上文件//" + name)

        elif time.localtime(time.time()).tm_hour == 10 and time.localtime(time.time()).tm_min >= 50:
            name = time.strftime("%Y-%m-%d") + '神华油化品竞拍上午11点.xlsx'
            wb.save(r"D://share//神华早上文件//" + name)

        elif time.localtime(time.time()).tm_hour >= 12:
            name = time.strftime("%Y-%m-%d")+'神华油化品竞拍下午'+str(time.localtime(time.time()).tm_hour)+'点45分.xlsx'
            wb.save(r"D://share//神华早上文件//"+name)
            #运行完成发送邮件
            # result_path = "D://share//神华早上文件//"+name
            # result_name = name
            # sendEmail.mail(result_path, result_name)


    def process_item(self, item, spider):
        i = {
            'name':None,'quantity':0,'warehouse':0,'district':None,'price':0,
            'minBidUnitPrice':0,'maxBidUnitPrice':0,'dealQty':0,'url':None,'name_id':None
        }

        merged_item = {**i, **item}
        datacell = [merged_item['name'], merged_item['quantity'], merged_item['warehouse'],merged_item['district'],merged_item['price'], merged_item['minBidUnitPrice'], merged_item['maxBidUnitPrice'], merged_item['dealQty'],merged_item['url'],merged_item['name_id']]
        self.table_values.append(datacell)
        return item

