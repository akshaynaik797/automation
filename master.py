from trigger import behave_main
from common import get_data_from_mssno_api

mss_no = 'MSS-1003069' #appolo
get_data_from_mssno_api(mss_no)
behave_main(['-t @login'])