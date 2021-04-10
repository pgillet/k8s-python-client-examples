import binascii
import os
from os import listdir
from pprint import pprint

import yaml
from kubernetes import config, utils
from kubernetes.client import ApiClient


def create_k8s_object(yaml_file=None, env_subst=None):
    with open(yaml_file) as f:
        str = f.read()
        if env_subst:
            for env in env_subst:
                str = str.replace(env, env_subst[env])
        return yaml.safe_load(str)


def main():
    # Configs can be set in Configuration class directly or using helper utility
    config.load_kube_config("kubeconfig-sa")

    name_suffix = "-" + binascii.b2a_hex(os.urandom(8))
    priority_class_name = "routine"
    env_subst = {"${NAMESPACE}": "spark-jobs",
                 "${SERVICE_ACCOUNT_NAME}": "hippi-spark",
                 "${DRIVER_NODE_AFFINITIES}": "driver",
                 "${EXECUTOR_NODE_AFFINITIES}": "compute",
                 "${NAME_SUFFIX}": name_suffix,
                 "${PRIORITY_CLASS_NAME}": priority_class_name}

    k8s_client = ApiClient()
    verbose = True

    # Create driver pod
    k8s_dir = os.path.join(os.path.dirname(__file__), "k8s/spark-submit")
    k8s_object_dict = create_k8s_object(os.path.join(k8s_dir, "pyspark-pi-driver-pod.yaml"), env_subst)
    pprint(k8s_object_dict)
    k8s_objects = utils.create_from_dict(k8s_client, k8s_object_dict, verbose=verbose)

    # Prepare ownership on dependent objects
    owner_refs = [{"apiVersion": "v1",
                   "controller": True,
                   "kind": "Pod",
                   "name": k8s_objects[0].metadata.name,
                   "uid": k8s_objects[0].metadata.uid}]

    # List all YAML files in k8s/spark-submit directory, except the driver pod definition file
    other_resources = listdir(k8s_dir)
    other_resources.remove("pyspark-pi-driver-pod.yaml")
    for f in other_resources:
        k8s_object_dict = create_k8s_object(os.path.join(k8s_dir, f), env_subst)
        # Set ownership
        k8s_object_dict["metadata"]["ownerReferences"] = owner_refs
        pprint(k8s_object_dict)
        utils.create_from_dict(k8s_client, k8s_object_dict, verbose=verbose)

    print("Submitted %s" % (k8s_objects[0].metadata.labels["app-name"]))

if __name__ == "__main__":
    main()
