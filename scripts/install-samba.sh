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

# install Samba
apt-get install -y samba

# configure Samba
SAMBA_FILE="/etc/samba/smb.conf"
smbpasswd -a $SUDO_USER
if grep -qe "\[data\]" $SAMBA_FILE; then
	sed -i "s/^\(\sforce user\).*$/\1 = $SUDO_USER/" $SAMBA_FILE
else
tee -a $SAMBA_FILE > /dev/null << SAMBA_END
[data]
   path = /mnt/data/data
   guest ok = yes
   read only = no
   browseable = yes
   public = yes
   writable = yes
   create mask = 0755
   force user = $SUDO_USER
SAMBA_END

# restart Samba
systemctl restart smbd

# configure UFW
ufw allow from $INT_NET to any app samba
#ufw allow from $INT_NET to any port 137,138 proto udp
#ufw allow from $INT_NET to any port 139,445 proto tcp
