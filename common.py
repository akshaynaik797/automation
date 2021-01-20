from urllib.parse import urlparse

import requests
import mysql.connector
from datetime import datetime

from settings import conn_data, logs_folder, mss_no_data_api, grouping_data_api, update_hospitaltlog_api
from time import sleep
import os

from requests import get
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from make_log import log_exceptions
from settings import WAIT_PERIOD, WEBDRIVER_FOLDER_PATH, attachments_folder, chrome_options

driver = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
wait = int(WAIT_PERIOD)

if not os.path.exists(logs_folder):
    os.mkdir(logs_folder)


class FillPortalData:

    def __init__(self, mss_no):
        self.mss_no = mss_no
        self.data = dict()
        self.login_records = []
        self.records = []
        self.logout_records = []

        r1 = requests.post(mss_no_data_api, data={"pid": self.mss_no})
        if r1.status_code == 200:
            self.data = r1.json()
            fields = (
                'insurer', 'process', 'field', 'is_input', 'path_type', 'path_value', 'api_field',
                'default_value', 'step', 'seq')
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
                                            print(str(datetime.now()), self.mss_no, row['api_field'], sep=',', file=fp)
                                temp_string = temp_string + ' ' + temp1
                            row['value'] = temp_string
                        elif ':' in row['api_field']:
                            for j in row['api_field'].split(':'):
                                try:
                                    if j == '-1':
                                        temp = temp[int(j.strip())]
                                    else:
                                        temp = temp[j.strip()]
                                except TypeError:
                                    with open('logs/api_field_error.log', 'a') as fp:
                                        print(str(datetime.now()), self.mss_no, row['api_field'], sep=',', file=fp)
                                    temp = ''
                            row['value'] = temp.strip()
                    records.append(row)
            self.data['db_data'] = records
            self.status = self.data['0']['Currentstatus']
            for i in self.data['db_data']:
                if i['process'] == 'login':
                    self.login_records.append(i)
                if i['process'] == 'logout':
                    self.logout_records.append(i)
                if i['process'] == self.status:
                    self.records.append(i)

    def get_api_field(self, api_field):
        if api_field != '':
            temp = self.data
            for i in api_field.split(','):
                temp = temp[i.strip()]
            return temp
        return ''

    def login(self):
        for i in self.login_records:
            value = i['value']
            message = i['field']
            step = i['step']
            if i['field'] == 'portal_link':
                try:
                    visit_portal(value)
                    status = 'pass'
                except:
                    status = 'fail'
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                           status, message, '')
            if i['is_input'] == 'I':
                path_type, path_value = i['path_type'], i['path_value']
                step = 'fill_input'
                try:
                    fill_input(value, path_type, path_value)
                    status = 'pass'
                except:
                    status = 'fail'
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                           status, message, '')
            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                step = 'press_button'
                try:
                    press_button(path_type, path_value)
                    status = 'pass'
                except:
                    status = 'fail'
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                           status, message, '')

    def logout(self):
        for i in self.logout_records:
            value = i['value']
            message = i['field']
            step = i['step']
            if i['field'] == 'portal_link':
                try:
                    visit_portal(value)
                    status = 'pass'
                except:
                    status = 'fail'
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                           status, message, '')
            if i['is_input'] == 'I':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    fill_input(value, path_type, path_value)
                    status = 'pass'
                except:
                    status = 'fail'
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                           status, message, '')
            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    press_button(path_type, path_value)
                    status = 'pass'
                except:
                    status = 'fail'
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                           status, message, '')

    def execute(self):
        for i in self.records:
            try:
                value = i['value']
                message = i['field']
                step = i['step']
                if i['field'] == 'portal_link':
                    try:
                        visit_portal(value)
                        status = 'pass'
                    except:
                        status = 'fail'
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, '')
                    print(i['step'], i['value'])
                if i['is_input'] == 'I':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        fill_input(value, path_type, path_value)
                        status = 'pass'
                    except:
                        status = 'fail'
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, '')
                    print(i['step'], i['value'])
                if i['is_input'] == 'B':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        press_button(path_type, path_value)
                        status = 'pass'
                    except:
                        status = 'fail'
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, '')
                    print(i['step'], i['value'])
                if i['is_input'] == 'F':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        upload_file(value, path_type, path_value)
                        status = 'pass'
                    except:
                        status = 'fail'
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, '')
                    print(i['step'], i['value'])
                    z = 1
                if i['is_input'] == 'LIST':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        select_option(value, path_type, path_value)
                        status = 'pass'
                    except:
                        status = 'fail'
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, '')
                    print(i['step'], i['value'])
            except:
                z = 1


