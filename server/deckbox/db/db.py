# Handles DB persistence to PostgreSQL
from deckbox.util import config
from deckbox.db import Base, user, deck

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Session = None

def init_db():
    # Create DB engine
    engine = create_engine(
        'postgresql://' + config.db('user') + ':' + config.db('pass') +
        '@' + config.db('host') + ':' + config.db('port') + '/' + config.db('name')
    )

    # Init database
    Base.metadata.create_all(engine)

    global Session
    Session = sessionmaker(bind=engine)

def create_session():
    return Session()