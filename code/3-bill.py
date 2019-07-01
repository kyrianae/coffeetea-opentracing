import time
from flask import Flask
from flask import request
import json
from flask_cors import CORS
import random
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

tracer = trace.init_tracer('billing', tracer_server, tracer_port)

app = Flask(__name__)
CORS(app)


@app.route('/bill/<payment>/<name>')
def bill(payment, name):
    span = trace.newspan(tracer,
                         trace.getparentspanfromheader(tracer, request),
                         'bill')
    span.set_tag('customer', name)
    span.set_tag('payment', payment)

    res = trace.inject_in_header( tracer, span, {})

    res = API.call_api(data_server, data_port, '/cashin/'+payment, res)
    span.finish()
    sspan = trace.newspan(tracer, span.context, payment)

    time.sleep(random.randint(0, 200) / 1000)

    response = app.response_class(
        response=json.dumps({}),
        status=200,
        mimetype='application/json'
    )

    sspan.finish()
    return response


# Run server
app.run(port=bill_port, host='0.0.0.0')

