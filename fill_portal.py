import random
from copy import deepcopy
from urllib.parse import urlparse

import requests
import mysql.connector
from datetime import datetime

from settings import conn_data, logs_folder, mss_no_data_api, grouping_data_api, \
    update_hospitaltlog_api, screenshot_folder, screenshot_url
from time import sleep
import os

from requests import get
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from make_log import log_exceptions, custom_log_data
from settings import WAIT_PERIOD, WEBDRIVER_FOLDER_PATH, attachments_folder, chrome_options


wait = int(WAIT_PERIOD)

if not os.path.exists(logs_folder):
    os.mkdir(logs_folder)
if not os.path.exists(screenshot_folder):
    os.mkdir(screenshot_folder)


class FillPortal:
    def __init__(self, mss_no, hosp_id):
        self.mss_no = mss_no
        self.hosp_id = hosp_id
        self.data = dict()
        self.login_records = []
        self.records = []
        self.logout_records = []
        self.home_records = []
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            query = "SELECT apiLink FROM apisConfig where hospitalID=%s and processName='portal_automation' limit 1;"
            cur.execute(query, (self.hosp_id,))
            result = cur.fetchone()
            if result is not None:
                mss_no_data_api = result[0]
        r1 = requests.post(mss_no_data_api, data={"pid": self.mss_no})
        if r1.status_code == 200:
            self.data = r1.json()
            fields = (
                'insurer', 'process', 'field', 'is_input', 'path_type', 'path_value', 'api_field',
                'default_value', 'step', 'seq', 'relation')
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
                            if isinstance(temp, str):
                                row['value'] = temp.strip()
                            else:
                                row['value'] = temp
                    records.append(row)
            self.data['db_data'] = records
            self.status = self.data['0']['Currentstatus']
            custom_log_data(mss_no=self.mss_no, status=self.status, records=self.data['db_data'], filename="records_db")
            for i in self.data['db_data']:
                if i['process'] == 'login':
                    self.login_records.append(i)
                if i['process'] == 'logout':
                    self.logout_records.append(i)
                if i['process'] == 'HOME':
                    self.home_records.append(i)
                if i['process'] == self.status:
                    self.records.append(i)

    def get_api_field(self, api_field):
        if api_field != '':
            temp = self.data
            for i in api_field.split(','):
                temp = temp[i.strip()]
            return temp
        return ''

    def visit_portal(self):
        for i in self.login_records:
            value = i['value']
            message = i['field']
            step = i['step']
            if 'link' in message:
                try:
                    visit_portal(value)
                    status = 'pass'
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                filename = f"{random.randint(99999, 999999)}.png"
                sleep(1)
                driver.save_screenshot(screenshot_folder + '/' + filename)
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], "visit_portal", step,
                           status, message, screenshot_url + filename, value)
                return driver.current_url
        return None

    def login(self):
        for i in self.login_records:
            value = i['value']
            message = i['field']
            step = i['step']
            if i['is_input'] == 'I' and i['field'] != 'portal_link':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    fill_input(value, path_type, path_value)
                    status = 'pass'
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                filename = f"{random.randint(99999, 999999)}.png"
                sleep(1)
                driver.save_screenshot(screenshot_folder + '/' + filename)
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], "login", step,
                           status, message, screenshot_url + filename, value)
            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    press_button(path_type, path_value, i)
                    status = 'pass'
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                filename = f"{random.randint(99999, 999999)}.png"
                sleep(1)
                driver.save_screenshot(screenshot_folder + '/' + filename)
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], "login", step,
                           status, message, screenshot_url + filename, value)

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
                    log_exceptions(row=i)
                filename = f"{random.randint(99999, 999999)}.png"
                sleep(1)
                driver.save_screenshot(screenshot_folder + '/' + filename)
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], "logout", step,
                           status, message, screenshot_url + filename, value)
            if i['is_input'] == 'I':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    fill_input(value, path_type, path_value)
                    status = 'pass'
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                filename = f"{random.randint(99999, 999999)}.png"
                sleep(1)
                driver.save_screenshot(screenshot_folder + '/' + filename)
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], "logout", step,
                           status, message, screenshot_url + filename, value)
            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    press_button(path_type, path_value, i)
                    status = 'pass'
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                filename = f"{random.randint(99999, 999999)}.png"
                sleep(1)
                driver.save_screenshot(screenshot_folder + '/' + filename)
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], "logout", step,
                           status, message, screenshot_url + filename, value)

    def home(self):
        for i in self.home_records:
            value = i['value']
            message = i['field']
            step = i['step']
            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    press_button(path_type, path_value, i)
                    status = 'pass'
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                filename = f"{random.randint(99999, 999999)}.png"
                sleep(1)
                driver.save_screenshot(screenshot_folder + '/' + filename)
                insert_log('', '', self.mss_no, self.data['0']['InsurerID'], "home", step,
                           status, message, screenshot_url + filename, value)

    def execute(self):
        for i in self.records:
            try:
                value = i['value']
                message = i['field']
                step = i['step']
                if value == '' or value is None:
                    value = i['default_value']
                if i['field'] == 'portal_link':
                    try:
                        visit_portal(value)
                        status = 'pass'
                    except:
                        status = 'fail'
                        log_exceptions(row=i)
                    filename = f"{random.randint(99999, 999999)}.png"
                    sleep(1)
                    driver.save_screenshot(screenshot_folder + '/' + filename)
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, screenshot_url + filename, value)
                    print(i['step'], i['value'])
                if i['is_input'] == 'I':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        fill_input(value, path_type, path_value)
                        status = 'pass'
                    except:
                        status = 'fail'
                        log_exceptions(row=i)
                    filename = f"{random.randint(99999, 999999)}.png"
                    sleep(1)
                    driver.save_screenshot(screenshot_folder + '/' + filename)
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, screenshot_url + filename, value)
                    print(i['step'], i['value'])
                if i['is_input'] == 'B' or i['is_input'] == 'LINK':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        press_button(path_type, path_value, i)
                        status = 'pass'
                    except:
                        status = 'fail'
                        log_exceptions(row=i)
                    filename = f"{random.randint(99999, 999999)}.png"
                    sleep(1)
                    driver.save_screenshot(screenshot_folder + '/' + filename)
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, screenshot_url + filename, value)
                    print(i['step'], i['value'])
                if i['is_input'] == 'S':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        search_and_click(path_type, path_value, i)
                        status = 'pass'
                    except:
                        status = 'fail'
                        log_exceptions(row=i)
                    filename = f"{random.randint(99999, 999999)}.png"
                    sleep(1)
                    driver.save_screenshot(screenshot_folder + '/' + filename)
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, screenshot_url + filename, value)
                    print(i['step'], i['value'])
                if i['is_input'] == 'RB':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        press_radio_button(path_type, path_value, i)
                        status = 'pass'
                    except:
                        status = 'fail'
                        log_exceptions(row=i)
                    filename = f"{random.randint(99999, 999999)}.png"
                    sleep(1)
                    driver.save_screenshot(screenshot_folder + '/' + filename)
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, screenshot_url + filename, value)
                    print(i['step'], i['value'])
                if i['is_input'] == 'F':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        upload_file(value, path_type, path_value)
                        status = 'pass'
                    except:
                        status = 'fail'
                        log_exceptions(row=i)
                    filename = f"{random.randint(99999, 999999)}.png"
                    sleep(1)
                    driver.save_screenshot(screenshot_folder + '/' + filename)
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, screenshot_url + filename, value)
                    print(i['step'], i['value'])
                    z = 1
                if i['is_input'] == 'LIST':
                    path_type, path_value = i['path_type'], i['path_value']
                    try:
                        select_option(value, path_type, path_value)
                        status = 'pass'
                    except:
                        status = 'fail'
                        log_exceptions(row=i)
                    filename = f"{random.randint(99999, 999999)}.png"
                    sleep(1)
                    driver.save_screenshot(screenshot_folder + '/' + filename)
                    insert_log('', '', self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'], step,
                               status, message, screenshot_url + filename, value)
                    print(i['step'], i['value'])

            except:
                z = 1



