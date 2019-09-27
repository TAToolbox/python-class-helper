#!/bin/bash
deactivate
python -m virtualenv ./venv
pip install -r requirements.txt
chmod 777 run