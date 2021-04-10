import os

from kubernetes import client, config

# Configs can be set in Configuration class directly or using helper utility
config_file = os.path.join(os.path.dirname(__file__), "kubeconfig-sa")
config.load_kube_config(config_file)

namespace = "spark-jobs"
group = "sparkoperator.k8s.io"
version = "v1beta2"
plural = "sparkapplications"

# Delete all SparkApplications in spark-jobs namespace
custom_object_api = client.CustomObjectsApi()

ret = custom_object_api.list_namespaced_custom_object(
    group=group,
    version=version,
    namespace=namespace,
    plural=plural,
    watch=False)

for i in ret["items"]:
    app_name = i["metadata"]["name"]
    print("Deleting SparkApplication %s" % app_name)
    custom_object_api.delete_namespaced_custom_object(
        group=group,
        version=version,
        namespace=namespace,
        plural=plural,
        name=app_name,)
