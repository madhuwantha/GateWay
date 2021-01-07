import requests, json


class SecurityManagerSDK(object):

    @staticmethod
    def sendStatus():
        data = {'client_id': 80, 'client_host': 'host'}
        r = requests.post(url="api_url", json=data)
        print(r, r.status_code, r.reason, r.text)
        if r.status_code == 200:
            print("yeah")
        else:
            print("not")
            # TODO : Error handling
        return "Status OK sent !"

