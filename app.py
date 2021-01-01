from flask import Flask, url_for

from flask_cors import CORS

from common import get_data_from_mssno_api, start_browser
from trigger import behave_main

start_browser()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['referrer_url'] = None


@app.route('/')
def index():
    mss_no = 'MSS-1003069'  # appolo
    get_data_from_mssno_api(mss_no)
    behave_main(['-t @check_portal'])
    behave_main(['-t @login'])
    return url_for('index', _external=True)


if __name__ == '__main__':
    app.run(host="0.0.0.0")
