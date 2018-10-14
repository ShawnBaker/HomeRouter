#!/bin/bash
# based on Ubuntu Server 18.04.1

# make sure this is run via sudo
if [ -z "$SUDO_USER" ]; then
    echo You must run this script using sudo.
    exit 1
fi

USAGE="Usage: $0 lan-interface lan-address wan-interface
   ex: sudo $0 enp0s3 192.168.0.0 enp0s8"

# get the parameters
if [ "$#" -ne 3 ]; then
	echo -e "$USAGE"
    exit
fi
LAN_IF="$1"
LAN_IP="$2"
WAN_IF="$3"
LAN_NET="${LAN_IP%.*}.0/24"

UFW_FILE="/etc/default/ufw"
SYSCTL_FILE="/etc/ufw/sysctl.conf"
BEFORE_RULES_FILE="/etc/ufw/before.rules"

# disable UFW
ufw disable

# set the default rules
ufw --force reset
ufw default deny incoming
ufw default allow outgoing

# set port forwarding
sed -i "s/^.*\(DEFAULT_FORWARD_POLICY\)=\".*\".*$/\1=\"ACCEPT\"/" $UFW_FILE
sed -i "s/^.*\(net\/ipv4\/ip_forward\)=.*$/\1=1/" $SYSCTL_FILE
sed -i "s/^.*\(net\/ipv6\/conf\/default\/forwarding\)=.*$/\1=1/" $SYSCTL_FILE

# route the LAN to the WAN
if grep -qe "-A POSTROUTING" $BEFORE_RULES_FILE; then
	sed -i "s/^\(-A POSTROUTING\).*$/\1 -s $LAN_NET -o $WAN_IF -j MASQUERADE/" $BEFORE_RULES_FILE
else
	ed -s $BEFORE_RULES_FILE << BEFORE_RULES_END
0a
# nat Table rules
*nat
:POSTROUTING ACCEPT [0:0]

# Forward traffic from $LAN_IF through $WAN_IF.
-A POSTROUTING -s $LAN_NET -o $WAN_IF -j MASQUERADE

# don't delete the 'COMMIT' line or these nat table rules won't be processed
COMMIT
.
w
BEFORE_RULES_END
fi

# enable SSH on the internal network
ufw allow from $LAN_NET to any port 22 proto tcp

# enable HTTP and HTTPS on the internal network
#ufw allow from $LAN_NET to any port 80,443 proto tcp

# enable DHCP server on the internal network
ufw allow in on $LAN_IF from any port 68 to any port 67 proto udp

# allow DNS server on the internal network
ufw allow from $LAN_NET to $LAN_IP proto tcp port 53 
ufw allow from $LAN_NET to $LAN_IP proto udp port 53

# allow the website port
ufw allow from $LAN_NET to any port 8801 proto tcp

# enable UFW
ufw -f enable
