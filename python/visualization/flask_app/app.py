__author__ = 'jayvee'

from flask import Flask, render_template

app = Flask(__name__)


@app.route('/', methods=['GET'])
def show_sigma():
    return render_template('show.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=2333, debug=True)
