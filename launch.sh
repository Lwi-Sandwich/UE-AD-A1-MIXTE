#!/bin/bash

# Function to clean up and kill all background jobs on Ctrl+C
cleanup() {
  kill $(jobs -p)
  exit 1
}

# Set up the trap to call cleanup on Ctrl+C
trap cleanup SIGINT

cd "$(dirname "$0")/user";
python3 ./user.py &
cd "../movie";
python3 ./movie.py &
cd "../showtime";
python3 ./showtime.py &
cd "../booking";
python3 ./booking.py &
wait