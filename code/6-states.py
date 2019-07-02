import json
from time import sleep as sleep
from influxdb import InfluxDBClient
from common import trace
from common import API
import os

tracer_server = os.environ["tracer_server"]
tracer_port = os.environ["tracer_port"]
data_server = os.environ["data_server"]
data_port = os.environ["data_port"]
influx_server = os.environ["influx_server"]
influx_port = os.environ["influx_port"]
influx_user = os.environ["influx_user"]
influx_pwd = os.environ["influx_pwd"]
influx_db = os.environ["influx_db"]

tracer = trace.init_tracer('states', tracer_server, tracer_port)

client_influx = InfluxDBClient(influx_server, influx_port, influx_user, influx_pwd, influx_db)
client_influx.create_database(influx_db)

# app = Flask(__name__)
# CORS(app)
i = 0
while True:
    if i == 0:
        root = trace.newspan(tracer, None, 'root')
    i += 1
    if i == 10:
        root.finish()
        i = 0
    r = None
    try:
        span = trace.newspan(tracer, root.context, 'pushdata')
        sspan = trace.newspan(tracer, span.context, 'ask data')
        res = trace.inject_in_header(tracer, span, {})
        r = API.call_api(data_server, data_port, '/state', res)
        # print(r.content)
        j = json.loads(r.content.decode())
        sspan.finish()
        sspan = trace.newspan(tracer, sspan.context, 'push tea')
        json_body = [
            {
            "measurement": "coffeetea",
            "tags": {
                "type": "tea",
                "fill": j['fill_tea_in_progress'],
            },
            "fields": {
                "resource": j['tea_leaf'],
                "refills": 1.0 if j['fill_tea_in_progress'] else 0.0,
                "wip_produce": j['tea_in_progress'],
            }
        }
        ]
        # print(json_body)
        sspan.finish()
        sspan = trace.newspan(tracer, sspan.context, 'push coffee')
        client_influx.write_points(json_body)
        json_body = [
            {
                "measurement": "coffeetea",
                "tags": {
                    "type": "coffee",
                    "fill": j['fill_coffee_in_progress'],
                },

                "fields": {
                    "resource": j['coffee_bean'],
                    "refills": 1.0 if j['fill_coffee_in_progress'] else 0.0,
                    "wip_produce": j['coffee_in_progress'],
                }
            }
        ]
        # print(json_body)
        client_influx.write_points(json_body)
        sspan.finish()
        sspan = trace.newspan(tracer, sspan.context, 'push water')
        json_body = [
            {
                "measurement": "coffeetea",
                "tags": {
                    "type": "water",
                    "fill": j['fill_water_in_progress']
                },

                "fields": {
                    "refills": 1.0 if j['fill_water_in_progress'] else 0.0,
                    "resource": j['water'],

                }
            }
        ]
        # print(json_body)
        client_influx.write_points(json_body)
        sspan.finish()
        sspan = trace.newspan(tracer, sspan.context, 'push stats')
        json_body = [
            {
                "measurement": "stats",
                "tags": {
                    "type": "gold"
                },

                "fields": {
                    "value": j['total'],
                    "clients": j['client']
                }
            }
        ]
        # print(json_body)
        client_influx.write_points(json_body)
        sspan.finish()
    except:
        print('not reached or error')
    span.finish()

    sleep(0.5)
