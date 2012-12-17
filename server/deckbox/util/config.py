# Manages app configuration
import ConfigParser
import os

# Config
CONFIG_FILE = os.path.join(os.path.dirname(__file__), '..', '..', 'deckbox-rest.cfg')

# Load config
config = ConfigParser.ConfigParser()
config.readfp(open(CONFIG_FILE))

def db(key):
    return config.get('database', key)

def server(key):
    return config.get('server', key)