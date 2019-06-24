# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pysolr
from scrapy.conf import settings
from scrapy.exceptions import DropItem

class CompeticionesPipeline(object):
    def __init__(self):
        self.mapping = settings['SOLR_COMPETICIONES_MAPPING'].items()
        self.ignore_duplicates = settings['SOLR_IGNORE_COMPETICIONES_DUPLICATES'] or False
        self.ids_seen = set()
        if self.ignore_duplicates and self.ids_seen is None:
            raise RuntimeError(
                'To ignore duplicates SOLR_IGNORE_COMPETICIONES_DUPLICATES and ids_seen has to be defined')
        self.solr = pysolr.Solr(settings['SOLR_URL'], timeout=10)

    def process_item(self, item, spider):
        if self.ignore_duplicates:
            if item.get('url') in self.ids_seen:
                raise DropItem("Duplicate item found: %s" % item)
        solr_item = {}
        for dst, src in self.mapping:
            solr_item[dst] = self.__get_item_value__(item, src)
        self.solr.add([solr_item])
        self.ids_seen.add(item.get('url'))
        return item

    def __get_item_value__(self, item, src):
        if type(src) is str:
            return item[src] if src in item else None
        elif type(src) is list:
            return [item[i] if i in item else None for i in src]
        else:
            raise TypeError('Only string and list are valid mapping source')
