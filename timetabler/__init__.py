from flask import Flask
app = Flask(__name__)

from functions import update_all

if app.config['UPDATE_ON_INIT']:
  update_all()

import timetabler.views
