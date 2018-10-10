from HomeRouter import app
from flask import g
from ipaddress import ip_network
from .netplan import *
import os, subprocess, sqlite3, netifaces

#==============================================================================
# get_interface_choices
#==============================================================================
def get_interface_choices():
	list = [('none', 'None')]
	for interface in netifaces.interfaces():
		if interface != 'lo':
			addrs = netifaces.ifaddresses(interface)
			links = addrs[netifaces.AF_LINK]
			if links:
				device = (interface, interface + ' (' + links[0]['addr'] + ')')
				list.append(device)	
	return list

#==============================================================================
# update_interfaces
#==============================================================================
def update_interfaces(lan_interface, lan_keep_settings, wan_interface, wan_keep_settings):

	# don't do anything if nothing has changed
	lan_changed = lan_interface != g.settings.lan_interface
	wan_changed = wan_interface != g.settings.wan_interface
	if not lan_changed and not wan_changed:
		return

	# get the netplan file
	netplan = load_netplan()

	# update the LAN interface
	if lan_changed:
		old_lan = get_interface(netplan, g.settings.lan_interface)
		print(old_lan)
		if old_lan:
			bring_interface_down(g.settings.lan_interface)
		if lan_interface:
			new_lan = get_interface(netplan, lan_interface)
			if lan_keep_settings and old_lan:
				if new_lan and lan_interface != wan_interface:
					remove_interface(netplan, lan_interface)
				old_lan.interface = lan_interface
			else:
				if not new_lan:
					new_lan = create_lan_interface(netplan, lan_interface)
			bring_interface_up(lan_interface)

	# update the WAN interface
	if wan_changed:
		old_wan = get_interface(netplan, g.settings.wan_interface)
		if old_wan:
			bring_interface_down(g.settings.wan_interface)
		if wan_interface:
			new_wan = get_interface(netplan, wan_interface)
			if lan_keep_settings and old_wan:
				if new_wan and wan_interface != lan_interface:
					remove_interface(netplan, wan_interface)
				old_wan.interface = wan_interface
			else:
				if not new_wan:
					new_wan = create_wan_interface(netplan, wan_interface)
			bring_interface_up(wan_interface)

	# update the netplan file
	save_netplan(netplan)

	# update the settings
	g.settings.lan_interface = lan_interface
	g.settings.wan_interface = wan_interface
	g.settings.save()

#==============================================================================
# update_lan
#==============================================================================
def update_lan(form):

	# get the netplan file
	netplan = load_netplan()

	# get the iface stanza
	stanza = get_interface(netplan, g.settings.lan_interface)
	# iface = [g.settings.lan_interface, 'inet', form.connection.data]
	# if stanza:
	# 	stanza.lines['iface'] = iface
	# else:
	# 	stanza = hrutils.InterfaceStanza()
	# 	stanza.add_line(['iface'] + iface)
	#
	# # set the stanza values
	# if form.connection.data == 'static':
	# 	stanza.set_value('address', form.address.data)
	# 	stanza.set_value('netmask', form.netmask.data)
	# 	num_bits = sum([bin(int(x)).count("1") for x in form.netmask.data.split(".")])
	# 	network = ip_network(form.address.data + '/' + str(num_bits), strict = False)
	# 	stanza.set_value('network', str(network.network_address))
	# 	stanza.set_value('broadcast', str(network.broadcast_address))
	# else:
	# 	stanza.remove_value('address')
	# 	stanza.remove_value('netmask')
	# 	stanza.remove_value('network')
	# 	stanza.remove_value('broadcast')
	#
	# # update the interfaces file
	# ifile.save('Home Router')

#==============================================================================
# update_wan
#==============================================================================
def update_wan(form):

	# get the netplan file
	netplan = load_netplan()

	# get the iface stanza
	stanza = get_interface(netplan, g.settings.wan_interface)
	# iface = [g.settings.wan_interface, 'inet', form.connection.data]
	# if stanza:
	# 	stanza.lines['iface'] = iface
	# else:
	# 	stanza = hrutils.InterfaceStanza()
	# 	stanza.add_line(['iface'] + iface)
	#
	# # set the stanza values
	# if form.connection.data == 'static':
	# 	stanza.set_value('address', form.address.data)
	# 	stanza.set_value('netmask', form.netmask.data)
	# 	stanza.set_value('gateway', form.netmask.data)
	# 	num_bits = sum([bin(int(x)).count("1") for x in form.netmask.data.split(".")])
	# 	network = ip_network(form.address.data + '/' + str(num_bits), strict = False)
	# 	stanza.set_value('network', str(network.network_address))
	# 	stanza.set_value('broadcast', str(network.broadcast_address))
	# else:
	# 	stanza.remove_value('address')
	# 	stanza.remove_value('netmask')
	# 	stanza.remove_value('gateway')
	# 	stanza.remove_value('network')
	# 	stanza.remove_value('broadcast')
	# dns = []
	# if form.dns1.data:
	# 	dns.append(form.dns1.data)
	# if form.dns2.data:
	# 	dns.append(form.dns2.data)
	# stanza.set_value('dns-nameservers', dns)
	# stanza.set_value('mtu', str(form.mtu.data) if form.mtu.data else '')
	# stanza.set_value('hwaddress', ['ether', form.mac.data])
	#
	# # update the interfaces file
	# ifile.save('Home Router')

#==============================================================================
# open_db
#==============================================================================
def open_db():
	if not hasattr(g, 'database'):
		file_name = os.path.join(app.root_path, 'HomeRouter.db')
		exists = os.path.exists(file_name)
		g.database = sqlite3.connect(file_name)
		g.database.row_factory = sqlite3.Row
		if not exists:
			cur = g.database.cursor()
			with app.open_resource('schema.sql', mode='r') as f:
				cur.executescript(f.read())
			cur.execute('INSERT INTO settings(lan_interface, wan_interface) VALUES("", "")')
			g.database.commit()
	return g.database

#==============================================================================
# close_db
#==============================================================================
@app.teardown_appcontext
def close_db(error):
	if hasattr(g, 'database'):
		g.database.close()
		delattr(g, 'database')
