from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scraper.spiders.amazon import AmazonSpider
from multiprocessing import Process, Queue


class Amazon:
    
    @staticmethod
    def scrape(keyword) -> list:
        if len(keyword) < 1:
            keyword = 'vitamin c'
            
        q = Queue()
        q.put(keyword)
        p = Process(target = crawl, args = (q,))
        p.start()
        p.join()
        res = q.get()
        q.close()
        q.join_thread()
        return res


def crawl(queue) -> list:
    keyword = queue.get()
    process = CrawlerProcess(get_project_settings())
    data = []
    process.crawl(AmazonSpider, keyword = keyword, data = data)
    process.start()
    queue.put(data)
    return data
