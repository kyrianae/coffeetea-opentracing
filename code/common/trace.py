import logging
from jaeger_client import Config
from opentracing import Format
import time


def init_tracer(service, host, port):
    logging.getLogger('').handlers = []
    logging.basicConfig(format='%(message)s', level=logging.INFO)
    config = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': host,
                'reporting_port': port,
            },
            'logging': True,
        },
        service_name=service,
    )
    # this call also sets opentracing.tracer
    return config.initialize_tracer()


def getparentspanfromjson(tracer, data):
    return tracer.extract(
                        Format.TEXT_MAP,
                        data
                    )


def getparentspanfromheader(tracer, request):
    return tracer.extract(
        Format.HTTP_HEADERS,
        request.headers
    )


def newspan(tracer, parentspan, name):
    if parentspan:
        span = tracer.start_span(name, child_of=parentspan)
    else:
        span = tracer.start_span(name)
    return span


def inject_in_header(tracer, span, headers):
    tracer.inject(
        span_context=span.context,
        format=Format.HTTP_HEADERS,
        carrier=headers)
    return headers


def gett():
    return str(time.time())