def insert_log(tab_id, transactionid, referenceno, insurer, process, step, status, message, url, api_value):
    try:
        data = (tab_id, transactionid, referenceno, insurer, process, step, status, message, url, api_value)
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            query = "insert into logs (tab_id, transactionid, referenceno, " \
                    "insurer, process, step, status, message, url, api_value) " \
                    "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
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
        for i in range(2):
            element = WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, path)))
            element.send_keys(data)
            value = element.get_attribute("value")
            if value == data:
                break
        pass


def search_and_click(path_type, path, path_row):
    value = path_row['value']
    if value == '':
        value = path_row['default_value']
    if path_type == 'xpath':
        elements = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_all_elements_located((By.XPATH, path)))
        for i, j in enumerate(elements):
            if value in j.text:
                j.click()


def press_radio_button(path_type, path, path_row):
    if path_type == 'xpath':
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path))).click()


def press_button(path_type, path, path_row):
    seq, result = int(path_row['seq']) + 1, None
    if path_type == 'xpath':
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path))).click()
        with mysql.connector.connect(**conn_data) as con:
            cur = con.cursor()
            query = "select path_value from paths where insurer=%s and process=%s and seq=%s limit 1;"
            cur.execute(query, (path_row['insurer'], path_row['process'], seq))
            result = cur.fetchone()
        if result is not None:
            WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, result[0])))


