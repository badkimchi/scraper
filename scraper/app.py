from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.amazon import AmazonSpider

import asyncio
import nest_asyncio

nest_asyncio.apply()

from fastapi import FastAPI
from multiprocessing import Process, Queue


from scraper.amazon import Amazon

app = FastAPI()

results = {}


@app.get("/", tags = ['ROOT'])
async def root () -> list:
    q = Queue()
    p = Process(target = scrape_amazon, args = (q,))
    p.start()
    p.join()
    res = q.get()
    q.close()
    q.join_thread()
    return res


def scrape_amazon (queue) -> list:
    keyword = 'tmg'
    if len(keyword) < 1:
        keyword = 'vitamin c'
    
    process = CrawlerProcess(get_project_settings())
    data = []
    process.crawl(AmazonSpider, keyword = keyword, data = data)
    process.start()
    queue.put(data)
    return data
