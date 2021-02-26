import os
from distutils.dir_util import remove_tree

from flask import Flask, request, jsonify, url_for, send_from_directory
from flask_cors import CORS
import mysql.connector

from selenium import webdriver

from common import FillPortal
from make_log import custom_log_data
from settings import screenshot_folder, conn_data, WEBDRIVER_FOLDER_PATH, chrome_options, root_folder

app = Flask(__name__)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['referrer_url'] = None

@app.route("/")
def index():
    return url_for('index', _external=True)

@app.route('/getportalfieldvalues', methods=["POST"])
def getportalfieldvalues():
    fields, records, temp = ['refno', 'pname', 'insid'], [], {}
    data = request.form.to_dict()
    q = "select refno, pname, insid from portal_field_values where refno=%s limit 1"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (data['refno'],))
        r = cur.fetchone()
        if r is not None:
            for k, v in zip(fields, r):
                temp[k] = v
    return temp

@app.route('/setportalfieldvalues', methods=["POST"])
def setportalfieldvalues():
    data = request.form.to_dict()
    q = "select * from portal_field_values where refno=%s limit 1"
    q1 = "update portal_field_values set pname=%s, insid=%s where refno=%s and pname!='' and insid!=''"
    q2 = "insert into portal_field_values (refno, pname, insid) values (%s, %s, %s)"
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        cur.execute(q, (data['refno'],))
        r = cur.fetchone()
        if r is not None:
            cur.execute(q1, (data['pname'], data['insid'], data['refno']))
        else:
            cur.execute(q2, (data['refno'], data['pname'], data['insid']))
        con.commit()
    return jsonify("done")

@app.route('/run', methods=["GET"])
def run():
    data = request.args.to_dict()
    if 'mss_no' not in data and 'hosp_id' not in data:
        return jsonify("pass mss_no and hosp_id")
    else:
        driver = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
        portal = FillPortal(data['mss_no'], data['hosp_id'])
        z = portal.visit_portal(driver=driver)
        if z is None or z == 'data:,':
            custom_log_data(filename='failed_portal', mssno=portal.mss_no, porta_link=portal.data['0']['PortalLink'])
        else:
            portal.login()
            portal.home()
            portal.execute()
    driver.quit()
    if os.path.exists(root_folder):
        remove_tree(root_folder)
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
    app.run(host="0.0.0.0", port=9985)
