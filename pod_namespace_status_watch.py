import os
import sys

from kubernetes import client, config, watch
from pick import pick


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

    count = 10
    w = watch.Watch()
    label_selector = "app-name=%s,spark-role=driver" % app_name
    for event in w.stream(v1.list_namespaced_pod, namespace=namespace, label_selector=label_selector, timeout_seconds=10):
        print("Event: %s" % event['object'].status.phase)
        count -= 1
        if not count:
            w.stop()
    print("Finished pod stream.")


if __name__ == "__main__":
    main()
