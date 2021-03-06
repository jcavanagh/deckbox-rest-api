from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship, backref

from deckbox.db import Base

class Deck(Base):
    __tablename__ = 'decks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    json = Column(Text)

    def __init__(self, user_id, json):
        self.user_id = user_id
        self.json = json

    def __repr__():
        return "<Deck('%s')>" % (self.id)