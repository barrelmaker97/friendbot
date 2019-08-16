from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/', methods = ['GET', 'POST'])
def user():
    if request.method == 'GET':
        return "Hello, world!"
        data = request.form # a multidict containing POST data

if __name__ == '__main__':
    app.run()
