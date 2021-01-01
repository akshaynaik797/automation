import os
import sys

from selenium import webdriver

driver_port = 9990
server_port = 5000
screenshot_folder = 'screenshots'
attachments_folder = 'attachments'
io_folder = 'io'
folder_list = [screenshot_folder, attachments_folder, io_folder]
login_details_file = io_folder + '/' + 'login_details.json'
# full path of chromedriver folder
WEBDRIVER_FOLDER_PATH = "/home/akshay/Downloads/chromedriver"

# period in seconds to wait for loading websites
WAIT_PERIOD = 120


def before_all(context):
    for i in folder_list:
        if not os.path.exists(i):
            os.mkdir(i)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("debuggerAddress", f"localhost:{driver_port}")
    context.browser = webdriver.Chrome(WEBDRIVER_FOLDER_PATH, options=chrome_options)
    context.main_window = context.browser.window_handles[0]


def after_all(context):
    context.browser.quit()


def before_scenario(context, scenario):
    print(123)


def after_scenario(context, scenario):
    print(scenario.name, scenario.status)
    pass


def after_step(context, step):
    with open('temp.txt', 'a') as fp:
        print(step.name, step.status, context.data['msg'], file=fp)
    if step.status == 'failed':
        with open('steps.log', 'a') as fp:
            print(step.name, step.status, step.filename, step.line, step.exception, file=fp)

