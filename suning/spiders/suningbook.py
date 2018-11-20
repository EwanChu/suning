# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy


class SuningbookSpider(scrapy.Spider):
    name = 'suningbook'
    allowed_domains = ['suning.com']
    start_urls = ['https://book.suning.com/']

    def parse(self, response):
        # 1.大分类
        li_list = response.xpath("//div[@class='book-skin']//div[@class='menu-list']/div")
        item = {}
        for li in li_list:
            item["b_cast"] = li.xpath(".//h3/a/text()").extract_first()

        # 2.小分类
        for li in li_list:
            item["s_cast"] = li.xpath(".//p/a/text()").extract_first()
            item["s_href"] = li.xpath(".//p/a/@href").extract_first()
            if item["s_href"] is not None:
                yield scrapy.Request(
                    item["s_href"],
                    callback=self.parse_book_list,
                    meta={"item": deepcopy(item)}
                )
        # 3.小小分类
        for li in li_list:
            item["xs_cast"] = li.xpath(".//ul/li/a/text()").extract_first()
            item["xs_href"] = li.xpath(".//ul/li/a/@href").extract_first()
            if item["xs_href"] is not None:
                yield scrapy.Request(
                    item["xs_href"],
                    callback=self.parse_book_list,
                    meta={"item": deepcopy(item)}
                )


    def parse_book_list(self, response):
        item = deepcopy(response.meta["item"])
        # 图书列表页分组
        li_list = response.xpath("//div[@class='search-results clearfix mt10']//div[@id='filter-results']/ul/li")
        for li in li_list:
            item["book_name"] = li.xpath(".//div[@class='res-info']/p[@class='sell-point']/a/@title").extract_first()
            item["book_img"] =li.xpath(".//div[@class='res-img']//img/@src").extract_first()
            item["book_price"] = li.xpath(
                ".//div[@class='res-info']/p[@class='prive-tag']/em/text()").extract_first()
            t = li.xpath(".//div[@class='res-info']/p[@class='sell-point']/a/@href").extract_first()
            item["book_href"] = "https:" + t
            if item["book_href"] is not None:
                yield scrapy.Request(
                    item["book_href"],
                    callback=self.parse_books,
                    meta={"item": deepcopy(item)}
                )
        # 实现翻页功能
        pg_new = int(response.xpath("//div[@class='search-main']//div[@id='bottom_pager']/a[5]/text()").extract_first())
        if response.xpath("//div[@class='search-main']//div[@id='bottom_pager']/a/@id[2]").extract_first() is None:
            url = response.xpath("//div[@class='search-main']//div[@id='bottom_pager']/a[6]/@href").extract_first()
            new_url = "https://list.suning.com" + url
            yield scrapy.Request(
                new_url,
                callback=self.parse_book_list()
            )
        for i in range(2, pg_new):
            url = response.xpath("//div[@class='search-main']//div[@id='bottom_pager']/a[7]/@href").extract_first()
            new_url = "https://list.suning.com" + url
            i += 1
            yield scrapy.Request(
                new_url,
                callback=self.parse_book_list(),
                meta={"item": response.meta["item"]}
            )

    def parse_books(self, response):
        item = response.meta["item"]
        li_list = response.xpath("//div[@class='proinfo-main']/ul")
        for li in li_list:
            item["book_author"] = li.xpath("./li[1]/text()").extract()[0]
            item["book_ph"] = li.xpath("./li[1]/text()").extract()[0]
            item["book_PD"] = li.xpath("./li[1]/text()").extract()[0]
            item["book_briefly"] = response.xpath("//div[@class='tabarea']//div[@id='productDetail']/div/dl[4]/dd/p/text()").extract_first()
        yield item


