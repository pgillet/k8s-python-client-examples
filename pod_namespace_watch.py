import os
from kubernetes import client, config, watch

# Configs can be set in Configuration class directly or using helper utility
config_file = os.path.join(os.path.dirname(__file__), "kubeconfig-sa")
config.load_kube_config(config_file)

v1 = client.CoreV1Api()
namespace = 'spark-jobs'
count = 10
w = watch.Watch()
for event in w.stream(v1.list_namespaced_pod, namespace=namespace, _request_timeout=60):
    print("Event: %s %s" % (event['type'], event['object'].metadata.name))
    count -= 1
    if not count:
        w.stop()

print("Ended.")
