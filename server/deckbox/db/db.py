# Handles DB persistence to PostgreSQL
from deckbox.util import config

from deckbox.db import Base
from user import User
from deck import Deck

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound


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

def get_user(session, username):
    user = None

    try:
        user = session.query(User)\
                .filter(User.username == username)\
                .one()
    except NoResultFound:
        # Oh noes
        pass

    return user

def get_user_by_session(session, session_id):
    user = None

    try:
        user = session.query(User)\
                .filter(User.session_id == session_id)\
                .one()
    except NoResultFound:
        # Oh noes
        pass

    return user

def get_deck(session, user, deck_id):
    deck = None

    try:
        deck = session.query(User, Deck)\
                .filter(User.session_id == session_id)\
                .filter(User.id == Deck.user_id)\
                .filter(Deck.id == id)\
                .one()
    except NoResultFound:
        # Oh noes
        pass

    return deck