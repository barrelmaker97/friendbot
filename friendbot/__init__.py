from flask import Flask
from os import environ, path

app = Flask(__name__)
app.config['EXPORT_DIR'] = path.expanduser(environ['EXPORT_DIR'])
print("Export can be found at {}".format(app.config['EXPORT_DIR']))

from friendbot import routes
