#!/usr/bin/python
from bottle import run
from deckbox.util import config

# Import API
from deckbox.api import deckbox

# Start Bottle
run(host=config.bottle('BOTTLE_HOST'), port=config.bottle('BOTTLE_PORT'))