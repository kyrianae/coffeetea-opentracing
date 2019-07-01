import time
import random
from flask import Flask
from flask import request
import json
from flask_cors import CORS
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

tracer = trace.init_tracer('produce', tracer_server, tracer_port)

app = Flask(__name__)
CORS(app)


@app.route('/produce/<drink>')
def produce_drink(drink):
    print('produce '+drink)

    response = app.response_class(
        status=404,
        mimetype='application/json'
    )

    span = trace.newspan(
        tracer,
        trace.getparentspanfromheader(tracer, request),
        drink
    )
    res = trace.inject_in_header(tracer, span, {})

    result = API.call_api(data_server, data_port, '/state', res)
    decoded = result.content.decode()
    _state = json.loads(decoded)

    error = False
    if True:
        if _state['water'] <= 0:
            API.call_api(data_server, data_port, '/resource/add/water', res)
        else:
            if drink == 'coffee' and _state['coffee_bean'] <= 0:
                API.call_api(data_server, data_port, '/resource/add/' + drink, res)
                error = True
                span.set_tag('reason', 'need ' + drink)
            elif drink == 'tea' and _state['tea_leaf'] <= 0:
                API.call_api(data_server, data_port, '/resource/add/' + drink, res)
                error = True
                span.set_tag('reason', 'need '+drink)
            else:
                r = API.call_api(data_server, data_port, '/consume/water', res)
                if r.status_code == 200:
                    API.call_api(data_server, data_port, '/consume/'+drink, res)
                    time.sleep(random.randint(0, 500) / 1000)

                    response = app.response_class(
                        status=200,
                        mimetype='application/json'
                    )
                    print(drink + ' produced')

        # span.status = status.Status( response.status,'TODO')

        span.set_tag('error', error)
        span.finish()
        return response


# Run server
app.run(port=produce_port, host='0.0.0.0')

