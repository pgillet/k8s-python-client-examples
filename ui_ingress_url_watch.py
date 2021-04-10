import os
import sys

from kubernetes import client, config, watch
from pick import pick

"""
Get the URL of a Spark application's Web UI.
"""


def main():
    # Configs can be set in Configuration class directly or using helper utility
    config_file = os.path.join(os.path.dirname(__file__), "kubeconfig-sa")
    config.load_kube_config(config_file)

    v1 = client.CoreV1Api()
    namespace = "spark-jobs"

    options = []
    # List all Spark applications
    ret = v1.list_namespaced_pod(namespace=namespace, label_selector="spark-role=driver")
    for pod in ret.items:
        options.append(pod.metadata.labels["app-name"])

    title = "Please choose a Spark Application: "
    if options:
        app_name, index = pick(options, title)
    else:
        print("No Spark app")
        sys.exit()

    # ---
    networking_v1_beta1_api = client.NetworkingV1beta1Api()
    w = watch.Watch()
    label_selector = "app-name=%s" % app_name
    for event in w.stream(networking_v1_beta1_api.list_namespaced_ingress, namespace=namespace,
                          label_selector=label_selector,
                          timeout_seconds=30):
        ingress = event['object'].status.load_balancer.ingress
        if ingress:
            external_ip = ingress[0].ip
            print("Event: The Spark Web UI is available at http://%s/%s" % (external_ip, app_name))
            w.stop()
        else:
            print("Event: Ingress not yet available")

    print("Finished pod stream.")


if __name__ == "__main__":
    main()
