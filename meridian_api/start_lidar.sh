#!/bin/bash


counter=1
output_file="$1/output.txt"

while true; do
    echo "This is line $counter" >> "$output_file"
    sleep 3
    ((counter++))
done


