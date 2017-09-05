import json
import requests
import sys

K8S_API = "http://localhost:8001/api/v1/"
BURST_VALUE = 3
ACI_NODE_NAME = "aci-connector"

# FUNCTION - Verify Kubernetes API
def verify_api():
    try:
        requests.get(K8S_API)
    except requests.exceptions.RequestException as e:
        print('Could not connect to: ' + K8S_API + ' API. Program will exit.')
        sys.exit(1)

# FUNCTION - Get app labels
# Searches for any unassigned pod that is also assigned the custom scheduler.
# The app label for this pod is returned.
# This is needed so that all pods with the common app label can be inventoried.
def get_app_label():

    APP_LABEL_LIST = []

    # Return pod object
    POD_RESPONSE = requests.get(K8S_API + "pods")
    pod_object = json.loads(POD_RESPONSE.text)

    # Return nonscheduled pods assigned the custom scheduler
    for item in pod_object['items']:
        if item['spec']['schedulerName'] == 'test-scheduler' and item['status']['phase'] == 'Pending':

            # Get app label
            APP_LABEL = item['metadata']['labels']['app']

            if APP_LABEL not in APP_LABEL_LIST:
                APP_LABEL_LIST.append(APP_LABEL)

    return APP_LABEL_LIST

# FUNCTION - get all pods with app label
# Here all pods that match an app label are evaluated for node assignment.
# If assigned to K8S node, counter is incremented.
# If not assigned to a node, pod is returned in a list.
def get_pods(app_label, node_list):

    COUNT_SCHEDULED_ACS = 0
    POD_TO_SCHEDULE = []

    PODS_FILTERED = requests.get(K8S_API + "pods?labelSelector=app=" + app_label)
    PODS_FILTERED_OBJECT = json.loads(PODS_FILTERED.text)
 
    # Check for node, increment of present
    for item in PODS_FILTERED_OBJECT['items']:
        if 'nodeName' in item['spec']:
            COUNT_SCHEDULED_ACS += 1
        else:
            POD_TO_SCHEDULE.append(item['metadata']['name'])

    return COUNT_SCHEDULED_ACS, POD_TO_SCHEDULE

# FUNCTION - Schedule pod
def schedule_pod(pod, node):

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

# FUNCTION - Get Nodes
def get_nodes ():

    NODE_LIST = []
    
    # Return node object
    NODE_RESPONSE = requests.get(K8S_API + "nodes")
    node_object = json.loads(NODE_RESPONSE.text)

    # Get node name
    for item in node_object['items']:
        NODE = item['metadata']['name']

        # Get node status
        for condition in item['status']['conditions']:
            if condition['type'] == 'Ready':
                NODE_STATUS = condition['status']

        # Exclude ACI Connector and unready nodes
        if NODE != ACI_NODE_NAME and NODE_STATUS == 'True':
            NODE_LIST.append(NODE)

    return NODE_LIST


# Verify API connectivity
verify_api()

# Get list of app labels with unassigned pod with the custom scheduler
APP_LABELS_UNSCHEDULED = get_app_label()

# Get avalibale nodes
NODES = get_nodes()

for APP_LABEL_UNSCHEDULED in APP_LABELS_UNSCHEDULED:
    UNSCHEDULED_PODS = get_pods(APP_LABEL_UNSCHEDULED, NODES)
    print(UNSCHEDULED_PODS[1])

# Determine proper node (calc burst ++)

# Schedule pod on ACI node