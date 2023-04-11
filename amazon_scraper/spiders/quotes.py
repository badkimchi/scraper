import scrapy
from amazon_scraper.items import Product

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

    def start_requests(self):
        url = "https://www.amazon.com/s?k=vitamin+c&s=exact-aware-popularity-rank&page=1"
        yield scrapy.Request(url, meta={'playwright': True})

    def parse(self, response):
        for quote in response.css('div[data-asin]'):
            quote_item = Product()
            asin = quote.css('div::attr(data-asin)').extract()
            
            # ignore wrapper div that contains multiple asins
            # ignore div with empty asin
            if len(asin) > 1 or not len(asin[0]):
                continue

            prices = quote.css('span[class="a-offscreen"]')
            price_current = 0
            price_before = 0
            for idx, p in enumerate(prices):
                text = p.css('span::text').get()
                if idx == 0:
                    price_current = text
                else:
                    price_before = text
                
            quote_item['id'] = asin
            quote_item['price_current'] = price_current
            quote_item['price_before'] = price_before
            yield quote_item