def insert_log(tab_id, transactionid, referenceno, insurer, process, step, status, message, url):
    try:
        data = (tab_id, transactionid, referenceno, insurer, process, step, status, message, url)
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            query = "insert into logs (tab_id, transactionid, referenceno, " \
                    "insurer, process, step, status, message, url) " \
                    "values (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            cur.execute(query, data)
            con.commit()
            return True
    except:
        log_exceptions()
        return False


def check_portal(link):
    try:
        response = requests.get(link)
        status = response.status_code
        if status == 200:
            return True
        return False
    except:
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
    fields = (
        'insurer', 'process', 'field', 'is_input', 'path_type', 'path_value', 'api_field', 'default_value', 'step')
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        query = "SELECT * FROM paths where insurer = %s"
        cur.execute(query, (insurer_id,))
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


def upload_file(data, path_type, path):
    file_path = download_file(data)
    WebDriverWait(driver, wait) \
        .until(EC.visibility_of_element_located((By.XPATH, path))).send_keys(file_path)


def select_option(data, path_type, path):
    select = Select(WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, path))))
    select.select_by_visible_text(data)
    pass


def grouping_ins_hosp():
    url = grouping_data_api
    myobj = {}
    x = requests.post(url, data=myobj)
    data = x.json()
    data_dict = dict()
    data_set = set()
    for i in data:
        data_set.add((i['HospitalID'], i['insurerID']))
    for i, j in data_set:
        data_dict[i + ',' + j] = []
        for record in data:
            if record['HospitalID'] == i and record['insurerID'] == j:
                data_dict[i + ',' + j].append(record)
    return data_dict


def update_hospitaltlog(**kwargs):
    fields = 'fStatus', 'fLock', 'Type_Ref'
    url = update_hospitaltlog_api
    x = requests.post(url, data=kwargs)


def download_file(url):
    # open in binary mode
    a = urlparse(url)
    # print(a.path)
    # print(os.path.basename(a.path))
    if not os.path.exists(attachments_folder):
        os.mkdir(attachments_folder)
    with open(attachments_folder + '/' + os.path.basename(a.path), "wb") as file:
        # get request
        response = requests.get(url)
        # write to file
        file.write(response.content)
        return os.path.abspath(attachments_folder + '/' + os.path.basename(a.path))


if __name__ == '__main__':
    while 1:
        try:
            a = grouping_ins_hosp()
            with open('logs/group_data.log', 'a') as fp:
                print('=' * 100, file=fp)
                print(str(datetime.now()), file=fp)
                print('-' * 100, file=fp)
                print(str(a), file=fp)
            for i in a:
                ########for test purpose
                if i != '8,16':
                    continue
                ########
                portal = FillPortalData(a[i][0]['Type_Ref'])
                portal.login()
                for j in a[i]:
                    try:
                        ########for test purpose
                        # if j['Type_Ref'] != 'MSS-1005451':
                        #     continue
                        ########
                        update_hospitaltlog(Type_Ref=j['Type_Ref'], fLock=1)
                        portal1 = FillPortalData(j['Type_Ref'])
                        portal1.execute()
                        update_hospitaltlog(Type_Ref=j['Type_Ref'], fLock=0, fStatus='X')
                    except:
                        log_exceptions()
                        update_hospitaltlog(Type_Ref=j['Type_Ref'], fLock=0, fStatus='E')
                portal.logout()
        except:
            log_exceptions()
        sleep(300)
