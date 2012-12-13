# deckbox-rest-api #

A simple REST API for deckbox.org.  Authenticates and scrapes deck data, then makes the data available via REST.

* PostgreSQL

## Usage ##

Execute deckbox-rest.py to start the server

## Setup ##

### Python ###
* Python 2.7.3 / pip
    * sudo apt-get install python python-pip
* Bottle 0.10.11
    * sudo pip install bottle
* Scrapy 0.16
    * sudo pip install Scrapy
* SQLAlchemy 0.7.9
    * sudo pip install sqlalchemy

### PostgreSQL ###
* sudo apt-get install postgresql