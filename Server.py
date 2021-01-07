from flask import Flask, request
import ast

from Env import Env


class Server(object):
    app = Flask(__name__)

    def run(self):
        self.app.run(host=Env.get("host"), port=Env.get("host"), debug=False, use_reloader=True)

    @app.route('/update-model', methods=['POST'])
    def getAggModel(self):
        if request.method == 'POST':
            file = request.files['model'].read()
            fname = request.files['json0'].read()

            fname = ast.literal_eval(fname.decode("utf-8"))
            fname = fname['fname']
            print(fname)

            wfile = open("UpdatedModel/" + fname, 'wb')
            wfile.write(file)

            return "Model received!"
        else:
            return "No file received!"
