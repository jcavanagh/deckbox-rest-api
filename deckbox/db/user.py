from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref

from deckbox.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True)
    password = Column(String(64))
    salt = Column(String(64))

    decks = relationship('Deck', backref='deck')

    def __init__(self, username, password, salt):
        self.username = username
        self.password = password
        self.salt = salt

    def __repr__():
        return "<User('%s','%s')>" % (self.id, self.name)