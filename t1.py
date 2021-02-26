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
a = driver.current_url
driver.get('https://provider.ihx.in/#')
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/section/section/div[3]/form/div[1]/input"))).send_keys('GirishS1000945@medibuddy.in')
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, '//*[@id="exampleInputPassword1"]'))).send_keys('Noble@123')
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/section/section/div[3]/form/div[4]/div/button[1]"))).click()
time.sleep(8)
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div/div/form/div[2]/button"))).click()
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/section/header/div[2]/a[1]"))).click()
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabclaim-new"]/div[5]/h4/div/div/label[1]/span'))).click()
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabclaim-new"]/div[5]/form/div/div[1]/input-control/div/div/input'))).send_keys('5043550787')
WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabclaim-new"]/div[5]/form/div/div[2]/input-control/div/div/input'))).send_keys('billekal')
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, '//*[@id="tabclaim-new"]/div[5]/form/div/div[3]/button'))).click()
xp = '/html/body/div[1]/section/section/div/div[8]/div/div/div/div/a'
WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '//*[@id="myForm"]/div[3]/div[1]/div/div[1]/input-control/div/div/div/input'
doa = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, xp)))
a = doa.get_attribute('value')
driver.execute_script('arguments[0].removeAttribute("readonly")', doa)
doa.clear()
doa.send_keys('28-Feb-2021')
# driver.execute_script("arguments[0].setAttribute('value',arguments[1])", doa, '28-Feb-2021')
b = doa.get_attribute('value')
pass