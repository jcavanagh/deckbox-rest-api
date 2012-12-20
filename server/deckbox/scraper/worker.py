from scrapy import project, signals
from scrapy.conf import settings
from scrapy.crawler import CrawlerProcess
from scrapy.xlib.pydispatch import dispatcher
from multiprocessing import Queue, Process
import multiprocessing
 
class Worker(multiprocessing.Process):
 
    def __init__(self, spider, deckbox_user, deckbox_pass):
        multiprocessing.Process.__init__(self)
 
        self.crawler = CrawlerProcess(settings)
        if not hasattr(project, 'crawler'):
            self.crawler.install()
        self.crawler.configure()
 
        self.items = []
        self.spider = spider
        self.username = deckbox_user
        self.password = deckbox_pass
        dispatcher.connect(self._item_passed, signals.item_passed)
 
    def _item_passed(self, item):
        self.items.append(item)
  
    def _crawl(self):
        if self.spider:
            self.crawler.crawl(self.spider(self.username, self.password))
        self.crawler.start()
        self.crawler.stop()
    
    def crawl(self, spider):
        p = Process(target=self._crawl)
        p.start()
        p.join()
