from selenium import webdriver

driver_port = 9990
server_port = 5000
screenshot_folder = 'screenshots'
attachments_folder = 'attachments'
logs_folder = 'logs'

conn_data = {'host': "iclaimdev.caq5osti8c47.ap-south-1.rds.amazonaws.com",
             'user': "admin",
             'password': "Welcome1!",
             'database': 'portals'}

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_experimental_option("debuggerAddress", f"localhost:{driver_port}")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("window-size=1300,768")


# full path of chromedriver folder
WEBDRIVER_FOLDER_PATH = "/home/akshay/Downloads/chromedriver"

# period in seconds to wait for loading websites
WAIT_PERIOD = 20
