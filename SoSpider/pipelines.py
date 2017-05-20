# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import uuid
import logging

from elasticsearch import helpers
from elasticsearch.serializer import JSONSerializer


BUF_SIZ = 50

class SospiderPipeline(object):
    items_buffer = []
    serializer = JSONSerializer()

    def process_item(self, item, spider):
        data = dict(item)
        url_key = spider.url_key(item['url'])
        #if spider.redis_cache.exists(url_key):
        #    return item
        #else:
        #    spider.redis_cache.set(url_key, item['url'])
        #    spider.redis_cache.expire(url_key,
        #                              spider.conf_dict['expire_seconds'])
        extra_data = data.pop('extra')
        data.update(extra_data)
        self.index_item(data, spider)
        return item

    def index_item(self, item, spider):
        index_action = {
            '_index': spider.es_index,
            '_type': 'fulltext',
            '_source': item,
            '_id': uuid.uuid1(),
        }
        logging.info('get %s' % item['url'])
        try:
            self.serializer.dumps(index_action)
            self.items_buffer.append(index_action)
        except Exception as e:
            logging.info('dumps failed')
        if len(self.items_buffer) > BUF_SIZ:
            self.send_item(spider)
            self.items_buffer = []

    def send_item(self, spider):
        res = helpers.bulk(spider.es, self.items_buffer)
        logging.info('bulk %s' % str(res))

    def close_spider(self, spider):
        if len(self.items_buffer):
            self.send_item()
