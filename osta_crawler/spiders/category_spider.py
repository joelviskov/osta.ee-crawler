from osta_crawler.items import CategoryItem
import scrapy
import logging
from scrapy.utils.log import configure_logging


class CategorySpider(scrapy.Spider):
    name = 'category_spider'
    allowed_domains = ['osta.ee']
    start_urls = [
        'https://www.osta.ee'
    ]

    configure_logging(install_root_handler=False)
    logging.basicConfig(
        filename='log.txt',
        format='%(levelname)s: %(message)s',
        level=logging.INFO,
        filemode='w'
    )

    custom_settings = {
        "FEEDS": {
            'categories.json': {
                'format': 'jsonlines',
                'encoding': 'utf8',
                'store_empty': False,
                'fields': None,
                'indent': 4,
                'item_export_kwargs': {
                    'export_empty_fields': True,
                },
            }
        }
    }

    current_index = 0

    def get_next_id(self):
        self.current_index = self.current_index + 1
        return self.current_index

    def parse(self, response):
        main_category_anchors = response.css('li.nav-item.hero a')
        yield from response.follow_all(main_category_anchors, callback=self.parse_first_level)

    def parse_first_level(self, response):
        sidebar = response.css('div.main-sidebar__section.cat-list__section')
        list_items = sidebar.css('ul.cat-list__sub-list li.nav-item')

        # First level of category.
        index_here = self.get_next_id()
        yield CategoryItem(
            id=index_here,
            name=sidebar.css('h3.cat-list__title::text').get().strip(),
            parent_id=None
        )

        yield from response.follow_all(list_items.css('a'), callback=self.parse_level, meta={"parent": index_here})

    def parse_level(self, response):
        sidebar = response.css('div.main-sidebar__section.cat-list__section')
        list_items = sidebar.css('ul.cat-list__sub-list-sub li.nav-item')
        index_here = self.get_next_id()

        if not list_items:
            # Must be max two-leveled.
            active_item = sidebar.css('ul.cat-list__sub-list li.nav-item.active')
            yield CategoryItem(
              id = index_here,
              name=active_item.css('a::text').get().strip(),
              parent_id = response.request.meta['parent'],
            )
        else:
            active_item = list_items.css('li.nav-item.active')
            if not active_item:
                # Middle level of category discovered.
                yield CategoryItem(
                  id = index_here,
                  name=sidebar.css('ul.cat-list__sub-list li.nav-item a::text')[0].get().strip(),
                  parent_id = response.request.meta['parent'],
                )
                yield from response.follow_all(list_items.css('a'), callback=self.parse_level, meta={"parent": index_here})
            else:
                # Last level of categories discovered.
                yield CategoryItem(
                  id = index_here,
                  name=active_item.css('a::text').get().strip(),
                  parent_id = response.request.meta['parent'],
                )