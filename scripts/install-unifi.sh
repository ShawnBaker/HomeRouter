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
INT_NET="$NETWORK/24"

# download
echo 'deb http://www.ubnt.com/downloads/unifi/debian stable ubiquiti' | tee -a /etc/apt/sources.list.d/100-ubnt.list
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-3.4.list
apt-get update
wget -O /etc/apt/trusted.gpg.d/unifi-repo.gpg https://dl.ubnt.com/unifi/unifi-repo.gpg
apt-get update

# install
apt-get install -y unifi

# configure UFW
ufw allow from $INT_NET to any port 3478 proto udp
ufw allow from $INT_NET to any port 8080,8443,8843,8880 proto tcp
