#!/usr/bin/python
from bottle import run
from deckbox.util import config

# Import API
from deckbox.api import deckbox

# DB
from deckbox.db import db
db.init_db()

# Start Bottle
run(host=config.server('host'), port=config.server('port'))