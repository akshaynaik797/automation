import os
import random
from datetime import datetime
from distutils.dir_util import remove_tree
from itertools import zip_longest
from os import listdir
from os.path import abspath, isfile, join
from pathlib import Path
from time import sleep
from urllib.parse import urlparse
import tkinter as tk
from tkinter import messagebox

import mysql.connector
import pyautogui as pyautogui
import requests
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver

import make_log
from make_log import log_exceptions, custom_log_data
from settings import WAIT_PERIOD, attachments_folder
from settings import conn_data, logs_folder, grouping_data_api, \
    update_hospitaltlog_api, screenshot_folder, root_folder, setportalfieldvalues_api, \
    WEBDRIVER_FOLDER_PATH, chrome_options

wait = int(WAIT_PERIOD)

if not os.path.exists(logs_folder):
    os.mkdir(logs_folder)
if not os.path.exists(screenshot_folder):
    os.mkdir(screenshot_folder)

class FillPortal:
    def __init__(self, mss_no, hosp_id, **kwargs):
        self.mss_no = mss_no
        self.hosp_id = hosp_id
        self.data = dict()
        self.login_records = []
        self.records = []
        self.logout_records = []
        self.home_records = []
        self.anti_flag = 'H' #H -> ubuntu machine,  P -> package machine, A - > ALL
        self.transaction_id = ""

        if os.path.exists(root_folder):
            remove_tree(root_folder)
        tmp = os.path.join(root_folder, self.mss_no)
        Path(tmp).mkdir(parents=True, exist_ok=True)
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
            pname, insid = self.data['0']['PatientName'], self.data['0']['InsurerID']
            r2 = requests.post(setportalfieldvalues_api, data={"refno": self.mss_no, "pname": pname, "insid": insid})
            for i in self.data['0']['Lastdoc']:
                download_file1(i['Doc'], self.mss_no)
            fields = (
                'insurer', 'process', 'field', 'is_input', 'path_type', 'path_value', 'api_field',
                'default_value', 'step', 'seq', 'relation', 'flag')
            with mysql.connector.connect(**conn_data) as con:
                cur = con.cursor()
                query = "SELECT * FROM paths where insurer = %s and (seq is not Null or seq != '') order by seq"
                cur.execute(query, (self.data['0']['InsurerID'],))
                result = cur.fetchall()
                records = []
                for i in result:
                    row = dict()
                    for j, k in zip(fields, i):
                        row[j] = k
                    row['mss_no'] = self.mss_no
                    row['value'] = ''
                    if row['api_field'] is not None and row['api_field'] != '':
                        tmp = row['api_field']
                        if ';' in tmp:
                            value = ""
                            for i in tmp.split(';'):
                                temp = self.data
                                for j in i.split(':'):
                                    try:
                                        temp = temp[j.strip()]
                                    except TypeError:
                                        with open('logs/api_field_error.log', 'a') as fp:
                                            print(str(datetime.now()), self.mss_no, j, row['api_field'], sep=',', file=fp)
                                    except:
                                        log_exceptions()
                                        temp = ''
                                if isinstance(temp, str):
                                    value += temp.strip()
                            row['value'] = value
                        elif ':' in tmp:
                            temp = self.data
                            for j in tmp.split(':'):
                                try:
                                    temp = temp[j.strip()]
                                except TypeError:
                                    with open('logs/api_field_error.log', 'a') as fp:
                                        print(str(datetime.now()), self.mss_no, j, row['api_field'], sep=',', file=fp)
                                except:
                                    log_exceptions()
                                    temp = ''
                            if isinstance(temp, str):
                                row['value'] = temp.strip()
                    records.append(row)
            self.data['db_data'] = records
            self.status = self.data['0']['Currentstatus']
            if 'status' in kwargs:
                self.status = kwargs['status']
            # custom_log_data(mss_no=self.mss_no, status=self.status, records=self.data['db_data'], filename="records_db")
            for i in self.data['db_data']:
                if i['process'] == 'login':
                    self.login_records.append(i)
                if i['process'] == 'logout':
                    self.logout_records.append(i)
                if i['process'] == 'HOME':
                    self.home_records.append(i)
                if i['process'].strip() in self.status:
                    self.records.append(i)

    def get_api_field(self, api_field):
        if api_field != '':
            temp = self.data
            for i in api_field.split(','):
                temp = temp[i.strip()]
            return temp
        return ''

    def visit_portal(self, **kwargs):
        if 'driver' in kwargs:
            driver = kwargs['driver']
        for i in self.login_records:
            value = i['value']
            message = i['field']
            step = i['step']
            if self.anti_flag == i['flag']:
                continue
            if 'link' in message:
                try:
                    flag = visit_portal(value, driver=driver)
                    if flag is True:
                        status = 'pass'
                    else:
                        status = 'fail'
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message='visit portal failed')
                filename = f"{random.randint(99999, 999999)}.png"
                sleep(1)
                driver.save_screenshot(screenshot_folder + '/' + filename)
                insert_log('', self.transaction_id, self.mss_no, self.data['0']['InsurerID'], "visit_portal", step,
                           status, message, filename, value)
                return driver.current_url
        return None

    def login(self, **kwargs):
        step, message, value, status = "", "", "", ""
        if 'driver' in kwargs:
            driver = kwargs['driver']
        for i in self.login_records:
            # if status == 'fail':
            #     break
            value = i['value']
            message = i['field']
            step = i['step']
            default_value = i['default_value']
            if self.anti_flag == i['flag']:
                continue
            if i['is_input'] == 'I' and 'link' not in i['field']:
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    fill_input(value, path_type, path_value, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            if i['is_input'] == 'C':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    while 1:
                        sleep(10)
                        if get_input(value, path_type, path_value, driver=driver):
                            status = 'pass'
                            break
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)

            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    press_button(path_type, path_value, i, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            filename = f"{random.randint(99999, 999999)}.png"
            sleep(1)
            driver.save_screenshot(screenshot_folder + '/' + filename)
            insert_log('', self.transaction_id, self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'],
                       step,
                       status, message, filename, value)
        if status == 'fail':
            return False
        return True

    def logout(self, **kwargs):
        step, message, value, status = "", "", "", ""
        if 'driver' in kwargs:
            driver = kwargs['driver']
        for i in self.logout_records:
            # if status == 'fail':
            #     break
            value = i['value']
            message = i['field']
            step = i['step']
            default_value = i['default_value']
            if self.anti_flag == i['flag']:
                continue
            if i['field'] == 'portal_link':
                try:
                    visit_portal(value, driver=driver)
                    status = 'pass'
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            if i['is_input'] == 'I':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    fill_input(value, path_type, path_value, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    press_button(path_type, path_value, i, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            filename = f"{random.randint(99999, 999999)}.png"
            sleep(1)
            driver.save_screenshot(screenshot_folder + '/' + filename)
            insert_log('', self.transaction_id, self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'],
                       step,
                       status, message, filename, value)
        if status == 'fail':
            return False
        return True


    def home(self, **kwargs):
        step, message, value, status = "", "", "", ""
        if 'driver' in kwargs:
            driver = kwargs['driver']
        for i in self.home_records:
            # if status == 'fail':
            #     break
            value = i['value']
            message = i['field']
            step = i['step']
            default_value = i['default_value']
            if value == '' or value is None:
                value = i['default_value']
            if self.anti_flag == i['flag']:
                continue
            if i['is_input'] == 'Link':
                try:
                    flag = visit_portal(value, driver=driver)
                    if flag is True:
                        status = 'pass'
                    else:
                        status = 'fail'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)

            if i['is_input'] == 'B':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    press_button(path_type, path_value, i, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            filename = f"{random.randint(99999, 999999)}.png"
            sleep(1)
            driver.save_screenshot(screenshot_folder + '/' + filename)
            insert_log('', self.transaction_id, self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'],
                       step,
                       status, message, filename, value)
        if status == 'fail':
            return False
        return True


    def execute(self, **kwargs):
        step, message, value, status = "", "", "", ""
        if 'driver' in kwargs:
            driver = kwargs['driver']
        i_value = None
        for i in self.records:
            #commented to excute after excepetion
            # if status == 'fail':
            #     break
            value = i['value']
            message = i['field']
            step = i['step']
            default_value = i['default_value']
            if self.anti_flag == i['flag']:
                continue
            if value == '' or value is None:
                value = i['default_value']
            if i['is_input'] == 'Link':
                try:
                    flag = visit_portal(value, driver=driver)
                    if flag is True:
                        status = 'pass'
                    else:
                        status = 'fail'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            if i['is_input'] == 'I':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    fill_input(value, path_type, path_value, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)

            if i['is_input'] == 'B' or i['is_input'] == 'LINK':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    if '{i}' in path_value:
                        path_value = path_value.replace('{i}', f"[{i_value}]")
                    if '||' in path_value:
                        path_list = path_value.split('||')
                        for xp in path_list:
                            try:
                                wait = 5
                                element = WebDriverWait(driver, wait) \
                                    .until(EC.visibility_of_element_located((By.XPATH, xp)))
                                ele_value = element.text
                                if ele_value == value:
                                    path_value = xp
                                    break
                            except TimeoutException:
                                pass
                    press_button(path_type, path_value, i, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            if i['is_input'] == 'S':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    i_value = search_and_click(path_type, path_value, i, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            if i['is_input'] == 'RB':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    press_radio_button(path_type, path_value, i, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            if i['is_input'] == 'LIST':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    if path_type == 'xpath':
                        # press_button(path_type, path_value, i, driver=driver)
                        upload_file(self.mss_no, path_value, driver=driver)
                    else:
                        select_option(value, path_type, path_value, driver=driver)
                    status = 'pass'
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            if i['is_input'] == 'code':
                path_type, path_value = i['path_type'], i['path_value']
                try:
                    exec_code(value, path_value, driver=driver, data=self.data)
                except TimeoutException:
                    log_exceptions(row=i)
                    status = 'fail with timeout'
                    dialog(value=value, step=step, status=status, message=message)
                except:
                    status = 'fail'
                    log_exceptions(row=i)
                    dialog(value=value, step=step, status=status, message=message)
            filename = f"{random.randint(99999, 999999)}.png"
            sleep(1)
            driver.save_screenshot(screenshot_folder + '/' + filename)
            insert_log('', self.transaction_id, self.mss_no, self.data['0']['InsurerID'], self.data['0']['Currentstatus'],
                       step,
                       status, message, filename, value)
        if status == 'fail':
            return False
        return True

def run(**kwargs):
    response, step = {}, ""
    try:
        if 'status' in kwargs and kwargs['status'] != 'None':
            portal = FillPortal(kwargs['mss_no'], kwargs['hosp_id'], status=kwargs['status'])
        else:
            portal = FillPortal(kwargs['mss_no'], kwargs['hosp_id'])
        driver = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
        z = portal.visit_portal(driver=driver)
        if z is None or z == 'data:,':
            step = "portal check"
            custom_log_data(filename='failed_portal', mssno=portal.mss_no, porta_link=portal.data['0']['PortalLink'])
            response = {'error': "see logs", "step": step}
        else:
            step = "login"
            if portal.login(driver=driver):
                step = "home"
                driver.refresh()
                if portal.home(driver=driver):
                    step = "execution"
                    if portal.execute(driver=driver):
                        response = {'msg': 'success'}
            else:
                response = {'error': "see logs", "step": step}
    except (KeyboardInterrupt, SystemExit):
        pass
    except:
        make_log.log_exceptions(data=kwargs)
    finally:
        submit_dialog()
        driver.quit()
        if os.path.exists(root_folder):
            remove_tree(root_folder)
    return response

def dialog(step, message, value, status, **kwargs):
    msg = f'Do you want to run further or cancel the script?\nstep= {step}\nstatus= {status}' \
          f'\nmessage= {message}\nvalue= {value}\nPressing cancel will close browser.'
    root = tk.Tk()
    root.withdraw()
    tmp = messagebox.askokcancel(title=None, message=msg, icon='error')
    root.update()
    if tmp:
        return tmp
    exit()

def submit_dialog():
    msg = "Clicking 'OK' would close the browser, so please complete the submission of documents, and then press 'OK'."
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(title=None, message=msg, icon='error')
    root.update()

def exec_code(value, path_value, **kwargs):
    data = kwargs['data']
    if 'driver' in kwargs:
        driver = kwargs['driver']
    if path_value == 'code_upload_preauth_icici':
        code_upload_preauth_icici(data, driver=driver)
    if path_value == 'code_upload_preauth_fhpl':
        code_upload_preauth_fhpl(data, driver=driver)
    if path_value == 'code_upload_enhance_fhpl':
        code_upload_enhance_fhpl(data, driver=driver)
    if path_value == 'code_upload_query_fhpl':
        code_upload_query_fhpl(data, driver=driver)
    if path_value == 'code_calendar_preauth_icici':
        code_calendar_preauth_icici(path_value, value, driver=driver)

def upload_file(mss_no, path, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    mypath = os.path.join(root_folder, mss_no)
    onlyfiles = [abspath(join(mypath, f)) for f in listdir(mypath) if isfile(join(mypath, f))]
    try:
        for j in onlyfiles:
            WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, path))).send_keys(j)
    except ElementNotInteractableException:
        for j in onlyfiles:
            WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, path))).click()
            pyautogui.write(j)
            pyautogui.press('enter')
            pass

def code_upload_preauth_fhpl(data, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    mss_no = data['0']['RefNo']
    xpath_list = ['//*[@id="fupreauthForm"]', '//*[@id="fuPatientIDProof"]', '//*[@id="fuInvestigationFile"]']
    btn_list = ['//*[@id="ContentPlaceHolder1_TabContainer1_tbAddDocuments_btnPreauthForm"]',
                '//*[@id="ContentPlaceHolder1_TabContainer1_tbAddDocuments_btnPatienIDProof"]',
                '//*[@id="ContentPlaceHolder1_TabContainer1_tbAddDocuments_btnInvestigationFile"]']
    mypath = os.path.join(root_folder, mss_no)
    onlyfiles = [abspath(join(mypath, f)) for f in listdir(mypath) if isfile(join(mypath, f))]
    if len(onlyfiles) == 1:
        onlyfiles = onlyfiles * 3
    for file_btn, upload_btn, fpath in zip(xpath_list, btn_list, onlyfiles):
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, file_btn))).send_keys(fpath)
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, upload_btn))).click()
        alert = Alert(driver)
        alert.accept()

