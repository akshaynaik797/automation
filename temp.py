import json

from common import get_data_from_mssno_api
from features.environment import login_details_file

b = '0,PortalLink'.split(",")
mss_no = 'MSS-1003069'  # appolo
get_data_from_mssno_api(mss_no)
with open(login_details_file, 'r') as json_file:
    a = json.load(json_file)
    for i in b:
        a = a[i]
pass