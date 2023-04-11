# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Product(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    price_current = scrapy.Field()
    price_before = scrapy.Field()

    
