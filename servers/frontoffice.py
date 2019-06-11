# import json
from traceback import print_exc
import os
# import zipfile
# from tests.common.image_processing import GDALCalcNDVI
# import time
from urllib3.exceptions import InsecureRequestWarning
import requests
import urllib3
import socket
# import urllib
from urllib.parse import urljoin


class Product:
    def __init__(self):
        self.uid = ""
        self.sizemb = 0.
        self.header = ""
        self.dl_file_root_dir = ""
        self.dl_file_full_path = ""


def get_product(p_header, my_service_result):
    urllib3.disable_warnings(InsecureRequestWarning)
    # cmd = url + "search/arlas/explore/catalog/_search?&f=" + api_command
    if __debug__:
        print("start download")
    result = requests.get(my_service_result.url, headers=p_header, verify=False)
    my_service_result.resultcode = result.status_code
    if __debug__:
        print("end download")
    # result = requests.get(cmd, verify=False)
    # Throw an error for bad status codes
    result.raise_for_status()
    return result


def search_product(search_url, my_service_result):
    # product = None
    # try:
    # Set-up config
    product = Product()
    my_service_result.host = socket.gethostname()

    # Destination directory is working directory.
    product.dl_file_root_dir = os.getcwd()
    product.dl_file_full_path = os.path.join(product.dl_file_root_dir, 'frontofficeimg.zip')

    # Search for the image through the API.
    if __debug__:
        print("\nAPI Search;\n")
    # start_time = time.time()
    # result = search_by_external_id(external_id, website_url)
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    result = requests.get(search_url, verify=False)
    my_service_result.resultcode = result.status_code
    # elapsed_time = time.time() - start_time
    # print("Time elapsed: {:3.3f} seconds".format(elapsed_time))
    if __debug__:
        print(result.reason)

    # Extract the image internal ID from the search result.
    json_result = result.json()
    if __debug__:
        print(str(json_result).encode('utf-8'))
    product.uid = json_result['hits'][0]['data']['uid']
    if __debug__:
        print("\nProduct internal id: " + product.uid)
        print("Archive size is " + str(product.sizemb) + " MB")

    # except Exception as e:
    #     print("An error occurred")
    #     print("Message : " + str(e))
    #     print("Stack trace : ")
    #     print_exc()
    #     product = None

    # finally:
    return product


def download_product(api_key, product, my_service_result):
    my_service_result.host = socket.gethostname()
    # try:
    # Download the image.
    if __debug__:
        print("\nAPI Download\n")
        print("Downloading product ...")
    # start_time = time.time()
    header = {'Authorization': "Apikey " + api_key}
    result = get_product(header, my_service_result)
    my_service_result.resultcode = result.status_code
    if __debug__:
        print(result)

    # current_block_number = 1
    total_block_number = 1024
    with open(product.dl_file_full_path, 'wb') as handle:
        for block in result.iter_content(total_block_number):
            handle.write(block)
            # print(str(current_block_number/total_block_number) + "%")
            # current_block_number = current_block_number + 1
    # elapsed_time = time.time() - start_time
    # print("Time elapsed: {:3.3f} seconds".format(elapsed_time))

    # Unzip contents
    # zip_file = zipfile.ZipFile(product.dl_file_full_path)
    # print("\nUnzipping file " + product.dl_file_full_path + " ...")
    # zip_file.extractall(product.dl_file_root_dir)
    # zip_file.close()
    # print("File unzipped to directory : " + str(product.dl_file_root_dir) + "\n")

    # if not no_processing:
    #     # Apply NDVI processing. Output image is in working directory.
    #     SAFE_product_path = os.path.join(dl_file_root_dir, image_external_id + ".SAFE")
    #     obj = GDALCalcNDVI()
    #     obj.run(SAFE_product_path, dl_file_root_dir, cloud_optimized)

    if os.path.isfile(product.dl_file_full_path):
        file_stat = os.stat(product.dl_file_full_path)
        product.sizemb = file_stat.st_size / 1024
        os.remove(product.dl_file_full_path)
    else:
        print("ERROR: File not downloaded: " + product.dl_file_full_path)
        raise FileNotFoundError

    # except Exception as e:
    #     print("An error occurred")
    #     print("Message : " + str(e))
    #     print("Stack trace : ")
    #     print_exc()
    #     status = -1
    #
    # finally:
    return 0

