#!/bin/bash
# based on Ubuntu Server 18.04.1

# make sure this is run via sudo
if [ -z "$SUDO_USER" ]; then
    echo You must run this script using sudo.
    exit 1
fi

FSTAB_FILE="/etc/fstab"

if grep -qe "/mnt/data" $FSTAB_FILE; then
	echo "It's already been done."
	exit 1
fi

modprobe dm-mod
vgchange -ay ubuntu-vg
mkdir /mnt/data
#chmod 0777 /mnt/data
mount /dev/ubuntu-vg/root /mnt/data
tee -a $FSTAB_FILE > /dev/null << FSTAB_END
/dev/mapper/ubuntu--vg-root /mnt/data ext4 defaults 0 0
FSTAB_END

#UUID=1f2dce12-f3f4-4c1a-8fdf-c99d7c7ffc8f /mnt/data ext4 defaults 0 0
