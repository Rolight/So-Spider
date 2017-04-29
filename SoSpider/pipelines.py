# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import uuid
from elasticsearch import Elasticsearch


class SospiderPipeline(object):

    def process_item(self, item, spider):
        data = dict(item)
        extra_data = data.pop('extra')
        data.update(extra_data)
        es = Elasticsearch()
        es.indices.create(index=spider.es_index, ignore=400)
        es.create(
            index=spider.es_index,
            doc_type='fulltext',
            id=uuid.uuid1(),
            body=data
        )
        return item
