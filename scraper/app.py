from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.amazon import AmazonSpider

import asyncio
import nest_asyncio
nest_asyncio.apply()

from fastapi import FastAPI

from scraper.amazon import Amazon

app = FastAPI()


@app.get("/", tags = ['ROOT'])
async def root () -> list:
    keyword = 'tmg'
    if len(keyword) < 1:
        keyword = 'vitamin c'
    
    process = CrawlerProcess(get_project_settings())
    data = []
    process.crawl(AmazonSpider, keyword = keyword, data = data)
    process.start()
    print(data)
    
    
    # result = await Amazon.scrape('zinc')
    return data
