from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_cors import CORS
import mysql.connector

from common import FillPortal
from make_log import custom_log_data
from settings import screenshot_folder, conn_data

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['referrer_url'] = None

@app.route("/")
def index():
    return url_for('index', _external=True)

@app.route('/run', methods=["GET"])
def run():
    data = request.args.to_dict()
    if 'mss_no' not in data and 'hosp_id' not in data:
        return jsonify("pass mss_no and hosp_id")
    else:
        portal = FillPortal(data['mss_no'], data['hosp_id'])
        z = portal.visit_portal()
        if z is None or z == 'data:,':
            custom_log_data(filename='failed_portal', mssno=portal.mss_no, porta_link=portal.data['0']['PortalLink'])
        else:
            portal.login()
            portal.home()
            portal.execute()
    return data

@app.route('/get_log', methods=["POST"])
def get_log():
    field_list = ('id','time','transactionid','referenceno','tab_id',
                  'insurer','process','step','status','message','url')
    records = []
    params = []
    data = request.form.to_dict()
    for i in ('transactionid','referenceno', 'process'):
        if i not in data:
            return jsonify(f"pass {i} parameter")
    if 'fromdate' in data and 'todate' in data:
        for i in ('transactionid','referenceno', 'process', 'fromdate', 'todate'):
            params.append(data[i])
        q = "select * from logs where transactionid=%s and referenceno=%s and process=%s and time BETWEEN %s AND %s;"
    else:
        for i in ('transactionid','referenceno', 'process'):
            params.append(data[i])
        q = "select * from logs where transactionid=%s and referenceno=%s and process=%s;"

    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, params)
        r = cur.fetchall()
        for i in r:
            datadict = dict()
            for j, k in zip(field_list, i):
                datadict[j] = k
            records.append(datadict)
    return jsonify(records)

@app.route('/screenshot/<filename>')
def screenshot(filename):
    return send_from_directory(screenshot_folder, filename, mimetype='image/gif')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9982)
