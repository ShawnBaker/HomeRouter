#!/bin/bash
# based on Ubuntu Server 18.04.1

# make sure this is not run as root
if [ $EUID -eq 0 ]; then
    echo You must NOT run this script as root.
    exit 1
fi

SCRIPT_PATH="$(dirname $(realpath $0))"
cd $SCRIPT_PATH
cd ../..
python3 -m venv HomeRouter/venv
cd HomeRouter
. venv/bin/activate

pip install wheel
pip install flask
pip install flask-login
pip install flask-wtf
pip install flask-sslify
pip install netifaces
pip install pyyaml
pip install python-pam
pip install gunicorn

deactivate
