# -*- coding: utf-8 -*-
import scrapy
from urllib import parse
from scrapy.http import Request
from scrapy import FormRequest
from article.items import auctionItemLoader,auctionItem
import pandas as pd


class AuctionspiderSpider(scrapy.Spider):
    name = 'auctionSpider'
    allowed_domains = ['www.e-shenhua.com']
    start_urls = ['https://www.e-shenhua.com/ec/auction/oilAuctionList.jsp']
    headers = {
        "Host": "www.e-shenhua.com",
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64;rv: 60.0) Gecko / 20100101Firefox / 60.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q = 0.8",
        "Accept-Language": "zh-CN,zh;q = 0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
        "Accept-Encoding": "gzip, deflate, br"
    }

    post_url = 'https://www.e-shenhua.com/ec/auction/oilAuctionList.jsp?_DARGS=/ec/auction/oilAuctionList.jsp'
    post_data = {
        "/com/shenhua/commerce/auction/OilAuctionListSearchFormHandler.pageNum": "1",
        "/com/shenhua/commerce/auction/OilAuctionListSearchFormHandler.pageSize": "10",
        "/com/shenhua/commerce/auction/OilAuctionListSearchFormHandler.search": "搜索",
        "sortOrder": "desc",
        "sortProp": "pt.deposit_deadline",
        "_D:/com/shenhua/commerce/auction/OilAuctionListSearchFormHandler.pageNum": "+",
        "_D:/com/shenhua/commerce/auction/OilAuctionListSearchFormHandler.pageSize": "+",
        "_D:/com/shenhua/commerce/auction/OilAuctionListSearchFormHandler.search": "+"
    }

    def start_requests(self):
        for url in self.start_urls:
            yield FormRequest(url=self.post_url, formdata=self.post_data, headers=self.headers, callback=self.parse)


    def parse(self, response):
        urls = response.xpath("//table[@class='table expandable table-striped']/tbody//tr//a[@href]/text()").extract()
        prices = response.xpath("//table[@class='table expandable table-striped']//tbody/tr/td[6]/text()").extract()
        for i in range(len(urls)):
             url = "https://www.e-shenhua.com/ec/auction/english/englishAuctionDetail.jsp?productId="+urls[i].strip()
             yield Request(url,headers=self.headers,callback=self.parse_detail,meta={"price":prices[i]}) #parse.urljoin(response.url,urls[i])

        next_page = response.xpath("//table[@class='table expandable table-striped']/thead//ul/li//a[contains(text(),'下一页')]/@onclick").extract()

        if next_page.__len__() != 0:
            next = int(self.post_data["/com/shenhua/commerce/auction/OilAuctionListSearchFormHandler.pageNum"])+1
            self.post_data["/com/shenhua/commerce/auction/OilAuctionListSearchFormHandler.pageNum"] = str(next)
            yield FormRequest(url=self.post_url, formdata=self.post_data, headers=self.headers, callback=self.parse)
        pass

    def parse_detail(self, response):
        df = pd.read_excel("C://Users//lyz//Desktop//地区分类.xlsx")
        auction_item = auctionItem()
        item_loader = auctionItemLoader(item=auctionItem(),response=response)
        item_loader.add_value("url",response.url)
        item_loader.add_xpath("name","//div[@id='content-products-info']/table/tbody/tr[1]/td[1]//text()")
        name_id = response.xpath("//*[@id='skuId']/option/@value").extract()[0]
        item_loader.add_value("name_id",name_id)
        quantity = response.xpath("//div[@id='content-products-info']/table/tbody/tr[1]/td[3]/text()").extract()[0]
        item_loader.add_xpath("warehouse", "//div[@id='content-transaction-info']/table/tbody/tr[3]/td[2]/text()")
        unit = response.xpath("//div[@id='content-products-info']/table/tbody/tr[1]/td[3]/span/text()").extract()[0]
        if unit == '吨':
            item_loader.add_value("quantity",[quantity])
            item_loader.add_value("price",response.meta.get("price",""))
            maxBidUnitPrice = response.xpath("//*[@id='maxBidUnitPrice']/span/text()")
            minBidUnitPrice = response.xpath("//*[@id='minBidUnitPrice']/span/text()")
            if len(minBidUnitPrice)==0 and len(maxBidUnitPrice)!= 0 and float(maxBidUnitPrice.extract()[0].replace(',',''))!=0:
                dealQty = quantity
                item_loader.add_value("maxBidUnitPrice", maxBidUnitPrice.extract()[0].replace(',',''))
                item_loader.add_value("dealQty", dealQty)
            else:
                item_loader.add_xpath("maxBidUnitPrice", "//*[@id='maxBidUnitPrice']/span/text()")
                item_loader.add_xpath("minBidUnitPrice", "//*[@id='minBidUnitPrice']/span/text()")
                item_loader.add_xpath("dealQty", "//*[@class='dealQtySpan']/text()")

        elif unit == '公斤':
            quantity = float(quantity.strip().replace(',',''))//1000
            item_loader.add_value("quantity", quantity)
            price = float(response.meta.get("price","").strip().replace(',',''))*1000
            item_loader.add_value("price", price)
            maxBidUnitPrice = response.xpath("//*[@id='maxBidUnitPrice']/span/text()")
            minBidUnitPrice = response.xpath("//*[@id='minBidUnitPrice']/span/text()")
            if len(minBidUnitPrice) == 0 and len(maxBidUnitPrice) != 0 and float(maxBidUnitPrice.extract()[0].replace(',', '')) != 0:
                dealQty = quantity
                maxBidUnitPrice = float(response.xpath("//*[@id='maxBidUnitPrice']/span/text()").extract()[0].replace(',', '')) * 1000
                item_loader.add_value("maxBidUnitPrice", maxBidUnitPrice)
                item_loader.add_value("dealQty", dealQty)
            else:
                maxBidUnitPrice = float(response.xpath("//*[@id='maxBidUnitPrice']/span/text()").extract()[0].replace(',', '')) * 1000
                minBidUnitPrice = float(response.xpath("//*[@id='minBidUnitPrice']/span/text()").extract()[0].replace(',', '')) * 1000
                item_loader.add_value("maxBidUnitPrice", maxBidUnitPrice)
                item_loader.add_value("minBidUnitPrice", minBidUnitPrice)
                dealQty = float(response.xpath("//*[@class='dealQtySpan']/text()").extract()[0].strip().replace(',',''))//1000
                item_loader.add_value("dealQty", dealQty)
        try:
            warehouse = item_loader._values['warehouse'][0]
            district = df.get_value(warehouse,'地区')
            item_loader.add_value("district", district)
        except:
            item_loader.add_value("district",None)

        auction_item = item_loader.load_item()
        yield auction_item


