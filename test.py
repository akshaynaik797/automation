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
driver.get('https://www.icicilombard.com/IL-HEALTH-CARE')
xp = '//*[@id="username"]'
value = 'ilhc2444'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = '//*[@id="password"]'
value = 'icicilombard1234'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = '//*[@id="btnLogin"]'
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '//*[@id="content"]/ul/li[1]/div[1]/div[1]/span[1]/a'
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '//*[@id="hcnUhid"]'
value = 'IL18679704801'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = '//*[@id="btnSearch"]'
value = '8564249-2'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '//*[@id="link-table"]/div[2]/div/table/tbody/tr/td[1]'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '/html/body/div[1]/div[3]/div/div[6]/form/div[1]/div[5]/div[2]/p[1]/input[1]'
value = 'mediclaim.noble@gmail.com'
doa = WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp)))
doa.click()
b = doa.get_attribute('value')
driver.execute_script('arguments[0].removeAttribute("readonly")', doa)
doa.clear()
doa.send_keys('21/03/2021')
code_upload_preauth_icici(data, driver=driver)
pass
