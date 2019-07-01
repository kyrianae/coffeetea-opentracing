#!/usr/bin/python3
import os
from flask import Flask
import json
from flask_cors import CORS
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

tracer = trace.init_tracer('buy', tracer_server, tracer_port)

app = Flask(__name__)
CORS(app)


@app.route('/buy/<drink>/<payment>/<name>')
def buy_drink(drink, payment, name):
    span = trace.newspan(tracer, None, 'transaction')
    span.set_tag('drink', drink)
    span.set_tag('customer', name)
    span.set_tag('payment', payment)

    res = trace.inject_in_header(tracer, span, {})

    span.finish()

    if True:
        print(name+' buys '+drink)
        API.call_api(data_server, data_port, '/wip/add/'+drink, res)
        API.call_api(data_server, data_port, '/add/client', res)
        r = API.call_api(produce_server, produce_port, '/produce/'+drink, res)

        if r.status_code == 200:
            r = API.call_api(bill_server, bill_port, '/bill/' + payment + '/' + name, res)
            if r.status_code == 200:
                span.set_tag('error', False)
            else:
                span.set_tag('error', True)
                span.set_tag('bill', r.status_code)
        else:
            span.set_tag('error', True)
        response = app.response_class(
            response=json.dumps(res),
            status=r.status_code,
            mimetype='application/json'
        )
        API.call_api(data_server, data_port, '/wip/sup/'+drink, res)
        return response

# Run server
app.run(port=buy_port, host='0.0.0.0')

