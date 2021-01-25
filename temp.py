from flask import url_for
filename = 'asd.txt'
a = url_for('screenshot', filename=filename, _external=True)
pass