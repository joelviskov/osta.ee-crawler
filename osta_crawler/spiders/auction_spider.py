from osta_crawler.items import AuctionItem
import scrapy
import re
import datetime
import logging
from scrapy.utils.log import configure_logging


class AuctionSpider(scrapy.Spider):
    name = "auction_spider"
    allowed_domains = ["osta.ee"]
    start_urls = [
        "https://www.osta.ee/kategooria/audiovideo/mangukonsoolid?pagesize=180&q%5Bshow_items%5D=1",
    ]

    custom_settings = {
        "FEEDS": {
            "auctions.json": {
                "format": "jsonlines",
                "encoding": "utf8",
                "store_empty": False,
                "fields": None,
                "indent": 4,
                "item_export_kwargs": {
                    "export_empty_fields": True,
                },
            }
        }
    }

    configure_logging(install_root_handler=False)
    logging.basicConfig(filename="log.txt", format="%(levelname)s: %(message)s", level=logging.INFO, filemode="w")

    def parse(self, response):
        # Loop through auctions on the page and parse them.
        auction_anchors = response.css("ul.offers-list h3.offer-thumb__title a")
        yield from response.follow_all(auction_anchors, callback=self.parse_auction)

        navigation_anchors = response.css("div.page-selector a")
        for anchor in navigation_anchors:
            # Only follow to the next page if the link leads to the next page.
            if anchor.css("span::attr(id)").get() == "nextPage":
                next_page = anchor.attrib["href"]
                yield response.follow(next_page, callback=self.parse)

    def parse_auction(self, response):
        try:
            bids = response.css("span.js-current-bids::text").get()
            if bids is None:
                return  # We prefer only auctions.

            link = response.request.url

            breadcrumbs = response.css("div.breadcrumb-item a span::text").getall()
            breadcrumbs.pop(0)  # First is "Kõik kategooriad" which we will not use.

            extracted_price_now = response.css("span.js-current-price::text").get()
            extracted_price_buy = response.css("p.offer-details__price span::text").get()

            extracted_start = response.css("table.data-list")[1].css("tr td::text").getall()[1]
            extracted_end = response.css("span.js-date-end::text").get()

            yield AuctionItem(
                id=re.search("-(\d+).html$", link).group(1),
                name=response.css("div.header__title-block h1.header-title::text").get(),
                description=response.css("div.offer-details__description").get(),
                link=link,
                price_now=float(extracted_price_now) if extracted_price_now is not None else None,
                price_buy=float(extracted_price_buy) if extracted_price_buy is not None else None,
                bids=int(bids),
                category="_".join(breadcrumbs),
                views=int(response.css("table.data-list")[1].css("tr td::text").getall()[2]),
                start_date=self.get_date(extracted_start),
                end_date=self.get_date(extracted_end),
            )
        except BaseException as exception:
            logging.critical(f"Failed to parse {response.request.url}.\n{exception.__doc__}")

    def get_date(self, extract):
        regex = re.search("^(?:[ETKNRLP]{1}) (\d{2}).(\d{2}).(\d{4}) (\d{2}):(\d{2}):(\d{2})$", extract)
        if regex is None:
            return None

        day = int(regex.group(1))
        month = int(regex.group(2))
        year = int(regex.group(3))
        hour = int(regex.group(4))
        minute = int(regex.group(5))
        second = int(regex.group(6))
        return datetime.datetime(year, month, day, hour, minute, second)
