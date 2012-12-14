#!/usr/bin/python
from bottle import run

import deckbox
from deckbox.util import config
from deckbox.api import deckbox
from deckbox.db import db

db.init_db()

# Start Bottle
run(host=config.server('host'), port=config.server('port'))