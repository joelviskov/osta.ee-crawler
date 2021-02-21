# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Field


class OstaCrawlerItem(scrapy.Item):
    id = Field()
    name = Field()
    link = Field()
    price_now = Field()
    price_buy = Field()
    bids = Field()
    category = Field()
    views = Field()
    start_date = Field()
    end_date = Field()
