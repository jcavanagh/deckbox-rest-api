from bottle import route

from deckbox.db import user, deck

# Decks
@get('/decks/<id>')
def get_deck(id):
    return id

@post('/decks')
def create_deck():
    return None

# Users
@get('/users/<id>'):
def get_user(id):
    return id

@post('/users'):
def create_user():
    return None