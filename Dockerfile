FROM python:3.6.8-alpine

RUN pip3 install flask &&\
    pip3 install flask-cors &&\
    pip3 install kafka-python  &&\
    pip3 install jaeger-client &&\
    pip3 install urllib3 &&\
    pip3 install requests &&\
    pip3 install influxdb 

COPY code code
