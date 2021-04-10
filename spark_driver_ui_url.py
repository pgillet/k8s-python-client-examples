import os
import random
import sys

from kubernetes import client, config
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

    # NodePort URL
    # ui_service_name = app_name + "-ui-svc"
    # core_v1_api = client.CoreV1Api()
    #
    # ui_svc = core_v1_api.read_namespaced_service(name=ui_service_name, namespace="spark-jobs")
    # node_port = ui_svc.spec.ports[0].node_port
    #
    # # Choose a random node
    # nodes = core_v1_api.list_node()
    # n = random.randint(0, len(nodes.items) - 1)
    # node = nodes.items[n]
    #
    # external_ip = filter(lambda addr: addr.type == "ExternalIP", node.status.addresses)[0].address
    #
    # print("The Spark Web UI is available at http://%s:%s" % (external_ip, node_port))

    # Ingress URL
    ui_ingress_name = app_name + "-ui-ingress"
    networking_v1_beta1_api = client.NetworkingV1beta1Api()
    ui_ingress_status = networking_v1_beta1_api.read_namespaced_ingress_status(name=ui_ingress_name, namespace="spark-jobs")

    if ui_ingress_status.status.load_balancer.ingress is not None:
        external_ip = ui_ingress_status.status.load_balancer.ingress[0].ip
        print("The Spark Web UI is available at http://%s/%s" % (external_ip, app_name))
    else:
        print("Ingress not yet available")


if __name__ == "__main__":
    main()
