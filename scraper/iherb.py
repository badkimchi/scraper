from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.iherb import IherbSpider
from multiprocessing import Process, Queue


class Iherb:
    
    @staticmethod
    def scrape(keyword = 'tmg', country = 'us'):
        q = Queue()
        search = {"keyword": keyword, "country": country}
        q.put(search)
        p = Process(target = crawl, args = (q,))
        p.start()
        p.join()
        res = q.get()
        q.close()
        q.join_thread()
        return res


def crawl(queue) -> list:
    search = queue.get()
    process = CrawlerProcess(get_project_settings())
    data = []
    process.crawl(IherbSpider, search = search, data = data)
    process.start()
    queue.put(data)
    return data
