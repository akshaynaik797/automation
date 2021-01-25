import random
import time
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

from make_log import log_exceptions
from settings import WAIT_PERIOD, WEBDRIVER_FOLDER_PATH, attachments_folder, chrome_options
wait = WAIT_PERIOD
driver = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
driver.get('https://www.icicilombard.com/IL-HEALTH-CARE/Home/Login')
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, "//input[@id='username']"))).send_keys('ilhc2444')
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, "//input[@id='password']"))).send_keys('icicilombard1234')
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, "//input[@id='btnLogin']"))).click()
time.sleep(6)
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, "//*[contains(text(),'Add / View IPD PreAuth / Cashless Request')]"))).click()
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, "//input[@id='hcnUhid']"))).send_keys('123608668')
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, "//input[@id='btnSearch']"))).click()
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, "//input[@id='txtEmailAddress']"))).send_keys('tpappg@maxhealthcare.com')
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[2]/div[3]/div/button/span"))).click()
elements = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="link-table"]/div[2]/div/table/tbody/tr')))
for i, j in enumerate(elements):
    if 'ACTIVE' in j.text:
        j.click()
pass