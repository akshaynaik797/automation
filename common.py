import json
import subprocess

import requests

from features.environment import login_details_file, driver_port

window_id = ''

def is_browser_running():
    output = subprocess.check_output(["netstat", "-anutp", "2>/dev/null"]).decode("utf-8")
    if str(driver_port) in output and "chrome --remo" in output:
        return True
    return False


def start_browser():
    if not is_browser_running():
        # subprocess.Popen(
        #     f"google-chrome --headless --window-size=1366,768 --incognito --remote-debugging-port={driver_port}",
        #     shell=True)
        subprocess.Popen(
            f"google-chrome --incognito --remote-debugging-port={driver_port}",
            shell=True)
        pass

def get_data_from_mssno_api(mssno):
    try:
        r1 = requests.post("https://vnusoftware.com/iclaimtestmax/api/preauth", data={"pid": mssno})
        if r1.status_code == 200:
            response = r1.json()
            if response['msg'] == 'Successfully Got Records':
                pass
            else:
                response = {'error': 'invalid mssno'}
            with open(login_details_file, 'w') as json_file:
                json.dump(response, json_file)

    except requests.exceptions.ConnectionError:
        response = {'error': 'preauth api server down'}
        with open(login_details_file, 'w') as json_file:
            json.dump(response, json_file)


def open_tab(browser, main_window):
    browser.switch_to.window(main_window)
    browser.execute_script(f"window.open('');")
    b = browser.window_handles
    return b[-1]