def code_upload_enhance_fhpl(data, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    mss_no = data['0']['RefNo']
    file_input, add_btn = '//*[@id="ContentPlaceHolder1_TabContainer1_tbAddFiles_MultipleFileUpload1_fuUpload"]', \
                          '//*[@id="ContentPlaceHolder1_TabContainer1_tbAddFiles_MultipleFileUpload1_btnAdd"]'
    mypath = os.path.join(root_folder, mss_no)
    onlyfiles = [abspath(join(mypath, f)) for f in listdir(mypath) if isfile(join(mypath, f))]
    for fpath in onlyfiles:
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, file_input))).send_keys(fpath)
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, add_btn))).click()

def code_upload_query_fhpl(data, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    mss_no = data['0']['RefNo']
    #file_input = '//*[@id="ContentPlaceHolder1_MultipleFileUpload1_pnlFiles"]'
    #file_input = '//*[@id="ContentPlaceHolder1_MultipleFileUpload1_fuUpload"]'
    file_input, add_btn = '//*[@id="ContentPlaceHolder1_MultipleFileUpload1_fuUpload"]', \
                          '//*[@id="ContentPlaceHolder1_TabContainer1_tbAddFiles_MultipleFileUpload1_btnAdd"]'
    mypath = os.path.join(root_folder, mss_no)
    onlyfiles = [abspath(join(mypath, f)) for f in listdir(mypath) if isfile(join(mypath, f))]
    for fpath in onlyfiles:
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, file_input))).send_keys(fpath)
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, add_btn))).click()


