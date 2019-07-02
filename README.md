# coffeetea-opentracing
environment
jaeger is coming from grafana devenv
influx/grafana is coming from internet i will try to found again the source
docker-compose for jaeger and grafana.. are in nother project

## elements 
theis test contain differents services that call eah other implenting opentracing
### drinkclient
implements ''customer'' that want to buy coffee or tea with credit card or money
### buy
is the main entry point called to buy a drink
### produce
simulate the production
### data
is the core of data persistence
### bill
will push money

## Change Log
* 190702
> added docker-compose ... and how to
> start documentation

* 190701
> clean code and factorize some methods
> prepare externalization of configuration with variable



## TODO
* docker-compose for services
* kubernetes deployement
* switch metrics push in opentracing (opencensus ? ...)
* add API to change number of client, states frequencies, number of threads .....


issue on water curve with non real time data ??????
> due to Flask on data tried to switch to multi threaded but is not enough
> real use case to check why it s not working :)
