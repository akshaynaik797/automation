import random
from time import sleep

from features.environment import WAIT_PERIOD, screenshot_folder

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from make_log import log_exceptions

wait = WAIT_PERIOD

username_xpath = '/html/body/form/div[3]/center/table/tbody/tr[4]/td/table/tbody/tr[3]/td/table/tbody/tr[2]/td[2]/input'
password_xpath = '/html/body/form/div[3]/center/table/tbody/tr[4]/td/table/tbody/tr[3]/td/table/tbody/tr[3]/td[2]/input'
login_btn_xpath = '/html/body/form/div[3]/center/table/tbody/tr[4]/td/table/tbody/tr[3]/td/table/tbody/tr[4]/td/input'
invalid_login_xpath = '/html/body/form/div[3]/center/table/tbody/tr[4]/td/table/tbody/tr[3]/td/span'
logout_btn_xpath = '/html/body/form/div[3]/center/table/tbody/tr[3]/td/div[1]/ul/li[6]/a'


def pre_login(url, tab_id, driver):
    driver.switch_to.window(tab_id)
    driver.get(url)
    try:
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, username_xpath)))
    except TimeoutException:
        pass
    filename = f"{random.randint(99999, 999999)}.png"
    sleep(1)
    driver.save_screenshot(screenshot_folder + '/' + filename)
    return filename

def fill_username(username, tab_id, driver):
    filename = ''
    driver.switch_to.window(tab_id)
    WebDriverWait(driver, wait) \
        .until(EC.visibility_of_element_located((By.XPATH, username_xpath))).send_keys(username)
    filename = f"{random.randint(99999, 999999)}.png"
    sleep(1)
    driver.save_screenshot(screenshot_folder + '/' + filename)
    return filename


def fill_password(password, tab_id, driver):
    filename = ''
    driver.switch_to.window(tab_id)
    WebDriverWait(driver, wait) \
        .until(EC.visibility_of_element_located((By.XPATH, password_xpath))).send_keys(password)
    filename = f"{random.randint(99999, 999999)}.png"
    sleep(1)
    driver.save_screenshot(screenshot_folder + '/' + filename)
    return filename


def press_login(tab_id, driver):
    filename = ''
    driver.switch_to.window(tab_id)
    WebDriverWait(driver, wait) \
        .until(EC.visibility_of_element_located((By.XPATH, login_btn_xpath))).click()
    WebDriverWait(driver, wait) \
        .until(EC.visibility_of_element_located((By.XPATH, logout_btn_xpath)))
    filename = f"{random.randint(99999, 999999)}.png"
    sleep(1)
    driver.save_screenshot(screenshot_folder + '/' + filename)
    return filename

def check_if_logged_in(tab_id, driver):
    filename = ''
    driver.switch_to.window(tab_id)
    WebDriverWait(driver, wait) \
        .until(EC.visibility_of_element_located((By.XPATH, logout_btn_xpath)))
    filename = f"{random.randint(99999, 999999)}.png"
    sleep(1)
    driver.save_screenshot(screenshot_folder + '/' + filename)
    return filename

def login(username, password, tab_id, driver):
    filename = ''
    try:
        driver.switch_to.window(tab_id)
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, username_xpath))).send_keys(username)
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, password_xpath))).send_keys(password)
        WebDriverWait(driver, wait) \
            .until(EC.visibility_of_element_located((By.XPATH, login_btn_xpath))).click()
        try:
            WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, logout_btn_xpath)))
            filename = f"{random.randint(99999, 999999)}.png"
            sleep(1)
            driver.save_screenshot(screenshot_folder + '/' + filename)
            message = 'credentials working.'
            return True, message, filename
        except TimeoutException:
            error = WebDriverWait(driver, wait) \
                .until(EC.visibility_of_element_located((By.XPATH, invalid_login_xpath))).get_attribute('innerText')
            filename = f"{random.randint(99999, 999999)}.png"
            sleep(1)
            driver.save_screenshot(screenshot_folder + '/' + filename)
            message = 'wrong credentials'
            if "Invalid UserName or Password" in error:
                pass
            return False, message, filename
    except TimeoutException:
        log_exceptions()
        message = 'wrong xpaths in check_credentials, see logs'
        return False, message, filename
    except:
        log_exceptions()
        message = 'error in check_credentials, see logs'
        return False, message, filename