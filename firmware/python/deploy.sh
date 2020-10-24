#!/bin/bash
# firmware/deploy.sh:
# 
set -eu
set -o pipefail

err() {
    echo "[$(date +'%Y-%m-%dT%H:%M:%S%z')]: $@" >&2
}

for dest in $@
do
    cp -r code.py therefore "$dest" &
done

wait
