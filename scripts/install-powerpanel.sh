#!/bin/bash
# based on Ubuntu Server 18.04.1

# make sure this is run via sudo
if [ -z "$SUDO_USER" ]; then
    echo You must run this script using sudo.
    exit 1
fi

# download and install
wget https://dl4jz3rbrsfum.cloudfront.net/software/powerpanel_132_amd64.deb
dpkg -i powerpanel_132_amd64.deb

# configure
PP_FILE="/etc/pwrstatd.conf"
sed -i "s/^\(powerfail-shutdown\).*$/\1 = no/" $PP_FILE
sed -i "s/^\(lowbatt-threshold\).*$/\1 = 15/" $PP_FILE
sed -i "s/^\(shutdown-sustain\).*$/\1 = 300/" $PP_FILE
sed -i "s/^\(allowed-device-nodes\).*$/\1 = \/dev\/usb\/hiddev0/" $PP_FILE

# restart
systemctl restart pwrstatd
