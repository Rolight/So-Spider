# -*- coding: utf-8 -*-
import json
import scrapy
import time

from pprint import pprint
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from SoSpider.items import SospiderItem, clear_text


class GenericSpiderSpider(CrawlSpider):
    name = 'generic_spider'

    def __init__(self, *args, **kwargs):
        self.__dict__.update(kwargs)
        config = json.loads(self.config)
        # base config
        self.allowed_domains = config.get('allowed_domains')
        self.start_urls = config.get('start_urls')
        self.download_delay = config.get('sleep', 0)
        # rules config
        parse_url_rules = config.get('parse_url_rules', ['.*'])
        walk_url_rules = config.get('walk_url_rules', ['.*'])
        rules = [
            Rule(
                LinkExtractor(allow=parse_url_rule),
                callback='parse_item',
            )
            for parse_url_rule in parse_url_rules
        ]
        if walk_url_rules != parse_url_rules:
            rules += [
                Rule(
                    LinkExtractor(allow=walk_url_rule),
                    follow=True,
                )
                for walk_url_rule in walk_url_rules
            ]
        self.rules = tuple(rules)
        # selector config
        self.title_xpath = config.get('title_selector', '//head//title')
        self.content_xpath = config.get('content_selector', 'body')
        self.extra_selectors = config.get('custom_selectors', [])
        super(GenericSpiderSpider, self).__init__(*args, **kwargs)

    def get_item(self, response, xpath):
        text = response.xpath(xpath).extract_first()
        return clear_text(text)

    def parse_item(self, response):
        item = SospiderItem()
        item['url'] = response.url
        item['timestamp'] = time.time()
        item['title'] = self.get_item(response, self.title_xpath)
        item['content'] = self.get_item(response, self.content_xpath)
        item['extra'] = {}
        for index in self.extra_selectors:
            field_name = index['field_name']
            xpath = index['selector']
            item['extra'][field_name] = self.get_item(response, xpath)
        print('fetched a item:')
        print(item['title'])
        # pprint(dict(item))
        return item
