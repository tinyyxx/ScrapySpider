# -*- coding: utf-8 -*-
import scrapy


class Auctionspider2Spider(scrapy.Spider):
    name = 'auctionSpider2'
    allowed_domains = ['www.e-shenhua.com']
    start_urls = ['http://www.e-shenhua.com/']

    def parse(self, response):
        pass
