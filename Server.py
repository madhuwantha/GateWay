from flask import Flask, request
import ast

from Env import Env
from FLModel import FLModel
from SecurityManagerSDK import SecurityManagerSDK

app = Flask(__name__)
env = Env()


def run():
    app.run(host=str(env.get(key="host")), port=env.get(key="port"), debug=False, use_reloader=True)


@app.route("/", methods=['GET'])
def test():
    return {'status': True, 'message': "Gateway " + env.get(key="gatewayId") + " is running"}


@app.route('/modeltrain')
def modelTrain():
    try:
        fl_model = FLModel(epochs=env.get(key="epochs"))
        fl_model.train()
        return {'status': True, 'message': "Model trained successfully!"}
    except Exception as e:
        return {'status': False, 'message': "Model trained Failed " + e.__str__()}


@app.route('/update-model', methods=['POST'])
def getAggModel():
    if request.method == 'POST':
        file = request.files['model'].read()
        fname = request.files['json'].read()

        fname = ast.literal_eval(fname.decode("utf-8"))
        fname = fname['fname']
        print(fname)

        wfile = open("UpdatedModel/" + fname, 'wb')
        wfile.write(file)

        return {'status': True, 'message': "Model received!"}
    else:
        return {'status': False, 'message': "No file received!"}


@app.route('/send-model')
def sendModel():
    smSdk = SecurityManagerSDK()
    try:
        smSdk.senModel()
        return {'status': True, 'message': "Model send!"}
    except:
        return {'status': False, 'message': "Model sent failed"}


if __name__ == '__main__':
    app.run(host=str(env.get(key="host")), port=env.get(key="port"), debug=False, use_reloader=True)
