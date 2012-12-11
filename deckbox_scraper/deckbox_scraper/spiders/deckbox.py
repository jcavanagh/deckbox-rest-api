from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

from deckbox_scraper.items import Card, Deck

class DeckboxSpider(BaseSpider):
    name = "deckbox"
    allowed_domains = ["deckbox.org"]

    # Special set names which are structured as decks, but are not
    special_set_names = ['Inventory', 'Tradelist', 'Wishlist']

    # URLs
    login_url = "http://deckbox.org"
    decks_url = "http://deckbox.org/"

    start_urls = [
        login_url
    ]

    # Global spider data
    decks = {}
    deck_links = []

    def parse(self, response):
        if self.is_authenticated(response):
            return self.crawl_all(response)
        else:
            return self.login(response)

    def check_login_response(self, response):
        if self.is_authenticated(response):
            self.log("Successfully logged in.")
        else:
            self.log("Login unsuccessful :(")
            return False

        return self.crawl_all(response)

    def login(self, response):
        # TODO: Get credentials from config
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
            callback = self.check_login_response
        )

    def is_authenticated(self, response):
        return "Logout" in response.body

    def crawl_all(self, response):
        self.log('Crawling all...')

        # Get list of decks
        self.deck_links = SgmlLinkExtractor(allow = r'/sets/\d+').extract_links(response)

        return self.parse_deck_links(None)

    def parse_deck_links(self, response):
        if response:
            # Pull deck ID
            deck_id = response.url.rpartition('/')[2]

            print deck_id

            # Process
            self.decks[deck_id] = self.parse_deck(response)

        # See if we have links left to parse
        if self.deck_links:
            link = self.deck_links.pop(0)
        else:
            link = None

        # Skip special sets that are not decks
        while link and link.text in self.special_set_names:
            link = self.deck_links.pop(0)

        print link

        if link:
            return Request(link.url, callback=self.parse_deck_links)
        else:
            # Return combined data
            print self.decks

    def parse_deck(self, response):
        print 'parsing deck!'
        # Parse and return a Deck
        return {}