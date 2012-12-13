# Handles DB persistence to PostgreSQL
from sqlalchemy import create_engine
from deckbox.util import config

engine = create_engine('sqlite:///:memory:', echo=True)
engine.execute('select 1').scalar()