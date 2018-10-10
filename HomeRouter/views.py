from flask import session, render_template, redirect, url_for, request, g
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta
from HomeRouter import app, login_manager
from .forms import LoginForm, UserForm, SystemForm, WanForm, LanForm
from .models import User, Settings, Sys, Wan, Lan
from .utils import get_interface_choices, update_interfaces, update_lan, update_wan
from .netplan import *
from .dnsmasq import *
import pam, ipaddress, socket, netifaces

#==============================================================================
# load_user
#==============================================================================
@login_manager.user_loader
def load_user(username):
	return User(username)

#==============================================================================
# before_request
#==============================================================================
@app.before_request
def before_request():
	session.permanent = True
	app.permanent_session_lifetime = timedelta(minutes=15)
	session.modified = True
	g.user = current_user
	if g.user.is_authenticated:
		g.user.last_seen = datetime.utcnow()
	g.settings = Settings()

#==============================================================================
# index
#==============================================================================
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@app.route('/status', methods=['GET', 'POST'])
@login_required
def index(page=1):
	netplan = load_netplan()
	dnsmasq = load_dnsmasq()
	sys = Sys(dnsmasq)
	wan = Wan(netplan, g.settings.wan_interface)
	lan = Lan(netplan, dnsmasq, g.settings.lan_interface)
	leases = load_leases()
	return render_template('status.html', sys = sys, wan = wan, lan = lan, leases = leases)
    
#==============================================================================
# login
#==============================================================================
@app.route('/login', methods=['GET', 'POST'])
def login():
	if g.user is not None and g.user.is_authenticated:
		return redirect(url_for('index'))
	form = LoginForm(request.form)
	session.pop('login_error', None)
	if request.method == 'POST' and form.validate():
		p = pam.pam()
		if p.authenticate(form.username.data, form.password.data):
			user = User(form.username.data)
			login_user(user, remember=False)
			return redirect(url_for('index'))
		session['login_error'] = p.reason
	return render_template('login.html', form = form)
	
#==============================================================================
# logout
#==============================================================================
@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))

#==============================================================================
# user
#==============================================================================
@app.route('/user', methods=['GET', 'POST'])
@login_required
def user():
	form = UserForm(request.form)
	g.user.load()
	session.pop('user_error', None)
	if request.method == 'POST' and form.validate():
		err = g.user.save(form.full_name.data, form.path.data, form.shell.data, form.ssh_keys.data)
		if err:
			session['user_error'] = err
			return render_template('user.html', form = form)
		return redirect(url_for('index'))
	form.full_name.data = g.user.fullname
	form.path.data = g.user.path
	form.shell.data = g.user.shell
	form.ssh_keys.data = g.user.keys
	return render_template('user.html', form = form)
	
#==============================================================================
# system
#==============================================================================
@app.route('/system', methods=['GET', 'POST'])
@login_required
def system():
	form = SystemForm(request.form)
	dnsmasq = load_dnsmasq()
	form.host_name.data = socket.gethostname()
	form.domain_name.data = dnsmasq.get('domain', '')
	choices = get_interface_choices()
	form.lan.choices = choices
	form.wan.choices = choices
	session.pop('system_error', None)
	if request.method == 'POST':
		if form.validate():
			lan_interface = form.lan.data
			if lan_interface == 'none':
				lan_interface = ''
			wan_interface = form.wan.data
			if wan_interface == 'none':
				wan_interface = ''
			if lan_interface == g.settings.lan_interface and wan_interface == g.settings.wan_interface:
				return render_template('system.html', form = form)
			template = ''
			if wan_interface and wan_interface != g.settings.wan_interface:
				template = 'wan'
			if lan_interface and lan_interface != g.settings.lan_interface:
				template = 'lan'
			update_interfaces(lan_interface, form.lan_keep_settings.data, wan_interface, form.wan_keep_settings.data)
			if template:
				return redirect(url_for(template))
			else:
				return render_template('system.html', form = form)
		else:
			session['system_error'] = 'Invalid system ???'
			return render_template('system.html', form = form)
	form.lan.data = g.settings.lan_interface if g.settings.lan_interface else 'none'
	form.wan.data = g.settings.wan_interface if g.settings.wan_interface else 'none'
	return render_template('system.html', form = form)

#==============================================================================
# lan
#==============================================================================
@app.route('/lan', methods=['GET', 'POST'])
@login_required
def lan():
	form = LanForm(request.form)
	session.pop('lan_error', None)
	if request.method == 'POST':
		update_lan(form)
	elif g.settings.lan_interface:
		netplan = load_netplan()
		dnsmasq = load_dnsmasq()
		lan = Lan(netplan, dnsmasq, g.settings.lan_interface)
		form.connection.data = lan.type
		form.address.data = lan.address
		form.netmask.data = lan.netmask
		form.dhcp.data = lan.is_dhcp_server
		form.from_address.data = lan.from_address
		form.to_address.data = lan.from_address
		form.to_address.data = lan.to_address
		form.lease_time.data = lan.lease_time
	return render_template('lan.html', form = form)

#==============================================================================
# wan
#==============================================================================
@app.route('/wan', methods=['GET', 'POST'])
@login_required
def wan():
	form = WanForm(request.form)
	session.pop('wan_error', None)
	if request.method == 'POST':
		update_wan(form)
	elif g.settings.wan_interface:
		netplan = load_netplan()
		wan = Wan(netplan, g.settings.wan_interface)
		form.connection.data = wan.type
		form.address.data = wan.address
		form.netmask.data = wan.netmask
		form.dns1.data = wan.dns1
		form.dns2.data = wan.dns2
		form.mac.data = wan.mac
	return render_template('wan.html', form = form)
	
#==============================================================================
# not_found_error
#==============================================================================
@app.errorhandler(404)
def not_found_error(error):
	return render_template('404.html'), 404

#==============================================================================
# internal_error
#==============================================================================
@app.errorhandler(500)
def internal_error(error):
	return render_template('500.html'), 500
