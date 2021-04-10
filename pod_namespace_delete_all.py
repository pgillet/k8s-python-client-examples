import os

from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config_file = os.path.join(os.path.dirname(__file__), "kubeconfig-sa")
config.load_kube_config(config_file)

v1 = client.CoreV1Api()
namespace = "spark-jobs"

# Delete all pods in spark-jobs namespace
ret = v1.list_namespaced_pod(namespace=namespace, watch=False)
for i in ret.items:
    print("Deleting pod %s" % i.metadata.name)
    v1.delete_namespaced_pod(i.metadata.name, namespace)
