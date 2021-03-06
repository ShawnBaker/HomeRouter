#!/bin/bash
# based on Ubuntu Server 18.04.1

# make sure this is run via sudo
if [ -z "$SUDO_USER" ]; then
    echo You must run this script using sudo.
    exit 1
fi

USAGE="Usage: $0 lan-interface server-address domain-name wan-interface [wan-mac]
   ex: sudo $0 enp0s3 192.168.0.1 my.world enp0s8
   ex: sudo $0 enp0s3 192.168.0.10 my.world enp0s8 11:22:33:44:55:66"

# get the parameters
if [ "$#" -ne 4 ] && [ "$#" -ne 5 ]; then
	echo -e "$USAGE"
	exit 1
fi
LAN_IF="$1"
SERVER_IP="$2"
LAN_ROOT_IP="${SERVER_IP%.*}"
DOMAIN_NAME="$3"
WAN_IF="$4"
if [ "$#" -eq 5 ]; then
	WAN_MAC="$5"
	WAN_REAL_MAC="$(cat /sys/class/net/$WAN_IF/address)"
else
	WAN_MAC=""
fi

# install some python tools
apt-get install -y python3-pip python3-venv

# create the website virtual environment
sudo -u $SUDO_USER ./install-venv.sh

# update the website settings
SCRIPT_PATH="$(dirname $(realpath $0))"
SETTINGS_FILE="$SCRIPT_PATH/../data/settings.xml"
sed -i "s/^\(.*<lan-interface>\).*\(<\/lan-interface>.*\)$/\1$LAN_IF\2/" $SETTINGS_FILE
sed -i "s/^\(.*<wan-interface>\).*\(<\/wan-interface>.*\)$/\1$WAN_IF\2/" $SETTINGS_FILE

# create the website service file
WEBSITE_SERVICE_FILE="/etc/systemd/system/home-router-website.service"
tee $WEBSITE_SERVICE_FILE > /dev/null << WEBSITE_SERVICE_END
[Unit]
Description=Home Router - Website
After=network.target

[Service]
PIDFile=/home/$SUDO_USER/HomeRouter.pid
User=$SUDO_USER
Group=$SUDO_USER
RuntimeDirectory=gunicorn
WorkingDirectory=/home/$SUDO_USER/HomeRouter
ExecStart=/home/$SUDO_USER/HomeRouter/venv/bin/gunicorn --pid /home/$SUDO_USER/HomeRouter.pid --bind $SERVER_IP:8801 HomeRouter:app
PrivateTmp=true

[Install]
WantedBy=multi-user.target
WEBSITE_SERVICE_END

# enable the website service
systemctl enable home-router-website.service

# create the startup service file
STARTUP_SERVICE_FILE="/etc/systemd/system/home-router-startup.service"
tee $STARTUP_SERVICE_FILE > /dev/null << STARTUP_SERVICE_END
[Unit]
Description=Home Router - System Initialization
After=network.target

[Service]
WorkingDirectory=$SCRIPT_PATH
Type=forking
ExecStart=/bin/bash system-startup.sh
KillMode=process

[Install]
WantedBy=multi-user.target
STARTUP_SERVICE_END

# enable the startup service
systemctl enable home-router-startup.service

# remove cloud-init
CLOUD_CFG_FILE="/etc/cloud/cloud.cfg.d/90_dpkg.cfg"
tee $CLOUD_CFG_FILE > /dev/null << CLOUD_CFG_END
datasource_list: [ None ]
CLOUD_CFG_END
apt-get purge -y cloud-init
rm -rf /etc/cloud/
rm -rf /var/lib/cloud/
rm -f /etc/netplan/50-cloud-init.yaml

# install Fail2Ban and Dnsmasq
apt-get install -y fail2ban dnsmasq

# disable the systemd DNS stub
RESOLVED_FILE="/etc/systemd/resolved.conf"
sed -i "s/^.*\(DNSStubListener\)=.*$/\1=no/" $RESOLVED_FILE
systemctl restart systemd-networkd.service
systemctl restart systemd-resolved.service

# configure netplan
NETPLAN_FILE="/etc/netplan/50-home-router.yaml"
tee $NETPLAN_FILE > /dev/null << NETPLAN_END
# generated by Home Router
network:
   version: 2
   renderer: networkd
   ethernets:
      $LAN_IF:
         addresses: [$SERVER_IP/24]
         dhcp4: false
         optional : false
         nameservers:
            addresses: [8.8.8.8,8.8.4.4]
            search: [$DOMAIN_NAME]
      $WAN_IF:
         addresses: []
         dhcp4: true
NETPLAN_END
if [ -n "$WAN_MAC" ]; then
tee -a $NETPLAN_FILE > /dev/null << MAC_END
         match:
            macaddress: $WAN_REAL_MAC
         macaddress: $WAN_MAC
MAC_END
fi

# restart netplan
netplan generate
netplan apply

# configure Dnsmasq
DNSMASQ_FILE="/etc/dnsmasq.conf"
tee $DNSMASQ_FILE > /dev/null << DNSMASQ_END
# generated by Home Router
domain-needed
bogus-priv
no-resolv
no-poll
strict-order
expand-hosts
bind-interfaces
read-ethers
domain=$DOMAIN_NAME
local=/$DOMAIN_NAME/
listen-address=127.0.0.1
listen-address=127.0.0.53
listen-address=$SERVER_IP
interface=$LAN_IF
server=8.8.8.8
server=8.8.4.4
dhcp-range=$LAN_ROOT_IP.100,$LAN_ROOT_IP.254,24h
dhcp-option=option:router,$SERVER_IP
dhcp-option=option:netmask,255.255.255.0
DNSMASQ_END

# restart Dnsmasq
systemctl restart dnsmasq

# configure UFW
./config-ufw.sh $LAN_IF $SERVER_IP $WAN_IF

# reboot
reboot