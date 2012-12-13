from bottle import route

@route('/deck/<id>')
def deck(id):
    return id