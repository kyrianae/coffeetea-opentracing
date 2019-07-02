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
## grafana
I will not present this amazing dashboarding tool
on url http://127.0.0.1:3000
in directory dashboard tyou will find some dashboard that use the influx db database for custom metrics
https://drive.google.com/file/d/1iXSKeyLVpKKBRTVZ8kx_lJxunOF2o9n6/view

## In Kubernetes
TODO