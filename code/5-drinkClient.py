import time
from urllib3.exceptions import InsecureRequestWarning
import urllib3
import random
from multiprocessing.dummy import Pool as ThreadPool
# from flask import Flask
# from flask_cors import CORS
from common import trace
from common import API
import os

tracer_server = os.environ["tracer_server"]
tracer_port = os.environ["tracer_port"]
data_server = os.environ["data_server"]
data_port = os.environ["data_port"]
produce_server = os.environ["produce_server"]
produce_port = os.environ["produce_port"]
bill_server = os.environ["bill_server"]
bill_port = os.environ["bill_port"]
buy_server = os.environ["buy_server"]
buy_port = os.environ["buy_port"]
influx_server = os.environ["influx_server"]
influx_port = os.environ["influx_port"]
influx_user = os.environ["influx_user"]
influx_pwd = os.environ["influx_pwd"]
influx_db = os.environ["influx_db"]
client_port = os.environ["client_port"]

tracer = trace.init_tracer('customer', tracer_server, tracer_port)

# app = Flask(__name__)
# CORS(app)

nb_client = 100
drinks = ['coffee', 'tea']
means_of_payment = ['gold', 'card']
energy = {
    'coffee': 3,
    'tea': 2
    }
clients = []

urllib3.disable_warnings(InsecureRequestWarning)


class Client:
    def __init__(self, name):
        self.name = name
        self.energy = 0
        self.last = True
        self.ready = True

    def drink(self):
        r = random.getrandbits(1)
        p = means_of_payment[random.getrandbits(1)]
        try:
            res = API.call_api(buy_server, buy_port, '/buy/'+drinks[r]+'/' + p + '/' + self.name, {})
            print('/buy/'+drinks[r]+'/' + p + '/' + self.name+' > '+str(res))
            self.energy = energy.get(drinks[r])

            self.last = True
        except Exception as e:
            print(e)
            self.last = False

    def live(self):
        while self.ready:
            if self.energy <= 0:
                self.drink()
            self.energy += -1
            time.sleep(0.5)


def launch(o):
    o.live()


for i in range(0, nb_client, 1):
    clients.append(Client('customer_'+str(i)))


pool = ThreadPool(nb_client)
results = pool.map(launch, clients)
pool.close()


# #TODO add configuration via http API
# @app.route('/config/<number>')
# def config(number):
#     print(number)
#     return None
#
# @app.route('/state')
# def state():
#         return None
