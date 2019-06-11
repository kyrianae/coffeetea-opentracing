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

jtracer_buy=init_tracer('buy')


tracer_producetea =init_tracer('produce_tea')
tracer_producecoffee=init_tracer('produce_coffee')

# tracer_buy = Tracer(exporter=ZipkinExporter(service_name="buy",
#                                             host_name='localhost',
#                                             port=9411,
#                                             endpoint='/api/v2/spans')
#                     , sampler=always_on.AlwaysOnSampler())
#
# tracer_bill = Tracer(exporter=ZipkinExporter(service_name="bill",
#                                 host_name='localhost',
#                                 port=9411,
#                                 endpoint='/api/v2/spans')
# , sampler=always_on.AlwaysOnSampler())
# tracer_producetea = Tracer(exporter=ZipkinExporter(service_name="produce-tea",
#                                 host_name='localhost',
#                                 port=9411,
#                                 endpoint='/api/v2/spans')
# , sampler=always_on.AlwaysOnSampler())
# tracer_producecoffee = Tracer(exporter=ZipkinExporter(service_name="produce-coffee",
#                                 host_name='localhost',
#                                 port=9411,
#                                 endpoint='/api/v2/spans')
# , sampler=always_on.AlwaysOnSampler())
# tracer_addwater = Tracer(exporter=ZipkinExporter(service_name="add-water",
#                                 host_name='localhost',
#                                 port=9411,
#                                 endpoint='/api/v2/spans')
# , sampler=always_on.AlwaysOnSampler())
# tracer_addtea = Tracer(exporter=ZipkinExporter(service_name="add-tea",
#                                 host_name='localhost',
#                                 port=9411,
#                                 endpoint='/api/v2/spans')
# , sampler=always_on.AlwaysOnSampler())
# tracer_addcoffee= Tracer(exporter=ZipkinExporter(service_name="add-coffee",
#                                 host_name='localhost',
#                                 port=9411,
#                                 endpoint='/api/v2/spans')
# , sampler=always_on.AlwaysOnSampler())


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
root = 'http://127.0.0.1:5000'
fill_coffee_in_progress =  False
fill_water_in_progress =  False
fill_tea_in_progress =  False

def gett():
    return str(time.time())

def call_api(path, header):
    print('call api ' +path)
    urllib3.disable_warnings(InsecureRequestWarning)
    result = requests.get(root+path, headers=header, verify=False)
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

@app.route('/add/coffee')
def add_coffee():
    print ('add coffee')
    global coffee_bean, fill_coffee_in_progress

    cf = False
    cw = False

    if not fill_coffee_in_progress:
        fill_coffee_in_progress = True
        logging.info('filling coffee tank')
        time.sleep(3)
        coffee_bean += 40
        fill_coffee_in_progress = False
        logging.info('filled coffee tank')
        cf = True

    while (fill_coffee_in_progress):
        logging.info('waiting end of tea filling')
        time.sleep(1)
        cw = True
    res = {
           'cw':str(cw),
           'cf':str(cf)
    }
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype = 'application/json'
    )

    return response


@app.route('/add/tea')
def add_tea():
    print ('add tea')
    global tea_leaf, fill_tea_in_progress

    tf = False
    tw = False

    if not fill_tea_in_progress:
        fill_tea_in_progress = True
        logging.info('filling teat tank')
        time.sleep(2)
        tea_leaf += 20
        fill_tea_in_progress = False
        logging.info('filled tea tank')
        tf = True

    while (fill_tea_in_progress):
        logging.info('waiting end of tea filling')
        time.sleep(1)
        tw = True
    res = {
           'tw':str(tw),
           'tf':str(tf)
    }
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype = 'application/json'
    )

    return response

@app.route('/add/water')
def add_water():
    print ('add water')
    global water,fill_water_in_progress

    wf=False
    ww=False

    if not fill_water_in_progress:
        fill_water_in_progress = True
        logging.info('filling water tank')
        time.sleep(3)
        water += 100
        fill_water_in_progress = False
        logging.info('filled water tank')
        wf=True

    while (fill_water_in_progress):
        logging.info('waiting end of water filling')
        time.sleep(1)
        ww=True
    res = {
           'ww':str(ww),
           'wf':str(wf)
    }
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )

    return response

@app.route('/buy/<drink>/<name>')
def buy_drink(drink,name):
    global tea_in_progress, client, coffe_in_progress
    jspan = jtracer_buy.start_span(name+gett())
    # span = tracer_buy.span(name="main")
    # with tracer_buy.span(name=name+gett()) as span:
    if True:
        print (name+' buys '+drink)
        # span.add_annotation(name+' buys '+drink)
        if drink == 'tea':
            tea_in_progress += 1
        else:
            coffe_in_progress += 1
        client += 1
        res = {}
        # 'name':name,
        #        'client': str(client),
        #        'drink': drink}
        jtracer_buy.inject(
            span_context=jspan.context,
            format=Format.HTTP_HEADERS,
            carrier=res)

        # logging.info('customer ' +str(res['client']) + ' ask for '+drink)
        # span.

        r = call_api('/produce/'+drink,res)
        if r.status_code == 200 :
            call_api('/bill', res)
        response = app.response_class(
            response=json.dumps(res),
            status=r.status_code,
            mimetype='application/json'
        )

        if drink == 'tea':
            tea_in_progress+= -1
        else:
            coffe_in_progress+= -1

        # span.status= status.Status(r.status_code,r.reason)
        jspan.finish()
        return response

@app.route('/produce/<drink>')
def produce_drink(drink):
    print ('produce '+drink)
    # print(request.headers
    global water,coffee_bean,tea_leaf
    res = {'stock.water':str(water),'stock.coffee':str(coffee_bean),'stock.tea':str(tea_leaf)}
    response = app.response_class(
        status=404,
        mimetype='application/json'
    )


    tracer = jtracer_buy
    # if drink == 'tea':
    #     tracer = tracer_producetea
    # else :
    #     tracer = tracer_producecoffee

    parentspan = tracer.extract(
        Format.HTTP_HEADERS,
        request.headers
    )

    span = tracer.start_span(drink+gett(), child_of=parentspan)
    # span_context = propagator.from_header(request.header)
    # with tracer.span(name=drink+gett()) as span:
    if True:
        # span.parent_span=request.headers['parent']
        if water <= 0:
            call_api('/add/water',res)
            # span.add_annotation('need water')
        else:
            if drink == 'coffee' and coffee_bean <=0:
                call_api('/add/coffee',res)
                # span.add_annotation('need coffee')
            elif drink == 'tea' and tea_leaf <=0:
                call_api('/add/' + drink, res)
                # span.add_annotation('need tea')
            else:
                water += -1
                if drink == 'coffee ':
                    coffee_bean += -1
                else:
                    tea_leaf += -1
                response = app.response_class(
                    # response=json.dumps(res),
                    status=200,
                    mimetype='application/json'
                )
        print (drink + ' produced')
        # span.status = status.Status( response.status,'TODO')
        span.finish()
        return response

@app.route('/bill')
def bill():
    global total
    total +=1
    res = {'total': str(total),
           }
    logging.info('total ' +str(res['total']) + ' $')
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    return response

# Run server
app.run(port=5000, host='0.0.0.0')


