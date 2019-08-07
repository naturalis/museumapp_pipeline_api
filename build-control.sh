#!/bin/bash

sudo docker build -t naturalis/museumapp_elastic_control:latest . -f Dockerfile-es_control; sudo docker login; sudo docker image push naturalis/museumapp_elastic_control:latest
