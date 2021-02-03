import requests, json

from Env import Env


class SecurityManagerSDK(object):

    env = Env()

    def sendStatus(self):
        data = {'client_id': self.env.get(key="port"), 'client_host': self.env.get(key="host")}
        r = requests.post(url="api_url", json=data)
        print(r, r.status_code, r.reason, r.text)
        if r.status_code == 200:
            print("yeah")
        else:
            print("not")
            # TODO : Error handling
        return "Status OK sent !"

