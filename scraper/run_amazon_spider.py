from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.amazon import AmazonSpider

process = CrawlerProcess(get_project_settings())
data = []
process.crawl(AmazonSpider, keyword = 'tmg', data = data)
process.start()

# print(data)
print(data[0]['package'])
print(data[0]['rating'])