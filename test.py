import random
import time
from copy import deepcopy
from urllib.parse import urlparse

import requests
import mysql.connector
from datetime import datetime

from selenium.webdriver.common.keys import Keys

from common import code_upload_preauth_icici
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

from make_log import log_exceptions
from settings import WAIT_PERIOD, WEBDRIVER_FOLDER_PATH, attachments_folder, chrome_options
wait = WAIT_PERIOD
import json

with open('temp.json') as fp:
    data = json.load(fp)
driver = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
a = driver.current_url
driver.get('https://heapp5.hdfcergo.com/ProviderPortal')
xp = '//*[@id="txtUserName"]'
value = 'HEGIC-HS-06338'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = '//*[@id="txtPassword"]'
value = 'noble@123'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = '//*[@id="btnDirectLogin"]'
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
driver.get('https://heapp5.hdfcergo.com/ProviderPortal/GeneratePreauth/GeneratePreauthClaim?ClaimNO=RC-HS20-12316878&ActionType=EN')
xp = '/html/body/div[2]/div/div[5]/div[2]/a'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '//*[@id="txtAdmissionDate"]'
doa = WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp)))
doa.click()
b = doa.get_attribute('value')
driver.execute_script('arguments[0].removeAttribute("readonly")', doa)
doa.clear()
doa.send_keys('21/03/2021')
pass
