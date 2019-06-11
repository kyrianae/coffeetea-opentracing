import time
from flask import Flask
from flask import request
import subprocess
import datetime
import json
import os
from flask_cors import CORS
import logging
from urllib3.exceptions import InsecureRequestWarning
import requests
import urllib3
import socket
import random
from multiprocessing.dummy import Pool as ThreadPool

nb_client = 200
root = 'http://127.0.0.1:5000'


from jaeger_client import Config
from opentracing import Format

def init_tracer(service):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': "127.0.0.1",
                'reporting_port': 6831,
            },
            'logging': True,
        },
        service_name=service,
    )
    # this call also sets opentracing.tracer
    return config.initialize_tracer()


tracer=init_tracer('customer')


def call_api(path, header):
    global root
    # print('call api ' +path)
    urllib3.disable_warnings(InsecureRequestWarning)
    result = requests.get(root+path, headers=header, verify=False)
    print('call api ' + path +' ' +str(result.status_code))
    result.raise_for_status()
    return result


class client():
    def __init__(self,name):
        self.name=name
        self.energy=0

    def drink(self):
        r = random.getrandbits(1)
        try:
            if  r == 0:
                call_api('/buy/coffee/'+self.name,{})
                self.energy=2
            else:
                call_api('/buy/tea/' + self.name,{})
                self.energy=3
            self.last=True
        except:
            self.last=False

    def live(self):
        while (True):
            if self.energy <= 0:
                self.drink()
            self.energy+= -1
            time.sleep(0.5)


def launch(o):
    o.live()

clients=[]
for i in range (0,nb_client,1):
    clients.append(client('customer_'+str(i)))

pool = ThreadPool(nb_client)
results = pool.map(launch,clients)
pool.close()