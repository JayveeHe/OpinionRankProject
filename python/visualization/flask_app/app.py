__author__ = 'jayvee'

from flask import Flask, render_template
# from flask_sockets import Sockets

app = Flask(__name__)


@app.route('/', methods=['GET'])
def show_sigma():
    return render_template('show.html')

# sockets = Sockets(app)

# @sockets.route('/echo')
# def echo_socket(ws):
#     while not ws.closed:
#         message = ws.receive()
#         ws.send(message)

if __name__ == '__main__':
    app.run('0.0.0.0', port=2333, debug=True)
