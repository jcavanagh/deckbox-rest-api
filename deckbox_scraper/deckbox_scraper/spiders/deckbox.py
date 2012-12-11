from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

from deckbox_scraper.items import DeckboxScraperItem

class DeckboxSpider(BaseSpider):
    name = "deckbox"
    allowed_domains = ["deckbox.org"]
    login_page = "http://deckbox.org"
    start_urls = [
        "http://deckbox.org"
    ]

    def parse(self, response):
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
        self.log(response.body)
        if "Logout" in response.body:
            self.log("Successfully logged in. Let's start crawling!")
        else:
            self.log("Bad times :(")