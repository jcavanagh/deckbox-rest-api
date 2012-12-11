# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class Card(Item):
    # Defines a card
    name = Field()
    cardType = Field()
    cost = Field()
    price = Field()

class Deck(Item):
    title = Field()
    legality = Field()
    main_deck = []   # Array of cards
    sideboard = []   # Array of cards
