#!/usr/bin/python
from bottle import run, debug

import deckbox
from deckbox.util import config
from deckbox.api import deckbox
from deckbox.db import db

db.init_db()

# Start Bottle
debug(True)
run(host=config.server('host'), port=config.server('port'))