def code_upload_preauth_icici(data, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    mss_no = data['0']['RefNo']
    mypath = os.path.join(root_folder, mss_no)
    onlyfiles = [abspath(join(mypath, f)) for f in listdir(mypath) if isfile(join(mypath, f))]
    lastdocs = data['0']['Lastdoc']
    lenth = len(lastdocs)
    cnt = 2
    add_more = '//*[@id="table-bottom"]/div[3]/input'
    for fp in onlyfiles:
        option, button = f'//*[@id="ddlDocumentType{cnt}"]/option[14]', f'//*[@id="btnBrowse{cnt}"]'
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, option))).click()
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, button))).send_keys(fp)
        if lenth > 1:
            WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, add_more))).click()
        cnt = cnt + 1

def code_calendar_mb(xpath, value, **kwargs):
    #format to submit is 28-Feb-2021
    if 'driver' in kwargs:
        driver = kwargs['driver']
    try:
        element = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.execute_script('arguments[0].removeAttribute("readonly")', element)
        element.clear()
        element.send_keys(value)
        return True
    except:
        log_exceptions()
        return False

def code_calendar_preauth_icici(xpath, value, **kwargs):
    #format to submit is 21/03/2021
    if 'driver' in kwargs:
        driver = kwargs['driver']
    try:
        element = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.execute_script('arguments[0].removeAttribute("readonly")', element)
        element.clear()
        element.send_keys(value)
        return True
    except:
        log_exceptions()
        return False

