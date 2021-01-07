import subprocess
from time import sleep

from flask import Flask, url_for, jsonify

from flask_cors import CORS

from common import get_data_from_mssno_api, start_browser, kill_browser, is_browser_running

start_browser()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['referrer_url'] = None


@app.route('/')
def index():
    mss_no = 'MSS-1003069'  # appolo
    get_data_from_mssno_api(mss_no)
    subprocess.run(["behave", "-i", "check_portal", "--junit"])
    subprocess.run(["behave", "-i", "login", "--junit"])
    return url_for('index', _external=True)

@app.route('/restart_browser')
def restart_browser():
    if is_browser_running():
        status = 'unable to kill browser'
        if kill_browser():
            status = 'unable to start browser'
            sleep(1)
            start_browser()
            status = 'browser started'
        return status
    else:
        start_browser()
        status = 'browser started'
        return status
if __name__ == '__main__':
    app.run(host="0.0.0.0")
