from HomeRouter import app

import os, time

LOCAL_DNSMASQ_FILE = os.path.join(os.path.dirname(app.root_path), 'data', 'dnsmasq.conf')
#DNSMASQ_FILE = LOCAL_DNSMASQ_FILE
DNSMASQ_FILE = '/etc/dnsmasq.conf'
DNSMASQ_LEASES_FILE = '/var/lib/misc/dnsmasq.leases'

#==============================================================================
# load_dnsmasq
#==============================================================================
def load_dnsmasq():
	dnsmasq = {}
	lines = open(DNSMASQ_FILE, 'r').read().splitlines()
	for line in lines:
		key = line
		value = ''
		i = line.find('=')
		if i != -1:
			key = line[:i]
			value = line[i + 1:]
		if key in dnsmasq:
			existing = dnsmasq[key]
			if isinstance(existing, list):
				existing.append(value)
			else:
				dnsmasq[key] = [existing, value]
		else:
			dnsmasq[key] = value
	return dnsmasq

#==============================================================================
# save_dnsmasq
#==============================================================================
def save_dnsmasq(dnsmasq):
	with open(LOCAL_DNSMASQ_FILE, 'w') as f:
		for key, value in dnsmasq.items():
			if isinstance(value, list):
				for v in value:
					f.write(key + '=' + v + '\n')
			else:
				f.write(key + '=' + value + '\n')

#==============================================================================
# load_leases
#==============================================================================
def load_leases():
	leases = []
	lines = open(DNSMASQ_LEASES_FILE, 'r').read().splitlines()
	#lines = [ '1411349054 08:11:96:e9:52:ec 192.168.1.96 W11837894 *', '1411413528 b4:b6:76:0c:c9:4d 192.168.1.46 root-HP-9470m *', '1411263016 00:1b:21:0e:f2:bd 192.168.1.219 root-Dell-DM061 *', '1411357237 00:01:2e:4d:49:bd 192.168.1.31 ata *', '1411263041 00:30:67:d2:25:65 192.168.1.51 root-TA75M *']
	for line in lines:
		parts = line.split(' ')
		lease = {}
		epoch = int(parts[0]) if len(parts) > 0 else 0
		t = time.localtime(epoch)
		lease['time'] = time.strftime("%Y-%m-%d %H:%M:%S", t)
		lease['mac'] = parts[1] if len(parts) > 1 else ''
		lease['address'] = parts[2] if len(parts) > 2 else ''
		lease['name'] = parts[3] if len(parts) > 3 else ''
		lease['other'] = ' '.join(parts[4:]) if len(parts) > 4 else ''
		leases.append(lease)
	return leases
