#!/bin/sh
exec uwsgi --master \
  --processes $WORKER_PROCESSES \
  --module $UWSGI_MODULE \
  --http $HOST:$PORT
