import json
import requests
import sys

pod = 'azure-vote-front-614820086-kzz5t'
node = 'aci-connector'
url = 'http://localhost:8001/api/v1/namespaces/default/pods/' + pod + '/binding'

headers = {'Content-Type': 'application/json'} 
payload = {
    "apiVersion": "v1",
    "kind": "Binding",
    "metadata": {
        "name": pod,
    },
    "target": {
        "apiVersion": "v1",
        "kind": "Node",
        "name": node,
    } 
}

r = requests.post(url, data=json.dumps(payload), headers=headers)