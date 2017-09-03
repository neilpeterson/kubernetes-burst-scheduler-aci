import json
import requests
import sys

K8S_API = "http://localhost:8001/api/v1/"

# Verify Kubernetes API
try:
    requests.get(K8S_API)
except requests.exceptions.RequestException as e:
    print('Could not connect to: ' + K8S_API + ' API. Program will exit.')
    sys.exit(1)
    
# Get Pods
POD_RESPONSE = requests.get(K8S_API + "pods")
pod_object = json.loads(POD_RESPONSE.text)

for item in pod_object['items']:
    print(item['metadata']['name'])
    print(item['spec']['schedulerName'])
    print(item['status']['phase'])

# Get Nodes
NODE_RESPONSE = requests.get(K8S_API + "nodes")
node_object = json.loads(NODE_RESPONSE.text)

for item in node_object['items']:
    print(item['metadata']['name'])
    print(item['status']['conditions'][3]['status'])

# Schedule pod

url = 'http://localhost:8001/api/v1/namespaces/default/pods/azure-vote-front-614820086-pvlm5/binding'

headers = {'Content-Type': 'application/json'} 
payload = {
    'apiVersion': 'v1',
    'kind': 'Binding',
    'metadata': {
        'name': 'azure-vote-front-614820086-pvlm5',
    },
    'target': {
        'apiVersion': 'v1',
        'kind': 'Node',
        'name': 'minikube',
    } 
}

r = requests.post(url, data=json.dumps(payload), headers=headers )