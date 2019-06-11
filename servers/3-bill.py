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
import random
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


tracer=init_tracer('billing')

# Flask
app = Flask(__name__)
CORS(app)

root = 'http://127.0.0.1:5003'

def gett():
    return str(time.time())

def call_api(path, header):
    print('call api ' +path)
    urllib3.disable_warnings(InsecureRequestWarning)
    result = requests.get(root+path, headers=header, verify=False)
    # result.raise_for_status()
    return result

@app.route('/bill')
def bill():

    parentspan = tracer.extract(
        Format.HTTP_HEADERS,
        request.headers
    )
    span = tracer.start_span('bill', child_of=parentspan)
    res = {}
    tracer.inject(
        span_context=span.context,
        format=Format.HTTP_HEADERS,
        carrier=res)

    res=call_api('/cashin',res)
    span.finish()
    sspan = span = tracer.start_span('money', child_of=span)

    time.sleep(random.randint(0, 200) / 1000)

    # logging.info('total ' +str(res['total']) + ' $')
    response = app.response_class(
        response=json.dumps({}),
        status=200,
        mimetype='application/json'
    )

    sspan.finish()

    return response

# Run server
app.run(port=5002, host='0.0.0.0')


