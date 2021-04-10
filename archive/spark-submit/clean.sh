#!/usr/bin/env bash

NAMESPACE=${1:-spark-jobs}

# Delete all SparkApplications. If the associated application is running when the deletion happens,
# the application is killed and all Kubernetes resources associated with the application are deleted
# or garbage collected.
kubectl delete sparkapplications.sparkoperator.k8s.io --all --namespace=${NAMESPACE}

# Delete remaining pods (from spark-submit)
kubectl delete pods --all --namespace=${NAMESPACE}

# Delete services
kubectl delete svc --all --namespace=${NAMESPACE}
