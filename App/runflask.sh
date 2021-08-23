#! /bin/bash
export FLASK_APP=connect.py
flask_loc=$(which flask)

$flask_loc run --host=0.0.0.0
