import scrapy
import re


# use the initial document only and prevent further download of anything else.
def should_abort_request(request):
    if request.resource_type in ['image', 'script', 'font', 'xhr', 'stylesheet', 'fetch', 'ping']:
        return True
    return False


class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    custom_settings = {
        'PLAYWRIGHT_ABORT_REQUEST': should_abort_request
    }
    
    def __init__(self, search, data = None, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)

        self.keyword = 'vitamin c'
        if 'keyword' in search and len(search['keyword']) > 0:
            self.keyword = search['keyword']

        self.country = 'us'
        if 'country' in search and len(search['country']) > 0:
            self.country = search['country']

        if data is None:
            data = []
        self.data = data
    
    # # for debugging
    # # /opt/homebrew/lib/python3.11/site-packages/scrapy/cmdline.py
    # # crawl amazon
    # # https://htmledit.squarefree.com/
    # def __init__(self, data = None, *args, **kwargs):
    #     super(AmazonSpider, self).__init__(*args, **kwargs)
    #     self.keyword = 'vitamin c'
    #     self.country = 'jp'
    #
    #     if data is None:
    #         data = []
    #     self.data = data
    
    def start_requests(self):
        url = f'{self.get_domain()}/s?k={self.keyword}&s=exact-aware-popularity-rank&page=1'
        yield scrapy.Request(url, meta = {'playwright': True})
    
    def get_domain(self):
        domain = 'https://www.amazon.com'
        if self.country == 'jp':
            domain = 'https://www.amazon.co.jp'
        return domain
    
    def parse(self, response, **kwargs):
        for product in response.css('div[data-asin]'):
            
            # warning: this value is only used as a scrape result for scrapy
            # it is not actually passed to the scrape results to the caller
            quote_item = Product()
            
            asin = product.css('div::attr(data-asin)').extract()
            
            # ignore wrapper div that contains multiple asins
            # ignore div with empty asin
            if len(asin) > 1 or not len(asin[0]):
                continue
            
            # get prices
            prices = product.css('span[class="a-offscreen"]')
            price_current = price_before = ''
            
            for idx, p in enumerate(prices):
                text = p.css('span::text').get()
                if idx == 0:
                    price_current = re.sub('[^0-9.]+', '', text)
                    continue
                if len(text) > 0:
                    price_before = re.sub('[^0-9.]+', '', text)
            
            try:
                price_current = float(price_current)
                price_before = float(price_before)
            except Exception:
                price_before = 0
            
            # title of the product
            title = product.css('span[class="a-size-base-plus a-color-base a-text-normal"]::text').get()
            
            # package composition such as 150 count
            package = product.css('span[class="a-size-base a-color-information a-text-bold"]::text').get()
            
            rating = '0'
            for span in product.css('span'):
                text = span.css('span::text').get()
                # us
                if text and "out of" in text and "stars" in text:
                    rating = text[0:text.index('out of') - 1]
                # jp
                if text and "つ星のうち" in text:
                    rating = text[len('5つ星のうち'):]
            
            try:
                rating = float(rating)
            except Exception:
                pass
            
            review_cnt = ''
            for a in product.css('a[href]'):
                hrefs = a.css('a::attr(href)').extract()
                if len(hrefs) < 0:
                    continue
                if "#customerReviews" not in hrefs[0]:
                    continue
                review_cnt = a.css('a span::text').get()
            try:
                review_cnt = int(review_cnt.replace(',', ''))
            except Exception:
                pass
            
            thumbnail_url = ''
            for img_tag in product.css('img[srcset]'):
                thumbnail_url = img_tag.css('img::attr(src)').get()
            
            self.data.append({
                'id': asin[0],
                'url': self.get_domain() + '/dp/' + asin[0],
                'title': title,
                'thumbnailUrl': thumbnail_url,
                'package': package,
                'rating': rating,
                'reviewCnt': review_cnt,
                'priceCurrent': price_current,
                'priceBefore': price_before,
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
