from flask import Flask

app = Flask(__name__)

from friendbot import routes
