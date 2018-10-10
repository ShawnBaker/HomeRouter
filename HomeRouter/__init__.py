import os
from flask import Flask
from flask_login import LoginManager
#from flask_sslify import SSLify

app = Flask(__name__)
app.secret_key = 'TK#B?HQJYqth9:m@4Z8!'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
#sslify = SSLify(app, age=3650)

if not app.debug:
	import logging
	from logging.handlers import RotatingFileHandler
	file_handler = RotatingFileHandler('logs/HomeRouter.log', 1024 * 1024, 5)
	file_handler.setLevel(logging.INFO)
	file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	app.logger.addHandler(file_handler)
	app.logger.setLevel(logging.INFO)
	app.logger.info('===================================')

from HomeRouter import views, models
