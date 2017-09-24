# POC Kubernetes Scheduler for bursting to ACI

Quick POC Kubernetes custom scheduleer to schedule first on K8S node and then ‘burst’ to ACI once a defined replica threshold has been crossed.

## Current state:

This is working to assign pods to ACI.

Current challenge is that I cannot figure out how to remove PODS from ACI (or any named node) in a scale in operations. Need to follow up on this, referencing this stack overflow article:

https://stackoverflow.com/questions/33617090/kubernetes-scale-down-specific-pods
