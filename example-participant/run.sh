#!/bin/bash

python -m src.server &
sleep 2 # Sleep for 2s to give the server enough time to start

for i in `seq 0 1`; do
    echo "Starting client $i"
    PORT="$((3000 + $i))" python app.py &
done

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait