from flask import Flask, request
import ast

from Env import Env
from FLModel import FLModel

app = Flask(__name__)
env = Env()


def run():
    app.run(host=str(env.get(key="host")), port=env.get(key="port"), debug=False, use_reloader=True)


@app.route("/", methods=['GET'])
def test():
    return "Gateway...."


@app.route('/modeltrain')
def model_train():
    fl_model = FLModel(epochs=env.get(key="epochs"))
    fl_model.train()
    return "Model trained successfully!"


@app.route('/update-_model', methods=['POST'])
def getAggModel():
    if request.method == 'POST':
        file = request.files['_model'].read()
        fname = request.files['json0'].read()

        fname = ast.literal_eval(fname.decode("utf-8"))
        fname = fname['fname']
        print(fname)

        wfile = open("UpdatedModel/" + fname, 'wb')
        wfile.write(file)

        return "Model received!"
    else:
        return "No file received!"
