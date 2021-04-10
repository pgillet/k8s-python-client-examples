import os
import sys

from kubernetes import client, config
from pick import pick

"""
Delete all resources of a Spark application by its name. 
"""


def is_launched_by_spark_operator(k8s_object=None):
    return "sparkoperator.k8s.io/launched-by-spark-operator" in k8s_object.metadata.labels


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
        print("No Spark app to delete")
        sys.exit()

    # ---
    label_selector = "app-name=%s,spark-role=driver" % app_name
    ret = v1.list_namespaced_pod(namespace=namespace, label_selector=label_selector)
    if (len(ret.items)) > 1:
        raise ValueError("Spark app name should be unique")
    if ret.items:
        pod = ret.items[0]
        if is_launched_by_spark_operator(pod):
            # Launched by Spark Operator
            custom_object_api = client.CustomObjectsApi()
            custom_object_api.delete_namespaced_custom_object(
                group="sparkoperator.k8s.io",
                version="v1beta2",
                namespace=namespace,
                plural="sparkapplications",
                name=app_name,
                propagation_policy="Background")
        else:
            # Launched by spark-submit
            v1.delete_namespaced_pod(pod.metadata.name, namespace, propagation_policy="Background")

        # Due to ownership relationships, all dependent objects are deleted in cascade and in the background
        print("Deleted Spark application %s" % app_name)


if __name__ == "__main__":
    main()
