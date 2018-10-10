from HomeRouter import app

import os, subprocess, yaml

LOCAL_NETPLAN_FILE = os.path.join(os.path.dirname(app.root_path), 'data', '50-home-router.yaml')
#NETPLAN_FILE = LOCAL_NETPLAN_FILE
NETPLAN_FILE = '/etc/netplan/50-home-router.yaml'

#==============================================================================
# load_netplan
#==============================================================================
def load_netplan():
	with open(NETPLAN_FILE, 'r') as f:
		return yaml.safe_load(f)
	return None

#==============================================================================
# save_netplan
#==============================================================================
def save_netplan(netplan):
	with open(LOCAL_NETPLAN_FILE, 'w') as f:
		yaml.dump(netplan, f)

#==============================================================================
# get_interface
#==============================================================================
def get_interface(netplan, interface):
    ethernets = netplan['network']['ethernets']
    for key, value in ethernets.items():
        if key == interface:
            return value
    return None

#==============================================================================
# remove_interface
#==============================================================================
def remove_interface(netplan, interface):
	existing = get_interface(netplan, interface)
	if existing:
		del netplan['network']['ethernets'][interface]

#==============================================================================
# bring_interface_up
#==============================================================================
def bring_interface_up(interface):
	#subprocess.run(['/usr/bin/sudo', '/bin/ip', 'link set ' + interface + ' up'], stdout=subprocess.PIPE)
	pass

#==============================================================================
# bring_interface_down
#==============================================================================
def bring_interface_down(interface):
	#subprocess.run(['/usr/bin/sudo', '/bin/ip', 'link set ' + interface + ' down'], stdout=subprocess.PIPE)
	pass

#==============================================================================
# create_lan_interface
#==============================================================================
def create_lan_interface(netplan, interface):
	dict = {}
	dict['addresses'] = ['192.168.0.10/24']
	dict['dhcp4'] = False
	dict['dhcp6'] = False
	dict['nameservers'] = {'addresses': ['8.8.8.8', '8.8.4.4']}
#	lan = {interface: dict}
	netplan['network']['ethernets'][interface] = dict
	print(dict)
	return dict

#==============================================================================
# create_wan_interface
#==============================================================================
def create_wan_interface(netplan, interface):
	dict = {}
	dict['addresses'] = []
	dict['dhcp4'] = True
	dict['dhcp6'] = True
#	wan = {interface: dict}
	netplan['network']['ethernets'][interface] = dict
	print(dict)
	return dict
