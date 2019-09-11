#!/bin/bash

COMMAND=$1

PUBLISH_DIR=$JSON_PUBLISH_PATH
LOAD_DIR=$JSON_LOAD_PATH

SIGNAL_FILE_READY=${PUBLISH_DIR}.ready
SIGNAL_FILE_WORKING=${PUBLISH_DIR}.busy

MINIMUM_NUM_OF_FILES=1000
NUM_OF_FILES=$(ls -1 ${PUBLISH_DIR}*.json 2> /dev/null | wc -l)

echo "$(date +"%Y-%m-%d %H:%M:%S") - loading documents from $PUBLISH_DIR"



if [ "$NUM_OF_FILES" -eq 0 ] && [ "$COMMAND" != "--reload" ]; then
  echo "$(date +"%Y-%m-%d %H:%M:%S") - nothing to load"
  exit
fi

if [ ! -f "$SIGNAL_FILE_READY" ] && [ "$COMMAND" != "--reload" ]; then
  echo "signal file $SIGNAL_FILE_READY missing"
  echo "$(date +"%Y-%m-%d %H:%M:%S") - done"
  exit
fi

if [ "$NUM_OF_FILES" -lt "$MINIMUM_NUM_OF_FILES" ] && [ "$COMMAND" != "--reload" ]; then
  echo "found only $NUM_OF_FILES documents in $PUBLISH_DIR (threshold: $MINIMUM_NUM_OF_FILES)"
  echo "$(date +"%Y-%m-%d %H:%M:%S") - done"
  exit
fi

if [ "$COMMAND" == "--reload" ]; then
  echo "reloading documents"
else
  echo "loading $NUM_OF_FILES documents"
fi

rm $SIGNAL_FILE_READY
touch $SIGNAL_FILE_WORKING 

if [ "$COMMAND" != "--reload" ]; then
  rm ${LOAD_DIR}*.json
  mv ${PUBLISH_DIR}*.json $LOAD_DIR
fi

export DEBUGGING=1 

export ES_CONTROL_COMMAND=set_documents_status 
export ES_CONTROL_ARGUMENT=busy
python elastic_control.py


export ES_CONTROL_COMMAND=delete_documents 
python elastic_control.py


export ES_CONTROL_COMMAND=load_documents 
export ES_CONTROL_ARGUMENT=$LOAD_DIR
python elastic_control.py


export ES_CONTROL_COMMAND=set_documents_status 
export ES_CONTROL_ARGUMENT=ready
python elastic_control.py

rm $SIGNAL_FILE_WORKING

echo "$(date +"%Y-%m-%d %H:%M:%S") - done"
