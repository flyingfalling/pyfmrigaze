#!/bin/bash

venv=$1
python3 -m venv $venv
source $venv/bin/activate && \
    pip install pandas dcm2bids dcm2niix numpy

echo "Created VENV in [$venv]"
