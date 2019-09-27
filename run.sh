#!/bin/bash


os=$OSTYPE
if [[ "$os" == "linux-gnu" ]]; then
    $(source venv/bin/activate);
elif [[ "$os" == "darwin"* ]]; then
    $(source venv/bin/activate);
elif [[ "$os" == "cygwin" ]]; then
    $(source venv/Scripts/activate);
elif [[ "$os" == "msys" ]]; then
    $(source venv/Scripts/activate);
fi

python classhelper.py
