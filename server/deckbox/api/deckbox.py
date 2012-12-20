from bottle import get, post, put, delete, request, response, abort

from ..db.user import User
from ..db.deck import Deck
from ..db import db

from ..scraper import worker, deckbox

import os, binascii, hashlib, json

# Auth
@post('/login')
def login():
    username = request.forms.username
    password = request.forms.password

    return actual_login(username, password)

def actual_login(username, password):
    if(not validate_present(username, password)):
        abort(400, "username and password must be specified")

    session = db.create_session()

    # Get user
    user = db.get_user(session, username)

    if(user is None):
        abort(401, "Bad username or password")

    # Pull user data
    salt = user.salt
    hashed_pass = user.password

    # Hash the submitted password
    new_hash_pass = hash_pass(password, salt)

    # Check it
    if(hashed_pass == new_hash_pass):
        # Create a session id and store
        session_id = get_session_id()
        user.session_id = session_id
        session.commit()

        response.set_cookie('session_id', session_id)
    else:
        abort(401, "Bad username or password")

    return "Login successful"

# Scrape
@get('/scrape/<username>')
def scrape(username):
    if(not validate_present(username)):
        abort(400, "username must be specified")

    session = db.create_session()

    # Get user
    user = db.get_user(session, username)

    if(user is None):
        abort(401, "Bad username or password")

    # Start a scrape for the given user
    crawler = worker.Worker(deckbox.DeckboxSpider, user.deckbox_username, user.deckbox_password)
    crawler.crawl('deckbox')

# Decks
@get('/decks')
def get_all_decks():
    session_id = request.get_cookie('session_id')

    if(not validate_present(session_id)):
        abort(401, "Bad session")

    session = db.create_session()

    decks = db.get_decks(session, user)

    return json.dumps(decks)

@get('/decks/<id>')
def get_deck(id):
    session_id = request.get_cookie('session_id')

    if(not validate_present(session_id)):
        abort(401, "Bad session")

    session = db.create_session()

    deck = db.get_deck()

    return json.dumps(deck)

@post('/decks')
def create_deck():
    # Validate
    json = request.forms.json
    session_id = request.get_cookie('session_id')

    if(not validate_present(session_id)):
        abort(401, "No session")

    if(not validate_present(json)):
        abort(400, "json must be specified")

    if(not validate_present(session_id)):
        abort(401, "Bad session")

    session = db.create_session()

    # Get user ID
    user = db.get_user_by_session(session, session_id)

    if(user is None):
        abort(401, "No user found for session")

    # Create deck
    deck = Deck(user.id, json)
    session.add(deck)
    session.commit()

    return "Deck creation successful"

# Users
@post('/users')
def create_user():
    # User attributes
    username = request.forms.username
    password = request.forms.password 
    deckbox_username = request.forms.deckbox_username
    deckbox_password = request.forms.deckbox_password

    # Validate
    if(not validate_present(username, password, deckbox_username, deckbox_password)):
        abort(400, "All fields must be specified.")

    session = db.create_session()

    if(db.get_user(session, username) is not None):
        # Login instead
        actual_login(username, password)

        return "Logged in successfully"

    # Generate salt and hash password
    salt = binascii.b2a_hex(os.urandom(32))
    hashed_pass = hash_pass(password, salt)

    # Create user
    user = User(username, hashed_pass, salt, deckbox_username, deckbox_password)
    
    # Commit the new user
    session.add(user)
    session.commit()

    # Autologin and set session ID
    actual_login(username, password)

    return "User " + username + " created successfully"

# Utils
def hash_pass(password, salt):
    return hashlib.sha256(salt + password).hexdigest()

def get_session_id():
    return binascii.b2a_hex(os.urandom(32))

def validate_present(*args):
    valid = True

    for arg in args:
        valid = valid & (arg != None and arg != '')

    return valid
