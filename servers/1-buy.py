import time

# from basictracer import propagator
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

# from opencensus.trace.tracer import Tracer
# from opencensus.trace import time_event as time_event_module
# from opencensus.ext.zipkin.trace_exporter import ZipkinExporter
# from opencensus.ext.prometheus.stats_exporter import PrometheusStatsExporter
# from opencensus.trace.samplers import always_on
# from opencensus.trace import status


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

tracer=init_tracer('buy')


# Flask
app = Flask(__name__)
CORS(app)

# coffee_bean=0
# tea_leaf=0
# water=0
# total=0
# client=0
# coffe_in_progress=0
# tea_in_progress=0
root = 'http://127.0.0.1'
# fill_coffee_in_progress =  False
# fill_water_in_progress =  False
# fill_tea_in_progress =  False

def gett():
    return str(time.time())

def call_api(port,path, header):
    print('call api ' +path)
    urllib3.disable_warnings(InsecureRequestWarning)
    result = requests.get(root+':'+str(port)+path, headers=header, verify=False)
    # result.raise_for_status()
    return result


@app.route('/buy/<drink>/<name>')
def buy_drink(drink,name):
    # global tea_in_progress, client, coffe_in_progress
    span = tracer.start_span('transaction')
    span.set_tag('drink',drink)
    span.set_tag('customer',name)
    #+gett()
    # span = tracer_buy.span(name="main")
    # with tracer_buy.span(name=name+gett()) as span:
    res = {}
    tracer.inject(
        span_context=span.context,
        format=Format.HTTP_HEADERS,
        carrier=res)

    if True:
        print (name+' buys '+drink)
        # span.add_annotation(name+' buys '+drink)
        if drink == 'tea':
            call_api(5003,'/add/wiptea',res)
        else:
            call_api(5003,'/add/wipcoffee', res)

        call_api(5003,'/add/client',res)
        # client += 1

        # 'name':name,
        #        'client': str(client),
        #        'drink': drink}


        # logging.info('customer ' +str(res['client']) + ' ask for '+drink)
        # span.

        r = call_api(5001,'/produce/'+drink,res)
        if r.status_code == 200 :
            call_api(5002,'/bill', res)
            span.set_tag('error', False)
        else:
            span.set_tag('error', True)
        response = app.response_class(
            response=json.dumps(res),
            status=r.status_code,
            mimetype='application/json'
        )


        if drink == 'tea':
            call_api(5003, '/sup/wiptea', res)
        else:
            call_api(5003, '/sup/wipcoffee', res)

        # span.status= status.Status(r.status_code,r.reason)
        span.finish()
        return response

# Run server
app.run(port=5000, host='0.0.0.0')


