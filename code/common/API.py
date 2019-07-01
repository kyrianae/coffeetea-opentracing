# https://scihub.copernicus.eu/dhus/search?q=*
from urllib3.exceptions import InsecureRequestWarning
import requests
import urllib3


def call_api(root, port, path, header):
    print('call api ' + path)
    urllib3.disable_warnings(InsecureRequestWarning)
    result = requests.get(root+':'+str(port)+path, headers=header, verify=False)
    return result
