from selenium import webdriver
import os

driver_port = 9990
server_port = 5000
root_folder = 'automation_data'
screenshot_folder = 'screenshots'
attachments_folder = 'attachments'
logs_folder = 'logs'
setportalfieldvalues_api = "http://15.206.235.20:9982/setportalfieldvalues"

screenshot_url = "http://3.7.8.68:9982/screenshot/"
grouping_data_api = 'http://3.7.8.68:9980/get_hospitaltlog'
update_hospitaltlog_api = 'http://3.7.8.68:9980/update_hospitaltlog'
mss_no_data_api = "https://vnusoftware.com/iclaimmax/api/preauth"

conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
             'user': "admin",
             'password': "Welcome1!",
             'database': 'portals'}

#####for test purpose
# conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
#              'user': "admin",
#              'password': "Welcome1!",
#              'database': 'portals_rep'}
######

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('prefs', {
"download.default_directory": os.path.abspath(attachments_folder), #Change default directory for downloads
"download.prompt_for_download": False, #To auto download the file
"download.directory_upgrade": True,
"plugins.always_open_pdf_externally": True #It will not show PDF directly in chrome
})
# chrome_options.add_experimental_option("debuggerAddress", f"localhost:{driver_port}")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("window-size=1300,768")


# full path of chromedriver folder
# WEBDRIVER_FOLDER_PATH = "/home/akshay/Downloads/chromedriver"
WEBDRIVER_FOLDER_PATH = "chromedriver"


# period in seconds to wait for loading websites
WAIT_PERIOD = 20
