#!/usr/bin/python3
import os
import time
from flask import Flask
from flask import request
import json
from flask_cors import CORS
import logging
from influxdb import InfluxDBClient
import random

from common import trace
from common import API

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

tracer = trace.init_tracer('data', tracer_server, tracer_port)

client_influx = InfluxDBClient(influx_server, influx_port, influx_user, influx_pwd, influx_db)
client_influx.create_database(influx_db)

# Flask
app = Flask(__name__)
CORS(app)

total = 0
client = 0
progress = {
    'coffee': 0,
    'tea': 0
}
resources = {
    'water': 0,
    'coffee': 0,
    'tea': 0
}
fill = {
    'water': False,
    'coffee': False,
    'tea': False
}

@app.route('/state')
def state():
    global total, client
    global fill, resources
    print('state')
    span = trace.newspan(
        tracer,
        trace.getparentspanfromheader(tracer, request),
        'state')
    res = {
        'tea_leaf': resources['tea'],
        'coffee_bean': resources['coffee'],
        'water': resources['water'],
        'total': total,
        'client': client,
        'coffee_in_progress': progress['coffee'],
        'tea_in_progress': progress['tea'],
        'fill_coffee_in_progress': fill['coffee'],
        'fill_water_in_progress': fill['water'],
        'fill_tea_in_progress': fill['tea']
    }
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype='application/json'
    )
    span.finish()
    return response


@app.route('/resource/add/<resource>')
def add_resource(resource):
    print('add ' + resource)
    global fill, resources, progress
    span = trace.newspan(
        tracer,
        trace.getparentspanfromheader(tracer,request),
        'add'+resource)
    res = {}
    cf = False
    cw = False

    if not fill[resource]:
        fill[resource] = True
        logging.info('filling ' + resource + ' tank')

        if resource == 'coffee':
            t2s = random.randint(2500, 3500) / 1000
            add = 40
        elif resource == 'tea':
            t2s = random.randint(1500, 2500) / 1000
            add = 20
        else:
            t2s = random.randint(4500, 5500) / 1000
            add = 100
        time.sleep(t2s)
        resources[resource] += add
        json_body = [
            {
                "measurement": "rt",
                "tags": {
                    "type": resource
                },

                "fields": {
                    "resource": resources[resource],
                    "movement": add
                }
            }]

        client_influx.write_points(json_body)

        fill[resource] = False

        logging.info('filled ' + resource + ' tank')
        cf = True

    while fill[resource]:
        logging.info('waiting end of ' + resource + ' filling')
        time.sleep(1)
        cw = True
    res = {
           'cw': str(cw),
           'cf': str(cf)
    }
    response = app.response_class(
        response=json.dumps(res),
        status=200,
        mimetype = 'application/json'
    )
    span.finish()
    return response


@app.route('/add/client')
def add_client():
    global total, client
    span = trace.newspan(
        tracer,
        trace.getparentspanfromheader(tracer, request),
        'add client')
    res = {}

    print('add client')
    client += 1
    json_body = [
        {
            "measurement": "rt",
            "tags": {
                "type": "client"
            },

            "fields": {
                "resource": client,
                "movement": 1
            }
        }
    ]
    client_influx.write_points(json_body)

    response = app.response_class(
        response=json.dumps('OK'),
        status=200,
        mimetype='application/json'
    )
    span.finish()
    return response


@app.route('/wip/<action>/<drink>')
def wip(action, drink):
    global total, client, progress
    span = trace.newspan(
        tracer,
        trace.getparentspanfromheader(tracer, request),
        'wip '+action+' '+drink)
    print('wip '+action+' '+drink+' '+str(1 if action == 'sup' else -1))

    progress[drink] += 1 if action == 'sup' else -1
    if progress[drink] < 0:
        progress[drink] = 0

    response = app.response_class(
        response=json.dumps('OK'),
        status=200,
        mimetype='application/json'
    )

    json_body = [
        {
            "measurement": "wip",
            "tags": {
                "type": drink
            },

            "fields": {
                "resource": progress[drink]
            }
        }
    ]
    client_influx.write_points(json_body)
    span.finish()
    return response

@app.route('/cashin/<payment>')
def cash_in(payment):
    global total
    span = trace.newspan(
        tracer,
        trace.getparentspanfromheader(tracer, request),
        'cash_in '+payment)

    # parent_span = trace.getparent_spanfromheader(tracer,request)
    # span = trace.newspan(tracer, parent_span, 'cash in')
    print('cash_in '+payment)
    total += 1
    print('total ' + str(total) + ' $')
    response = app.response_class(
        response=json.dumps('OK'),
        status=200,
        mimetype='application/json'
    )
    span.finish()
    return response


@app.route('/consume/<r>')
def consume(r):
    global tea_leaf, coffee_bean, water
    s=200
    print('consume '+r)
    span = trace.newspan(
        tracer,
        trace.getparentspanfromheader(tracer, request),
        'consume '+r)
    res = trace.inject_in_header(tracer, span, {})

    error = False
    if resources[r] <= 0:
        API.call_api(data_server, data_port, '/resource/add/'+r, res, )
        s = 404
        error = True
    else:
        resources[r] += -1
        json_body = [
            {
                "measurement": "rt",
                "tags": {
                    "type": r
                },

                "fields": {
                    "resource": resources[r],
                    "movement": -1
                }
            }
        ]
        client_influx.write_points(json_body)

        time.sleep(random.randint(0, 50) / 1000)
        print(r+' ' + str(resources[r]))

    span.set_tag('error', error)
    res = {}
    response = app.response_class(
        response=json.dumps(res),
        status=s,
        mimetype='application/json'
    )
    span.finish()
    return response


# Run server
app.run(port=data_port, host='0.0.0.0')
