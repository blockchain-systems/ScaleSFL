#!/bin/bash

python server.py &
sleep 2 # Sleep for 2s to give the server enough time to start

for i in `seq 0 1`; do
    echo "Starting client $i"
    python client.py &
done

# This will allow you to use CTRL+C to stop all background processes
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM
# Wait for all background processes to complete
wait