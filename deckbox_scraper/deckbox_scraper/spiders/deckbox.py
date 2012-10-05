from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.spiders.init import InitSpider
from scrapy.selector import HtmlXPathSelector

from deckbox_scraper.items import DeckboxScraperItem

class DeckboxSpider(InitSpider):
    name = "deckbox"
    allowed_domains = ["deckbox.org"]
    login_page = "http://deckbox.org"
    start_urls = [
        "http://deckbox.org"
    ]

    def init_request(self):
        return Request(url=self.login_page, callback=self.login, method='GET')

    def login(self, response):
        # Find token
        hxs = HtmlXPathSelector(response)
        token = hxs.select('//input[@name="authenticity_token"]/@value').extract()[0]
        self.log('Token: ' + token)

        return FormRequest.from_response(response,
            formdata = {
                'authenticity_token': token,
                'login': 'jcavanagh617@gmail.com', 
                'password': ''
            },
            callback=self.check_login_response
        )

    def check_login_response(self, response):
        self.log('checking login...')
        if "Logout" in response.body:
            self.log("Successfully logged in. Let's start crawling!")
            self.initialized()
        else:
            self.log("Bad times :(")

    def parse(self, response):
        self.log('parse!')