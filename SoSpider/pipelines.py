# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import uuid


class SospiderPipeline(object):

    def process_item(self, item, spider):
        data = dict(item)
        extra_data = data.pop('extra')
        data.update(extra_data)
        spider.es.indices.create(index=spider.es_index, ignore=400)
        spider.es.create(
            index=spider.es_index,
            doc_type='fulltext',
            id=uuid.uuid1(),
            body=data
        )
        return item
