#!/bin/bash
# based on Ubuntu Server 18.04.1

# make sure this is run via sudo
if [ -z "$SUDO_USER" ]; then
    echo You must run this script using sudo.
    exit 1
fi

USAGE="Usage: $0 network
   ex: sudo $0 192.168.0.0"

# get the parameters
if [ "$#" -ne 1 ]; then
	echo -e "$USAGE"
    exit
fi
NETWORK="$1"

# call the appropriate configuration scripts
./hr-drives.sh
./hr-samba.sh $NETWORK
./hr-unifi.sh $NETWORK
./hr-powerpanel.sh
