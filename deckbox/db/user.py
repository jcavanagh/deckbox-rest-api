from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship, backref

from deckbox.db import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(128), unique=True)
    password = Column(String(32))   #SHA-256
    salt = Column(String(32))

    #FIXME: Implement actual session management with timeouts and other nice things
    session_id = Column(String(64))

    #FIXME: I hate to store this in plaintext, but I have little choice with screen scraping
    deckbox_username = Column(String(128))
    deckbox_password = Column(String(128))

    decks = relationship('Deck', backref='deck')

    def __init__(self, username, password, salt, deckbox_username, deckbox_password):
        self.username = username
        self.password = password
        self.salt = salt
        self.deckbox_username = deckbox_username
        self.deckbox_password = deckbox_password

    def __repr__():
        return "<User('%s','%s')>" % (self.id, self.name)