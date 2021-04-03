import requests, json

from Env import Env


class SecurityManagerSDK(object):
    env = Env()

    def sendStatus(self):
        print("Sending status...............")
        data = {'client_id': self.env.get(key="port"), 'client_host': self.env.get(key="hostFI")}
        req = requests.post(url=self.env.get(key="serverUrl") + self.env.get(key="getClientStatusUrl"), json=data)

        if req.status_code == 200:
            result = {'status': True, 'message': " status sent"}
        else:
            result = {'status': False, 'message': " status sent Failed!"}
        return result

    def senModel(self):
        print("Sending model...............")
        file = open("LocalModel/mod.npy", 'rb')
        data = {'fname': 'model.npy', 'id': self.env.get(key="host") + ':' + str(self.env.get(key="port"))}
        files = {
            'json': ('json_data', json.dumps(data), 'application/json'),
            'model': ('model.npy', file, 'application/octet-stream')
        }

        req = requests.post(url=self.env.get(key="serverUrl") + self.env.get(key="getModelUrl"), files=files)

        if req.status_code == 200:
            result = {'status': True,  'message': " model sent"}
        else:
            result = {'status': False, 'message': " model sent Failed!"}

        return result

