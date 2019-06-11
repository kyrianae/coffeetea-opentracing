import time
import random
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


tracer=init_tracer('produce')

# Flask
app = Flask(__name__)
CORS(app)

coffee_bean=0
tea_leaf=0
water=0
total=0
client=0
coffe_in_progress=0
tea_in_progress=0
root = 'http://127.0.0.1'
fill_coffee_in_progress =  False
fill_water_in_progress =  False
fill_tea_in_progress =  False

def gett():
    return str(time.time())

def call_api(port,path, header):
    print('call api ' +path)
    urllib3.disable_warnings(InsecureRequestWarning)
    result = requests.get(root+':'+str(port)+path, headers=header, verify=False)
    # result.raise_for_status()
    return result

@app.route('/state')
def state():
    global tea_leaf,coffee_bean,water,total,client,coffe_in_progress ,tea_in_progress,fill_coffee_in_progress ,fill_water_in_progress,fill_tea_in_progress

    res = {
        'tea_leaf':tea_leaf,
        'coffee_bean':coffee_bean,
        'water':water,
        'total':total,
        'client':client,
        'coffe_in_progress':coffe_in_progress,
        'tea_in_progress':tea_in_progress,
        'fill_coffee_in_progress':fill_coffee_in_progress,
        'fill_water_in_progress':fill_water_in_progress,
        'fill_tea_in_progress':fill_tea_in_progress
    }
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/produce/<drink>')
def produce_drink(drink):
    print ('produce '+drink)
    global water,coffee_bean,tea_leafw

    # 'stock.water':str(water),'stock.coffee':str(coffee_bean),'stock.tea':str(tea_leaf)}
    response = app.response_class(
        status=404,
        mimetype='application/json'
    )

    parentspan = tracer.extract(
        Format.HTTP_HEADERS,
        request.headers
    )

    span = tracer.start_span(drink, child_of=parentspan)
    res = {}
    tracer.inject(
        span_context=span.context,
        format=Format.HTTP_HEADERS,
        carrier=res)

    state = json.loads(call_api(5003, '/state', res).content.decode())

    # span_context = propagator.from_header(request.header)
    # with tracer.span(name=drink+gett()) as span:

    error = False
    if True:
        # span.parent_span=request.headers['parent']
        if state['water'] <= 0:
            call_api(5003, '/add/water', res)
            # span.add_annotation('need water')
        else:
            if drink == 'coffee' and state['coffee_bean'] <= 0:
                call_api(5003, '/add/coffee', res)
                error = True
                # span.add_annotation('need coffee')
            elif drink == 'tea' and state['tea_leaf'] <= 0:
                call_api(5003, '/add/' + drink, res)
                error = True
                # span.add_annotation('need tea')
            else:
                call_api(5003, '/consume/water', res)
                if drink == 'coffee':
                    # coffee_bean += -1
                    call_api(5003, '/consume/coffee', res)
                    time.sleep(random.randint(0,500) / 1000)
                else:
                    # tea_leaf += -1
                    call_api(5003, '/consume/tea', res)
                    time.sleep(random.randint(0, 500) / 1000)
                response = app.response_class(
                    # response=json.dumps(res),
                    status=200,
                    mimetype='application/json'
                )
        print (drink + ' produced')
        # span.status = status.Status( response.status,'TODO')

        span.set_tag('error', error)
        span.finish()
        return response

# Run server
app.run(port=5001, host='0.0.0.0')