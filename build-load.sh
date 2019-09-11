#!/bin/bash

CONTAINER=naturalis/museumapp_document_load
TAG=$1
FILE=Dockerfile-doc_load

../_build.sh $CONTAINER $TAG $FILE
