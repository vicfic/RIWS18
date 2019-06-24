# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompeticionesItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class Competicion(scrapy.Item):
    """ Defines the Competition fields """
    url = scrapy.Field()
    urlCartel = scrapy.Field()
    nombre = scrapy.Field()
    provincia = scrapy.Field()
    comunidadAutonoma = scrapy.Field()
    pais = scrapy.Field()
    organizador = scrapy.Field()
    modalidad = scrapy.Field()
    distancia = scrapy.Field()
    fecha = scrapy.Field()
    participantes = scrapy.Field()
    superficie = scrapy.Field()
    lugar = scrapy.Field()
    web = scrapy.Field()
    descripcion = scrapy.Field()