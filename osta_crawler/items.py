# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class AuctionItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    link = scrapy.Field()
    price_now = scrapy.Field()
    price_buy = scrapy.Field()
    bids = scrapy.Field()
    category = scrapy.Field()
    views = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    description = scrapy.Field()

class CategoryItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    parent_id = scrapy.Field()