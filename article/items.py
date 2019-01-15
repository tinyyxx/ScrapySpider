# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy,datetime,re
from scrapy.loader.processors import MapCompose,TakeFirst,Join
from scrapy.loader import ItemLoader
from w3lib.html import remove_tags
from article.settings import SQL_DATETIME_FORMAT, SQL_DATE_FORMAT

def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y/%m/%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0

    return nums


def remove_comment_tags(value):
    if '评论' in value:
        return ""
    else:
        return value


def return_value(value):
    if value == ' ':
        return value
    elif type(value)==type(1.234):
        return value
    else:
        return value.strip().replace(",","")


class JobBoleArticleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field(
       # input_process = MapCompose(a)
    )
    create_date = scrapy.Field(
        input_processor = MapCompose(date_convert),
        output_processor = TakeFirst()
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        output_processor = MapCompose(return_value)
    )
    front_image_path = scrapy.Field()
    thumbsUp_nums = scrapy.Field(
        input_processor = MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor = MapCompose(remove_comment_tags),
        output_processor = Join(',')
    )
    content = scrapy.Field()

    pass


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()


def remove_slash(value):
    return value.replace("/","")

def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip()!="查看地图"]
    return "".join(addr_list)


class LagouJobItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field(

    )
    salary = scrapy.Field()
    job_city = scrapy.Field(
        input_processor = MapCompose(remove_slash),
    )
    work_years = scrapy.Field(
        input_processor=MapCompose(remove_slash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(remove_slash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field(
        input_processor=MapCompose(remove_tags),
    )
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags,handle_jobaddr),
    )
    company_name = scrapy.Field(
        input_processor=MapCompose(return_value)
    )
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(',')
    )
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = ("\n"
                      "            insert into lagou_job(title,url,salary,url_object_id,job_city,work_years,degree_need,job_type,publish_time,job_advantage,\n"
                      "            job_desc,job_addr,company_name,company_url,tags,crawl_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)\n"
                   #   "            ON DUPILICATE KEY UPDATE salary=VALUES(salary),job_desc=VALUES(job_desc)\n"
                      "               ")
        params = (
            self['title'],self['url'],self['salary'],self['url_object_id'],self['job_city'],self['work_years'],self['degree_need'],self['job_type'],
            self['publish_time'],self['job_advantage'],self['job_desc'],self['job_addr'],self['company_name'],self['company_url'],self['tags'],
            self['crawl_time'].strftime(SQL_DATETIME_FORMAT)
        )
        return insert_sql,params


class LagouJobItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    pass





#油化品竞价拍卖item
def str_to_float(value):
    try:
        return float(value)
    except:
        return value

class auctionItem(scrapy.Item):
    name = scrapy.Field()
    quantity = scrapy.Field(
        input_processor=MapCompose(return_value,str_to_float)
    )
    warehouse = scrapy.Field(
        input_processor=MapCompose(return_value)
    )
    district = scrapy.Field()
    url = scrapy.Field()
    price = scrapy.Field(
        input_processor=MapCompose(return_value,str_to_float)
    )
    maxBidUnitPrice = scrapy.Field(
        input_processor=MapCompose(return_value,str_to_float)
    )
    minBidUnitPrice = scrapy.Field(
        input_processor=MapCompose(return_value,str_to_float)
    )
    dealQty = scrapy.Field(
        input_processor=MapCompose(return_value,str_to_float)
    )
    name_id = scrapy.Field()
    pass


class auctionItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
    pass