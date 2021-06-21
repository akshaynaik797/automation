from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from settings import WAIT_PERIOD, WEBDRIVER_FOLDER_PATH, chrome_options

wait = WAIT_PERIOD
driver = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
driver.get('https://css-tricks.com/examples/DragAndDropFileUploading/?submit-on-demand')
xp = '/html/body/div/form/div[1]/input'
WebDriverWait(driver, wait).until(EC.visibility_of_element_located((By.XPATH, xp))).click()
pass