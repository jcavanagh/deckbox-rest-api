from scrapy.http import Request, FormRequest
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.selector import HtmlXPathSelector
from scrapy.spider import BaseSpider

class DeckboxSpider(BaseSpider):
    name = "deckbox"
    allowed_domains = ["deckbox.org"]

    start_urls = [
        "http://deckbox.org"
    ]

    # Special set names which are structured as decks, but are not decks
    special_set_names = ['Inventory', 'Tradelist', 'Wishlist']

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
            return self.crawl_all(response)
        else:
            self.log("Login unsuccessful :(")
            return None

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

        if link:
            return Request(link.url, callback=self.parse_deck_links)
        else:
            # TODO: Persist combined data
            return None

    def parse_deck(self, response):
        hxs = HtmlXPathSelector(response)

        # Parse and return a Deck
        deck = {}
        deck['title'] = hxs.select('//span[@class="section_title"]/text()').extract()
        deck['main_deck'] = []
        deck['sideboard'] = []

        # Parse main deck
        raw_main_deck = hxs.select('//div[@id="set_cards_table"]//tr[@id]')

        for raw_card in raw_main_deck:
            card = self.parse_card(raw_card)

            # Add card to deck
            deck['main_deck'].append(card)

        # Parse sideboard
        raw_sideboard = hxs.select('//div[@id="sideboard"]//tr[@id]')

        for raw_card in raw_sideboard:
            card = self.parse_card(raw_card)

            # Add card to deck
            deck['sideboard'].append(card)

        return deck

    def parse_card(self, raw_card):
        # Parse card
        card = {}
        card['id'] = raw_card.select('@id').extract()[0]
        card['name'] = raw_card.select('td[@class="card_name"]//a/text()').extract()[0]
        card['cardType'] = raw_card.select('td[not(@*)]/span/text()').extract()[0]
        card['rarity'] = raw_card.select('td[@class="mtg_rarity"]/img/@alt').extract()[0]
        card['price'] = raw_card.select('td[contains(@class, "price")]/a/text()').extract()[0]

        return card