def code_calendar_hdfc(xpath, value, **kwargs):
    #format to submit is 21/03/2021
    if 'driver' in kwargs:
        driver = kwargs['driver']
    try:
        element = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.execute_script('arguments[0].removeAttribute("readonly")', element)
        element.clear()
        element.send_keys(value)
        return True
    except:
        log_exceptions()
        return False

def code_calendar_hdfc_admn(xpath, value, **kwargs):
    #format to submit is 21/03/2021
    if 'driver' in kwargs:
        driver = kwargs['driver']
    try:
        element = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.execute_script('arguments[0].removeAttribute("readonly")', element)
        element.clear()
        element.send_keys(value)
        return True
    except:
        log_exceptions()
        return False

def code_calendar_preauth_star(xpath, value, field, **kwargs):
    #format to submit is 28-Feb-2021 12:14:15
    if 'driver' in kwargs:
        driver = kwargs['driver']
    if field == 'doa':
        no = '2'
    else:
        no = 4
    time = datetime.strptime('%d/%b/%Y %H:%M:%S', value).strftime('%d/%b/%Y %H:%M:%p')
    time = time.split(' ')[-1]
    date = datetime.strptime('%d-%B-%Y %H:%M:%S', value)
    h, m, p = time.split(':')
    ampm = f'//*[@id="myForm"]/div[{no}]/div[2]/div/div/table/tbody/tr[2]/td[6]/button'
    mm = f'//*[@id="myForm"]/div[2]/div[{no}]/div/div/table/tbody/tr[2]/td[3]/input'
    hh = f'//*[@id="myForm"]/div[2]/div[{no}]/div/div/table/tbody/tr[2]/td[1]/input'
    try:
        element = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, xpath)))
        driver.execute_script('arguments[0].removeAttribute("readonly")', element)
        element.clear()
        element.send_keys(date)
        WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, mm))).send_keys(m)
        WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, hh))).send_keys(h)
        if p == 'PM':
            WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, ampm))).click()
        return True
    except:
        log_exceptions()
        return False

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

