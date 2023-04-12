import scrapy
from scraper.items import Product


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

    def __init__ (self, keyword = '', data = None, *args, **kwargs):
        super(AmazonSpider, self).__init__(*args, **kwargs)
        self.keyword = keyword
        if data is None:
            data = []
        self.data = data

    def start_requests(self):
        keyword = 'vitamin c'
        if len(self.keyword) > 0:
            keyword = self.keyword
        url = f'https://www.amazon.com/s?k={keyword}&s=exact-aware-popularity-rank&page=1'
        yield scrapy.Request(url, meta={'playwright': True})

    def parse (self, response, **kwargs):
        for product in response.css('div[data-asin]'):
            quote_item = Product()
            asin = product.css('div::attr(data-asin)').extract()
            
            # ignore wrapper div that contains multiple asins
            # ignore div with empty asin
            if len(asin) > 1 or not len(asin[0]):
                continue

            # get prices
            prices = product.css('span[class="a-offscreen"]')
            price_current = price_before = 0
            
            for idx, p in enumerate(prices):
                text = p.css('span::text').get()
                if idx == 0:
                    price_current = text
                else:
                    price_before = text
            
            # title of the product
            title = product.css('span[class="a-size-base-plus a-color-base a-text-normal"]::text').get()
            
            # package composition such as 150 count
            package = product.css('span[class="a-size-base a-color-information a-text-bold"]::text').get()

            rating = '0'
            for span in product.css('span[aria-label]'):
                ratings = span.css('span::attr(aria-label)').extract()
                # there should be one label
                if len(ratings) < 0:
                    continue
                if "of 5 stars" in ratings[0]:
                    rating = ratings[0]
                    
            review_cnt = 0
            for a in product.css('a[href]'):
                hrefs = a.css('a::attr(href)').extract()
                if len(hrefs) < 0:
                    continue
                if "#customerReviews" not in hrefs[0]:
                    continue
                review_cnt = a.css('a span::text').get()
                    
            thumbnail_url = ''
            for img_tag in product.css('img[srcset]'):
                thumbnail_url = img_tag.css('img::attr(src)').get()
            
            quote_item['id'] = asin
            quote_item['title'] = title
            quote_item['thumbnail_url'] = thumbnail_url
            quote_item['package'] = package
            quote_item['rating'] = rating
            quote_item['review_cnt'] = review_cnt
            quote_item['price_current'] = price_current
            quote_item['price_before'] = price_before
            self.data.append(quote_item)
            yield quote_item

