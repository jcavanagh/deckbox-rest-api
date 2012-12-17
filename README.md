# deckbox-rest-api #

A simple REST API for deckbox.org.  Authenticates and scrapes deck data, then makes the data available via REST.

Includes a companion mobile application that makes use of the scraping backend.

## Setup / Prerequisites ##

### Python ###
* Python 2.7.3 / pip
    * sudo apt-get install python python-pip
* Bottle 0.10.11
    * sudo pip install bottle
* Scrapy 0.16
    * sudo pip install scrapy
* SQLAlchemy 0.7.9
    * sudo pip install sqlalchemy

### PostgreSQL ###
* sudo apt-get install postgresql

### Configuration and Installation ###
* Install prerequisites, as listed above
* Create an empty PostgreSQL database and standard user
* Rename deckbox-rest.cfg.dist to deckbox-rest.cfg.  Fill out all relevant database information with the db/user you just created.  Change the local REST API server port if desired.

## Usage ##

Execute deckbox-rest.py to start the server