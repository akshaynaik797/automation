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
driver.get('https://spp.starhealth.in/')
xp = '/html/body/div[1]/section/section/div[1]/div[2]/div/form/div[1]/input'
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = "/html/body/div[1]/section/section/div[1]/div[2]/div/form/div[2]/input"
value = 'noble123456'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = "/html/body/div[1]/section/section/div[1]/div[2]/div/form/button"
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = "/html/body/div[1]/section/header/div[3]/a"
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '//*[@id="tabclaim-new"]/div[4]/h4/div/div/label[1]/input'
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '//*[@id="tabclaim-new"]/div[4]/form/div/div[1]/input'
value = '8564249-2'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = "/html/body/div[1]/section/section/div[2]/div/div/div/div[4]/form/div/div[2]/input"
value = 'chhaya'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = '//*[@id="tabclaim-new"]/div[4]/form/div/div[3]/button'
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
xp = '//*[@id="tabclaim-new"]/div[7]/div/div/div/div/a'
value = 'mediclaim.noble@gmail.com'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()

xp = '//*[@id="datetimepicker"]'
doa = WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, xp)))
a = doa.get_attribute('value')
driver.execute_script('arguments[0].removeAttribute("readonly")', doa)
doa.clear()
doa.send_keys('28-Feb-2021')
b = doa.get_attribute('value')


xp = '//*[@id="myForm"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[3]/input'
value = '54'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = '//*[@id="myForm"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[1]/input'
value = '11'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)
xp = '//*[@id="myForm"]/div[2]/div[2]/div/div/table/tbody/tr[2]/td[6]/button'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()



# time = WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp)))
# WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
# WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).clear()
# driver.execute_script("arguments[0].setAttribute('value',arguments[1])", time, '28')
# WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).send_keys(value)


pass
