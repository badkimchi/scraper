from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.amazon import AmazonSpider


class Amazon:
    
    @staticmethod
    async def scrape (keyword):
        if len(keyword) < 1:
            keyword = 'vitamin c'
        
        process = CrawlerProcess(get_project_settings())
        data = []
        process.crawl(AmazonSpider, keyword = keyword, data = data)
        await process.start()
        print(data)
        return data
