#!/bin/bash

# Infinite loop
while true; do
  gzip *.json
    for csv_file in *.csv; do
      [ -e "$csv_file" ] || continue

      gzip "$csv_file"
      # You may define your own sync operation here if you chose to upload the results to a remove location
      # EXAMPLE :
      # rsync -azvrh --progress YOUR_OUTPUT_DIR YOUR_UPLOAD_DESTINATION
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
