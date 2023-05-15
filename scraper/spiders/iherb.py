import scrapy
import re


# use the initial document only and prevent further download of anything else.
from scrapy_playwright.page import PageMethod


def should_abort_request(request):
    if request.resource_type in ['image', 'script', 'font', 'xhr', 'stylesheet', 'fetch', 'ping']:
        return True
    return False


class IherbSpider(scrapy.Spider):
    name = 'iherb'
    custom_settings = {
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request
    }
    
    # def __init__(self, search, data = None, *args, **kwargs):
    #     super(IherbSpider, self).__init__(*args, **kwargs)
    #
    #     self.keyword = 'vitamin c'
    #     if 'keyword' in search and len(search['keyword']) > 0:
    #         self.keyword = search['keyword']
    #
    #     self.country = 'us'
    #     if 'country' in search and len(search['country']) > 0:
    #         self.country = search['country']
    #
    #     if data is None:
    #         data = []
    #     self.data = data
    
    # for debugging
    # /opt/homebrew/lib/python3.11/site-packages/scrapy/cmdline.py
    # crawl amazon
    # https://htmledit.squarefree.com/
    def __init__(self, data = None, *args, **kwargs):
        super(IherbSpider, self).__init__(*args, **kwargs)
        self.keyword = 'vitamin c'
        self.country = 'jp'

        if data is None:
            data = []
        self.data = data
    
    def start_requests(self):
        url = f'{self.get_domain()}/search?kw={self.keyword}&p=1'
        yield scrapy.Request(url)
    
    def get_domain(self):
        domain = 'https://www.iherb.com'
        if self.country == 'jp':
            domain = 'https://jp.iherb.com'
        return domain
    
    def parse(self, response, **kwargs):
        for product in response.css('div[itemtype="http://schema.org/Product"]'):
            # warning: this value is only used as a scrape result for scrapy
            # it is not actually passed to the scrape results to the caller
            quote_item = Product()
            
            product_id = product.css('a::attr(data-ga-product-id)').extract()
            
            # ignore wrapper div that contains multiple asins
            # ignore div with empty asin
            if len(product_id) > 1 or not len(product_id[0]):
                continue
            
            # get prices
            prices = product.css('div[class="product-price-top"]')
            price_current = price_before = ''
            
            for idx, p in enumerate(prices.css('bdi')):
                text = p.css('bdi::text').get()
                ext = prices.extract()
                if idx == 0:
                    price_current = re.sub('[^0-9.]+', '', text)
                    continue
                if idx == 1 and len(text) > 0:
                    price_before = re.sub('[^0-9.]+', '', text)
            
            try:
                price_current = float(price_current)
                price_before = float(price_before)
            except Exception:
                price_before = 0
            
            # title of the product
            title = product.css('a::attr(aria-label)').get()
            
            # package composition such as 150 count
            package = ''
            
            # what is the rating out of 5?
            rating = '0'
            for meta in product.css('meta[itemprop="ratingValue"]'):
                rating = meta.css('meta::attr(content)').get()
            
            try:
                rating = float(rating)
            except Exception:
                pass
            
            # how many reviews
            review_cnt = ''
            for meta in product.css('meta[itemprop="reviewCount"]'):
                review_cnt = meta.css('meta::attr(content)').get()

            try:
                review_cnt = int(review_cnt.replace(',', ''))
            except Exception:
                pass
            
            thumbnail_url = ''
            for span in product.css('span[class="product-image"]'):
                # html for thumbnail seems to vary
                thumbnail_url = span.css('img::attr(src)').get()
                if not thumbnail_url:
                    thumbnail_url = span.css('div::attr(data-image-retina-src)').get()
            
            self.data.append({
                'store': 'iherb',
                'id': product_id[0],
                'url': self.get_domain() + '/pr/' + product_id[0],
                'title': title,
                'thumbnailUrl': thumbnail_url,
                'package': package,
                'rating': rating,
                'reviewCnt': review_cnt,
                'priceCurrent': price_current,
                'priceBefore': price_before,
                'currency': '$' if self.country == 'us' else '¥',
            })
            yield quote_item


class Product(scrapy.Item):
    # define the fields for your item here like:
    id = scrapy.Field()
    # title = scrapy.Field()
    # thumbnail_url = scrapy.Field()
    # package = scrapy.Field()
    # rating = scrapy.Field()
    # review_cnt = scrapy.Field()
    # price_current = scrapy.Field()
    # price_before = scrapy.Field()
