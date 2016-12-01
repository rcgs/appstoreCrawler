# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    URL = scrapy.Field()
    title = scrapy.Field()
    maker = scrapy.Field()
    date = scrapy.Field()
    price = scrapy.Field()
    genre = scrapy.Field()
    platform = scrapy.Field()
    style = scrapy.Field()
    rating = scrapy.Field()
    ratecategory = scrapy.Field()
    player = scrapy.Field()
    copyright = scrapy.Field()
    descript = scrapy.Field()
    otherpac = scrapy.Field()
    info = scrapy.Field()
    timestamp = scrapy.Field()
    
    
    pass
