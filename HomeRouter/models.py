from HomeRouter import app
import os, subprocess, socket, ipaddress, netifaces
import xml.etree.ElementTree as ET
from .utils import open_db
from .netplan import *

SETTINGS_FILE_NAME = os.path.join(os.path.dirname(app.root_path), 'data', 'settings.xml')

#==============================================================================
# User
#==============================================================================
class User():

	def __init__(self, username):
		self.username = username
		self.fullname = ''
		self.path = ''
		self.shell = ''
		self.keys = ''

	def get_id(self):
		return self.username

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def __repr__(self):
		return '<User %r>' % (self.username)
		
	def load(self):
		try:
			p = subprocess.run(['/usr/bin/getent', 'passwd', self.username], stdout=subprocess.PIPE)
			app.logger.info(p)
			ent = p.stdout.decode('utf-8').strip()
		except Exception as e:
			app.logger.info(e)
			ent = 'unknown:x:1:1:Unknown,,,::'
		app.logger.info(ent)
		values = ent.split(':')
		self.fullname = values[4].split(',')[0]
		self.path = values[5]
		self.shell = values[6]
		self.keys = ''
		if self.path:
			file_name = os.path.join(os.path.join(self.path, '.ssh'), 'authorized_keys')
			if os.path.exists(file_name):
				f = open(file_name, 'r')
				self.keys = f.read()
				f.close()

	def save(self, fullname, path, shell, keys):
		if fullname != self.fullname:
			p = subprocess.run(['/usr/bin/sudo', '/usr/bin/chfn', '-f', fullname, self.username], stdout=subprocess.PIPE)
			if p.returncode == 0:
				self.fullname = fullname
			else:
				return 'chfn error: ' + str(p.returncode)
		if path != self.path:
			p = subprocess.run(['/usr/bin/sudo', '/usr/bin/usermod', '-m', '-d', path, self.username], stdout=subprocess.PIPE)
			if p.returncode == 0:
				self.path = path
			else:
				return 'usermod error: ' + str(p.returncode)
		if shell != self.shell:
			p = subprocess.run(['/usr/bin/sudo', '/usr/bin/chsh', '-s', shell, self.username], stdout=subprocess.PIPE)
			if p.returncode == 0:
				self.shell = shell
			else:
				return 'chsh error: ' + str(p.returncode)
		if self.path and keys != self.keys:
			ssh_path = os.path.join(self.path, '.ssh')
			if not os.path.exists(ssh_path):
				os.makedirs(ssh_path)
			file_name = os.path.join(ssh_path, 'authorized_keys')
			f = open(file_name, 'w+')
			f.write(keys)
			f.close()
			self.keys = keys
		return None

#==============================================================================
# Settings
#==============================================================================
class Settings():

	def __init__(self):
		tree = ET.parse(SETTINGS_FILE_NAME)
		lan = tree.find('lan-interface').text
		self.lan_interface = '' if lan is None else str(lan)
		wan = tree.find('wan-interface').text
		self.wan_interface = '' if wan is None else str(wan)
		#print('LAN = ' + self.lan_interface + '  WAN = ' + self.wan_interface)

	def save(self):
		settings = ET.Element("settings")
		ET.SubElement(settings, "lan-interface").text = self.lan_interface
		ET.SubElement(settings, "wan-interface").text = self.wan_interface
		tree = ET.ElementTree(settings)
		tree.write(SETTINGS_FILE_NAME)

#==============================================================================
# Interface
#==============================================================================
class Interface():

	def __init__(self, netplan, name):
		self.name = name
		self.type = 'none'
		self.address = ''
		self.netmask = ''
		self.dns1 = ''
		self.dns2 = ''
		self.interface = get_interface(netplan, name)
		if self.interface:
			dhcp = self.interface.get('dhcp4', True)
			self.type = 'dhcp' if dhcp else 'static'
			if dhcp:
				addrs = netifaces.ifaddresses(name)
				links = addrs[netifaces.AF_INET]
				if links:
					self.address = links[0].get('addr', '')
					self.netmask = links[0].get('netmask', '')
			else:
				addrs = self.interface.get('addresses', [])
				if len(addrs) > 0:
					ip = ipaddress.ip_interface(addrs[0])
					self.address = str(ip.ip)
					self.netmask = str(ip.netmask)
			if 'nameservers' in self.interface:
				addrs = self.interface['nameservers']['addresses']
				if len(addrs) > 0:
					self.dns1 = addrs[0]
				if len(addrs) > 1:
					self.dns2 = addrs[1]

#==============================================================================
# Lan
#==============================================================================
class Lan(Interface):

	def __init__(self, netplan, dnsmasq, name):
		Interface.__init__(self, netplan, name)
		self.is_dhcp_server = False
		self.from_address = ''
		self.to_address = ''
		self.lease_time = 0
		if dnsmasq.get('interface', '') == name:
			self.is_dhcp_server = dnsmasq.get('no-dhcp-interface', '') != name
			range = dnsmasq.get('dhcp-range', None)
			if range:
				parts = range.split(',')
				if len(parts) > 0:
					self.from_address  = parts[0]
				if len(parts) > 1:
					self.to_address = parts[1]
				seconds = 3600
				if len(parts) > 2:
					lease = parts[2]
					if lease == 'infinte':
						seconds = 0
					else:
						last = lease[-1]
						if last == 's':
							seconds = int(lease[:-1])
						elif last == 'm':
							seconds = int(lease[:-1]) * 60
						elif last == 'h':
							seconds = int(lease[:-1]) * 3600
						elif last == 'd':
							seconds = int(lease[:-1]) * 86400
						else:
							seconds = int(lease)
				self.lease_time = seconds

#==============================================================================
# Wan
#==============================================================================
class Wan(Interface):

	def __init__(self, netplan,  name):
		Interface.__init__(self, netplan, name)
		self.mac = self.interface.get('macaddress', '')
		self.gateway = ''
		gateways = netifaces.gateways().get(netifaces.AF_INET, None)
		if gateways:
			for gateway in gateways:
				if gateway[1] == name:
					self.gateway = gateway[0]

#==============================================================================
# Sys
#==============================================================================
class Sys():

	def __init__(self, dnsmasq):
		self.host_name = socket.gethostname()
		self.domain_name = dnsmasq.get('domain', '')
