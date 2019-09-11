#!/bin/bash

CONTAINER=naturalis/museumapp_elastic_control
TAG=$1
FILE=Dockerfile-es_control

../_build.sh $CONTAINER $TAG $FILE
