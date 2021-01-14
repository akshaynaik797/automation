import requests
import mysql.connector

from settings import conn_data, logs_folder
from time import sleep
import os

from requests import get
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from make_log import log_exceptions
from settings import WAIT_PERIOD, WEBDRIVER_FOLDER_PATH

chrome_options = webdriver.ChromeOptions()
driver = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
wait = int(WAIT_PERIOD)

if not os.path.exists(logs_folder):
    os.mkdir(logs_folder)

class FillPortalData:

    def __init__(self, mss_no):
        self.mss_no = mss_no
        self.data = dict()
        r1 = requests.post("https://vnusoftware.com/iclaimtestmax/api/preauth", data={"pid": self.mss_no})
        if r1.status_code == 200:
            self.data = r1.json()
            fields = (
            'insurer', 'process', 'field', 'is_input', 'path_type', 'path_value', 'api_field', 'default_value', 'step')
            with mysql.connector.connect(**conn_data) as con:
                cur = con.cursor()
                query = "SELECT * FROM paths where insurer = %s order by seq"
                cur.execute(query, (self.data['0']['InsurerID'],))
                result = cur.fetchall()
                records = []
                for i in result:
                    row = dict()
                    for j, k in zip(fields, i):
                        row[j] = k
                    temp = self.data
                    row['value'] = ''
                    if row['api_field'] is not None and row['api_field'] != '':
                        if '+' in row['api_field']:
                            temp_string = ''
                            for j in row['api_field'].split('+'):
                                temp1 = temp
                                for k in j.split(':'):
                                    try:
                                        temp1 = temp1[k.strip()]
                                    except TypeError:
                                        with open('logs/api_field_error.log', 'a') as fp:
                                            print(self.mss_no, row['api_field'], sep=',', file=fp)
                                temp_string = temp_string + ' ' + temp1
                            row['value'] = temp_string
                        elif ':' in row['api_field']:
                            for j in row['api_field'].split(':'):
                                try:
                                    temp = temp[j.strip()]
                                except TypeError:
                                    with open('logs/api_field_error.log', 'a') as fp:
                                        print(self.mss_no, row['api_field'], sep=',', file=fp)
                                    temp = ''
                            row['value'] = temp.strip()
                    records.append(row)
            self.data['db_data'] = records

    def get_api_field(self, api_field):
        if api_field != '':
            temp = self.data
            for i in api_field.split(','):
                temp = temp[i.strip()]
            return temp
        return ''

    def execute(self):
        records = self.data['db_data']
        for i in records:
            value = i['value']
            if i['field'] == 'portal_link':
                visit_portal(value)
            if i['is_input'] == 'I':
                path_type, path_value = i['path_type'], i['path_value']
                fill_input(value, path_type, path_value)
            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                press_button(path_type, path_value)



def check_portal(link):
    response = requests.get(link)
    status = response.status_code
    if status == 200:
        return True
    return False

def get_data_from_mssno_api(mssno):
    try:
        r1 = requests.post("https://vnusoftware.com/iclaimtestmax/api/preauth", data={"pid": mssno})
        if r1.status_code == 200:
            response = r1.json()
            if response['msg'] == 'Successfully Got Records':
                return response
            else:
                return {'error': 'invalid mssno'}
    except requests.exceptions.ConnectionError:
        return {'error': 'mssno api server down'}

def get_data_from_db(insurer_id):
    fields = ('insurer','process','field','is_input','path_type','path_value','api_field','default_value','step')
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        query = "SELECT * FROM paths where insurer = %s"
        cur.execute(query, (insurer_id, ))
        result = cur.fetchall()
        records = []
        for i in result:
            row = dict()
            for j, k in zip(fields, i):
                row[j] = k
            records.append(row)
    return records

def visit_portal(link):
    if check_portal(link):
        driver.get(link)
        return True
    return False

def fill_input(data, path_type, path):
    if path_type == 'xpath':
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path))).send_keys(data)
    pass

def press_button(path_type, path):
    if path_type == 'xpath':
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path))).click()

if __name__ == '__main__':
    portal = FillPortalData('MSS-1003113')
    for i in portal.data['db_data']:
        print(i['value'])
    portal.execute()
    pass