def visit_portal(link, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    if check_portal(link):
        driver.get(link)
        return True
    return False

def fill_input(data, path_type, path, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    if path_type == 'xpath':
        element = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path)))
        element.send_keys(data)

def get_input(data, path_type, path, **kwargs):
    value = None
    if 'driver' in kwargs:
        driver = kwargs['driver']
    if path_type == 'xpath':
        element = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path)))
        value = element.get_attribute("value")
        return value

def search_and_click(path_type, path, path_row, **kwargs):
    wait = 5
    if 'driver' in kwargs:
        driver = kwargs['driver']
    value = path_row['value']
    if value == '':
        value = path_row['default_value']
    if path_type == 'xpath':
        try:
            for i in range(10):
                try:
                    tmp_path = path
                    tmp_path = tmp_path.replace('{i}', f"[{i}]")
                    element = WebDriverWait(driver, wait) \
                        .until(EC.visibility_of_element_located((By.XPATH, tmp_path)))
                    ele_value = element.text
                    if value == ele_value:
                        return i
                except:
                    pass

        except:
            log_exceptions()

def press_radio_button(path_type, path, path_row, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    if path_type == 'xpath':
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path))).click()

def press_button(path_type, path, path_row, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    seq, result = int(path_row['seq']) + 1, None
    if path_type == 'xpath':
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, path))).click()

def upload_file(mss_no, path, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
    mypath = os.path.join(root_folder, mss_no)
    onlyfiles = [abspath(join(mypath, f)) for f in listdir(mypath) if isfile(join(mypath, f))]
    try:
        for j in onlyfiles:
            WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, path))).send_keys(j)
    except ElementNotInteractableException:
        for j in onlyfiles:
            WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, path))).click()
            pyautogui.write(j)
            pyautogui.press('enter')
            pass

def select_option(data, path_type, path, **kwargs):
    if 'driver' in kwargs:
        driver = kwargs['driver']
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
    fields = ('sno', 'insid', 'type', 'status', 'flag')
    with mysql.connector.connect(**conn_data) as con:
        cur = con.cursor()
        flag = '1'
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

def update_hospitaltlog(**kwargs):
    fields = 'fStatus', 'fLock', 'Type_Ref'
    url = update_hospitaltlog_api
    x = requests.post(url, data=kwargs)
    return x.text

def download_file1(url, mss_no):
    # open in binary mode
    a = urlparse(url)
    # print(a.path)
    # print(os.path.basename(a.path))
    tmp = os.path.join(root_folder, mss_no)
    Path(tmp).mkdir(parents=True, exist_ok=True)
    with open(tmp + '/' + os.path.basename(a.path), "wb") as file:
        # get request
        response = requests.get(url)
        # write to file
        file.write(response.content)
        return os.path.abspath(tmp + '/' + os.path.basename(a.path))

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
    run(mss_no='NH-1004598', hosp_id='8900080123380')