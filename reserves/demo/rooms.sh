#!/bin/bash

echo '"id","hotel/id","beds","name","price"'
for i in {1..4}; do
  for j in {100..199}; do
    echo '"reserves.room'$i'_'$j'","reserves.hotel'$i'","2","'$j'","100"'
    done
    done
