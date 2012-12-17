from bottle import get, post, put, delete, request, response, abort
from ..db import user, deck
from ..db.db import create_session

import os, hashlib, json

# Auth
@post('/login')
def login():
    session = create_session()

    username = request.query.username
    password = request.query.password

    if(username is None or password is None):
        abort(400, "username and password must be specified")

    # Get user
    user = session.query(Users)\
            .filter(User.username == username)\
            .one()

    # If we find no user, then we have a bad username
    if(user is None):
        abort(400, "Bad username or password")

    # Pull user data
    salt = user.salt
    password = user.password

    # Hash the submitted password
    new_hash_pass = hash_pass(password, salt)

    # Check it
    if(hash_pass == new_hash_pass):
        # Create a session id and store
        session_id = get_session_id()
        user.session_id = session_id
        session.commit()

    if(session_id is None):
        abort(401, "Bad username or password")

    response.set_cookie('session_id', session_id)

    return "Login successful"

# Decks
@get('/decks')
def get_all_decks():
    session = create_session()
    auth_token = request.get_cookie('auth_token')

    if(auth_token is None):
        abort(401, "Bad session")

    decks = session.query(User, Deck)\
            .filter(User.session_id == auth_token)\
            .filter(User.id == Deck.user_id)\
            .all()

    return json.dumps(decks)

@get('/decks/<id>')
def get_deck(id):
    session = create_session()
    auth_token = request.get_cookie('auth_token')

    if(auth_token is None):
        abort(401, "Bad session")

    deck = session.query(User, Deck)\
            .filter(User.session_id == auth_token)\
            .filter(User.id == Deck.user_id)\
            .filter(Deck.id == id)\
            .one()

    return json.dumps(deck)

@post('/decks')
def create_deck():
    session = create_session()
    auth_token = request.get_cookie('auth_token')

    if(auth_token is None):
        abort(401, "Bad session")

    json = request.query.json

    # Get user ID
    user_id = session.query(Users.id)\
            .filter(User.username == username)\
            .one()

    if(json is None):
        abort(400, "json must be specified")

    # Create deck
    deck = Deck(user_id, json)
    session.add(deck)
    session.commit()

    return "Deck creation successful"

# Users
@post('/users')
def create_user():
    session = create_session()

    # User attributes
    username = request.query.username
    password = request.query.password 
    deckbox_username = request.query.deckbox_username
    deckbox_password = request.query.deckbox_password

    # Validate
    if(username is None or password is None or deckbox_username is None or deckbox_password is None):
        abort(400, "All fields must be specified.")

    # Generate salt and hash password
    salt = os.urandom(32)
    hash_pass = hash_pass(password, salt)

    # Create user
    user = User(username, hash_pass, salt, deckbox_username, deckbox_password)

    # Autologin and return session ID
    session_id = actual_login(username, password)
    user.session_id = get_session_id()
    
    # Commit the new user
    session.add(user)
    session.commit()

    response.set_cookie('session_id', session_id)

    return "User " + username + " created successfully"

# Utils
def hash_pass(password, salt):
    return hashlib.sha256(salt + hashlib.sha256(password))

def get_session_id():
    return os.urandom(64)
