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

# Prerequisite
for execution you need to launch 
docker-compose for directory :
*dbdashboard
*jaeger
of https://github.com/kyrianae/coffeetea-docker-env
I merged different git project and changed 2 or 3 things (mainly networks)
in each directory launch the command 
> docker-compose up
Ii use 2 ways to this opentracing test
# How to Launch it ...
## In an IDE 
I use pycharm community edition
./code is the root of scripts
each script is working and don't need any parameter on command line
just need to launch each script linking env file : local.properties to the execution
## with dicker-compose
### build the image
launch
> ./build-container.sh 0.1
0.1 is preconfigured in the docker-compose for the next step
### launch docker-compose
as for backends with the command
> docker-compose up
# what to look
## opentracing
for the moment there is only jaeger ( I will try to add zipkin in parallel or with a switch)
on url http://127.0.0.1:16686
https://drive.google.com/file/d/1gkVjCMaj-pbeadzqDE_A3ChqdJugNckW/view
## grafana
I will not present this amazing dashboarding tool
on url http://127.0.0.1:3000
in directory dashboard tyou will find some dashboard that use the influx db database for custom metrics
https://drive.google.com/file/d/1iXSKeyLVpKKBRTVZ8kx_lJxunOF2o9n6/view

## In Kubernetes
TODO


## TODO
* docker-compose for services
* kubernetes deployement
* switch metrics push in opentracing (opencensus ? ...)
* add API to change number of client, states frequencies, number of threads .....


issue on water curve with non real time data ??????
> due to Flask on data tried to switch to multi threaded but is not enough
> real use case to check why it s not working :)
