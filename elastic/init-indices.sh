#!/bin/bash

SCHEMAS_PATH=/schemas/*.json
ELASTIC_HOST="http://127.0.0.1:9200"

for filepath in $SCHEMAS_PATH; do
  filename=$(basename -- $filepath)
  index="${filename%%.*}"
  echo "### ELASTIC: init index $index"
  curl -s -XPUT -H 'Content-Type: application/json' $ELASTIC_HOST/$index -d @$filepath
done