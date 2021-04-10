import binascii
import os
import time
from pprint import pprint

import yaml
from kubernetes import config, client, utils, watch
from kubernetes.client import ApiClient
from kubernetes.client.exceptions import ApiException


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

    namespace = "spark-jobs"
    name_suffix = "-" + binascii.b2a_hex(os.urandom(8))
    priority_class_name = "routine"
    env_subst = {"${NAMESPACE}": namespace,
                 "${SERVICE_ACCOUNT_NAME}": "hippi-spark",
                 "${DRIVER_NODE_AFFINITIES}": "driver",
                 "${EXECUTOR_NODE_AFFINITIES}": "compute",
                 "${NAME_SUFFIX}": name_suffix,
                 "${PRIORITY_CLASS_NAME}": priority_class_name}

    custom_object_api = client.CustomObjectsApi()

    # Create pod
    yaml_file = os.path.join(os.path.dirname(__file__), "k8s/spark-operator/pyspark-pi.yaml")
    spark_app = create_k8s_object(yaml_file, env_subst)
    pprint(spark_app)

    # create the resource
    group = "sparkoperator.k8s.io"
    version = "v1beta2"
    plural = "sparkapplications"

    custom_object_api.create_namespaced_custom_object(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
        body=spark_app,
    )
    print("Resource created")

    # get the resource and print out data
    resource = custom_object_api.get_namespaced_custom_object(
        group=group,
        version=version,
        name="pyspark-pi-%s%s" % (priority_class_name, name_suffix),
        namespace=namespace,
        plural=plural,
    )
    print("Resource details:")
    pprint(resource)

    # Hijack the auto-created UI service and change its type from ClusterIP to NodePort
    # app_name = resource["metadata"]["name"]
    # ui_service_name = app_name + "-ui-svc"
    # core_v1_api = client.CoreV1Api()
    # 
    # w = watch.Watch()
    # field_selector = "metadata.name=%s" % ui_service_name
    # for event in w.stream(core_v1_api.list_namespaced_service, namespace=namespace,
    #                       field_selector=field_selector,
    #                       timeout_seconds=30):
    #     ui_svc = event['object']
    #     if ui_svc:
    #         w.stop()
    #     else:
    #         print("Event: UI service not yet available")
    #
    # ui_svc.spec.type = "NodePort"
    # core_v1_api.patch_namespaced_service(name=ui_service_name, namespace="spark-jobs", body=ui_svc)

    # Create ingress
    # Prepare ownership on dependent objects
    owner_refs = [{"apiVersion": "sparkoperator.k8s.io/v1beta2",
                   "controller": True,
                   "kind": "SparkApplication",
                   "name": resource["metadata"]["name"],
                   "uid": resource["metadata"]["uid"]}]

    yaml_file = os.path.join(os.path.dirname(__file__), "k8s/spark-operator/pyspark-pi-ui-ingress.yaml")
    k8s_object_dict = create_k8s_object(yaml_file, env_subst)
    # Set ownership
    k8s_object_dict["metadata"]["ownerReferences"] = owner_refs
    pprint(k8s_object_dict)
    k8s_client = ApiClient()
    utils.create_from_dict(k8s_client, k8s_object_dict, verbose=True)

if __name__ == "__main__":
    main()
