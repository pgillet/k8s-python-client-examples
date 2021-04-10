import os

from kubernetes import client, config
from pick import pick

# Configs can be set in Configuration class directly or using helper utility
config_file = os.path.join(os.path.dirname(__file__), "kubeconfig-sa")
config.load_kube_config(config_file)

v1 = client.CoreV1Api()
namespace = "spark-jobs"

print("Listing pods with their IPs:")

ret = v1.list_namespaced_pod(namespace=namespace)
options = []
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    options.append(i.metadata.name)

title = "Please choose a Pod: "
pod_name, index = pick(options, title)

pod_status = v1.read_namespaced_pod_status(pod_name, namespace)  # Cannot be watched
print("Pod status: %s" % pod_status.status.phase)
