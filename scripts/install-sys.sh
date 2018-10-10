#!/bin/bash
# based on Ubuntu Server 18.04.1

# make sure this is run via sudo
if [ -z "$SUDO_USER" ]; then
    echo You must run this script using sudo.
    exit 1
fi

# make sure SSH key login is working
RED='\033[0;31m'
NC='\033[0m'
echo -e "${RED}This will disable SSH root and password logins."
echo -e "Please test your key login first.$NC"
read -r -p "Enter YES to continue: "
if [ "$REPLY" != "YES" ]; then
	echo -e "${RED}Script terminated.$NC"
	exit 1
fi

# update the system
add-apt-repository universe
apt-get update
apt-get upgrade -y
apt-get dist-upgrade -y
apt-get autoremove -y
apt-get autoclean -y

# don't require sudo passwords
SUDOERS_FILE="/etc/sudoers"
sed -i "/$SUDO_USER/d" $SUDOERS_FILE
echo "$SUDO_USER ALL=(ALL) NOPASSWD: ALL" | sudo tee -a $SUDOERS_FILE

# configure SSH, no root or password logins
# from remote machine: ssh-copy-id user@server
SSH_FILE="/etc/ssh/sshd_config"
sed -i "/PermitRootLogin/d" $SSH_FILE
sed -i "/PasswordAuthentication/d" $SSH_FILE
sed -i "/AllowUsers/d" $SSH_FILE
tee -a $SSH_FILE > /dev/null << SSH_END
PermitRootLogin no
PasswordAuthentication no
AllowUsers $SUDO_USER
SSH_END
service ssh restart

# put the host name in the hosts file
HOSTS_FILE="/etc/hosts"
sed -i "/127\.0\.1\.1/d" $HOSTS_FILE
tee -a $HOSTS_FILE > /dev/null << HOSTS_END
127.0.1.1	$(hostname)
HOSTS_END

# reboot
reboot