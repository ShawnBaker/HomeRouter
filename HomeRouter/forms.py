from wtforms import Form, StringField, PasswordField, TextAreaField, SelectField, BooleanField, IntegerField, validators

#==============================================================================
# LoginForm
#==============================================================================
class LoginForm(Form):
	username = StringField('Username')
	password = PasswordField('Password')

#==============================================================================
# UserForm
#==============================================================================
class UserForm(Form):
	full_name = StringField('Full Name')
	path = StringField('Home Directory')
	shell = StringField('Shell')
	ssh_keys = TextAreaField('SSH Keys', render_kw = {'rows': 5})

#==============================================================================
# SystemForm
#==============================================================================
class SystemForm(Form):
	host_name = StringField('Host')
	domain_name = StringField('Domain')
	lan = SelectField('LAN')
	lan_keep_settings = BooleanField('Keep LAN settings', default = True)
	wan = SelectField('WAN')
	wan_keep_settings = BooleanField('Keep WAN settings', default = True)

#==============================================================================
# WanForm
#==============================================================================
class WanForm(Form):
	connection = SelectField('Type', choices = [('static', 'Static IP'), ('dhcp', 'DHCP Client')])#, ('pppoe', 'PPPoE'), ('pptp', 'PPTP'), ('l2tp', 'L2TP')])
	unicast = BooleanField('Unicast')
	address = StringField('IP Address')
	netmask = IntegerField('Subnet Mask')
	gateway = StringField('Gateway')
	dns1 = StringField('Primary DNS')
	dns2 = StringField('Secondary DNS')
	mtu = IntegerField('MTU')
	mac = StringField('MAC')

#==============================================================================
# LanForm
#==============================================================================
class LanForm(Form):
	connection = SelectField('Type', choices = [('static', 'Static IP'), ('dhcp', 'DHCP Client')])
	address = StringField('IP Address')
	netmask = StringField('Subnet Mask')
	dhcp = BooleanField('Enable DHCP Server')
	from_address = StringField('From IP Address')
	to_address = StringField('To IP Address')
	lease_time = IntegerField('Lease Time')
