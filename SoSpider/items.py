# -*- coding: utf-8 -*-
import scrapy

from bs4 import BeautifulSoup

def clear_text(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

class SospiderItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    extra = scrapy.Field()
    timestamp = scrapy.Field()
