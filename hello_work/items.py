# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class HelloWorkItem(scrapy.Item):
    company_name = scrapy.Field()
    employment_status = scrapy.Field()
    business_number = scrapy.Field()