def upload_file(data, path_type, path):
    for j in [i['Doc'] for i in data]:
        file_path = download_file(j)
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path))).send_keys(file_path)


def select_option(data, path_type, path):
    select = Select(WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, path))))
    select.select_by_visible_text(data)
    pass


def grouping_ins_hosp():
    url = grouping_data_api
    ######for test purpose
    # url = "http://localhost:9980/get_hospitaltlog"
    ######
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
    fields = ('sno', 'insid', 'type', 'status', 'flag')
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        flag = '1'
        #######for test purpose
        # flag = '0'
        #######
        query = f"SELECT * FROM auto_filing_process where flag = '{flag}'"
        cur.execute(query)
        result = cur.fetchall()
        records = []
        for i in result:
            row = dict()
            for j, k in zip(fields, i):
                row[j] = k
            records.append(row)
            processed = dict()
        processed1 = dict()

        for j in data_dict:
            for i in records:
                if ',' + i['insid'] in j:
                    processed[j] = data_dict[j]
        for j in processed:
            processed1[j] = []
        for j in processed:
            for k in processed[j]:
                for i in records:
                    if k['Type'] == i['type'] and k['status'] == i['status']:
                        if k not in processed1[j]:
                            processed1[j].append(k)
                        pass
    return processed1

def test_grouping_ins_hosp():
    url = grouping_data_api
    ######for test purpose
    url = "http://localhost:9980/get_hospitaltlog"
    ######
    myobj = {}
    x = requests.post(url, data=myobj)
    data = x.json()
    data_dict = dict()
    data_set = set()
    for i in data:
        data_set.add((i['HospitalID'], i['insurerID']))
    data_set = {('8', 'I15')}
    for i, j in data_set:
        data_dict[i + ',' + j] = []
        for record in data:
            if record['HospitalID'] == i and record['insurerID'] == j:
                data_dict[i + ',' + j].append(record)
    return data_dict


def update_hospitaltlog(**kwargs):
    fields = 'fStatus', 'fLock', 'Type_Ref'
    url = update_hospitaltlog_api
    #########for test purpose
    x = requests.post(url, data=kwargs)
    return x.text
    ########


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
            ####for test purpose
            a = grouping_ins_hosp()
            # a = test_grouping_ins_hosp()
            with open('logs/group_data.log', 'a') as fp:
                print('=' * 100, file=fp)
                print(str(datetime.now()), file=fp)
                print('-' * 100, file=fp)
                print(str(a), file=fp)
            for i in a:
                if len(a[i]) == 0:
                    continue
                ####for test purpose
                # zz = '36'
                # if zz in i:
                #     continue
                # zz = '6'
                # if zz in i:
                #     continue
                ####
                portal = FillPortalData(a[i][0]['Type_Ref'])
                driver = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
                z = portal.visit_portal()
                if z is None or z == 'data:,':
                    custom_log_data(filename='failed_portal', mssno=portal.mss_no, porta_link = portal.data['0']['PortalLink'])
                    continue
                portal.login()
                for j in a[i]:
                    try:
                        update_hospitaltlog(Type_Ref=j['Type_Ref'], fLock=1,
                                            Type=j['Type'], status=j['status'])
                        portal1 = FillPortalData(j['Type_Ref'])
                        portal1.home()
                        if len(portal1.records) > 0:
                            portal1.execute()
                            update_hospitaltlog(Type_Ref=j['Type_Ref'], fLock=0,
                                                fStatus='X', Type=j['Type'], status=j['status'])
                        else:
                            update_hospitaltlog(Type_Ref=j['Type_Ref'], fLock=0,
                                                fStatus='S', Type=j['Type'], status=j['status'])
                    except:
                        log_exceptions(j=j)
                        update_hospitaltlog(Type_Ref=j['Type_Ref'], fLock=0, fStatus='E',
                                            Type=j['Type'], status=j['status'])
                    finally:
                        driver.quit()
                portal.logout()
                driver.quit()
        except:
            log_exceptions()
            pass
        sleep(300)
