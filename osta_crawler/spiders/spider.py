from osta_crawler.items import OstaCrawlerItem
import scrapy
import re
import datetime
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class SpiderSpider(scrapy.Spider):
    name = 'spider'
    allowed_domains = ['osta.ee']
    start_urls = [
        'https://www.osta.ee/kategooria/audiovideo/mangukonsoolid/konsoolid'
    ]

    def get_date(self, extract):
        regex = re.search(
            '^(?:[ETKNRLP]{1}) (\d{2}).(\d{2}).(\d{4}) (\d{2}):(\d{2}):(\d{2})$', extract)
        if regex is None:
            return None

        day = int(regex.group(1))
        month = int(regex.group(2))
        year = int(regex.group(3))
        hour = int(regex.group(4))
        minute = int(regex.group(5))
        second = int(regex.group(6))
        return datetime.datetime(year, month, day, hour, minute, second)

    def parse_auction(self, response):
        try:
            bids = response.css('span.js-current-bids::text').get()
            if bids is None:
                # We prefer only auctions.
                return

            link = response.request.url

            extracted_price_now = response.css(
                'span.js-current-price::text').get()
            price_now = float(
                extracted_price_now) if extracted_price_now is not None else None

            extracted_price_buy = response.css(
                'p.offer-details__price span::text').get()
            price_buy = float(
                extracted_price_buy) if extracted_price_buy is not None else None

            extracted_start = response.css(
                'table.data-list')[1].css('tr td::text').getall()[1]
            start_date = self.get_date(extracted_start)

            extracted_end = response.css('span.js-date-end::text').get()
            end_date = self.get_date(extracted_end)

            yield OstaCrawlerItem(
                id=re.search('-(\d+).html$', link).group(1),
                name=response.css(
                    'div.header__title-block h1.header-title::text').get(),
                link=link,
                price_now=price_now,
                price_buy=price_buy,
                bids=int(bids),
                category=response.css(
                    'div.breadcrumb span.active::text').get(),
                views=int(response.css('table.data-list')
                          [1].css('tr td::text').getall()[2]),
                start_date=start_date,
                end_date=end_date
            )
        except:
            f = open("errors.txt", "a")
            f.write(f'Failed on {response.request.url}.\n')
            f.close()

    def parse(self, response):
        # Loop through auctions on the page and parse them.
        auction_anchors = response.css('h3.offer-thumb__title a')
        yield from response.follow_all(auction_anchors, callback=self.parse_auction)

        navigation_anchors = response.css('div.page-selector a')
        for anchor in navigation_anchors:
            # Only follow to the next page if the link leads to the next page.
            if anchor.css('span::attr(id)').get() == 'nextPage':
                next_page = anchor.attrib['href']
                yield response.follow(next_page, callback=self.parse)