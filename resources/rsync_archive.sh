#!/bin/bash

# Infinite loop
while true; do
    for csv_file in *.csv; do
      [ -e "$csv_file" ] || continue

      gzip "$csv_file"
      $ELASTIC_SYNC
    done
    echo "restarting counter...."
    echo "time 10 seconds...."
    sleep 10
    echo "time 20 seconds...."
    sleep 10
    echo "time 30 seconds...."
    sleep 10
done
