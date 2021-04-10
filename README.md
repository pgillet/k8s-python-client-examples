When using the Kubernetes Python client library, we must first load authentication and cluster information.

# Service Account and Role Binding

First, you need to setup the required service account and roles.

```bash
kubectl create -f k8s/rbac.yaml
```

This command creates a new service account named `python-client-sa`, a new role with the needed permissions in the 
`spark-jobs` namespace and then binds the new role to the newly created service account.

**WARNING**: The `python-client-sa` is the service account that will provide the identity for the Kubernetes Python 
Client in the `spark_client` library. Do not confuse this service account with the `hippi-spark` service account for 
driver pods.

# The Easy Way

In this method, we can use an helper utility to load authentication and cluster information from a `kubeconfig` file and
 store them in `kubernetes.client.configuration`.

```python
from kubernetes import config, client

config.load_kube_config("path/to/kubeconfig_file")

v1 = client.CoreV1Api()

print("Listing pods with their IPs:")

ret = v1.list_namespaced_pod(namespace="spark-jobs")
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
```

But we **DO NOT** want to rely on the default `kubeconfig` file, denoted by the environment variable `KUBECONFIG` or
, failing that, in `~/.kube/config`. This `kubeconfig` file is yours, as user of the `kubectl` command. Concretely
, with this `kubeconfig` file, you have the right to do almost everything in the K8s cluster, and in all namespaces
. Instead, we're going to generate one especially for the service account created above, with the help of the script
 [`kubeconfig-gen.sh`](./kubeconfig-gen.sh).
The `kubeconfig-gen.sh` script effectively uses the default `kubeconfig` file, but its purpose is to generate another
 `kubeconfig` file that configures access to the cluster for the `python-client-sa` service account, with only the
  rights needed for the `spark_client` Python library in the single namespace `spark-jobs` (_"principle of least
   privilege"_).

# The Hard Way

## Fetch credentials

Here, we're going to configure the Python client in the most programmatic way possible.  
First, we need to fetch the credentials to access the Kubernetes cluster. We’ll store these in python environmental 
variables.

```bash
export APISERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
SECRET_NAME=$(kubectl get serviceaccount python-client-sa -o jsonpath='{.secrets[0].name}')
export TOKEN=$(kubectl get secret ${SECRET_NAME} -o jsonpath='{.data.token}' | base64 --decode)
export CACERT=$(kubectl get secret ${SECRET_NAME} -o jsonpath="{['data']['ca\.crt']}")
```

Note that environment variables are captured the first time the `os` module is imported, typically during IDE/Python 
startup. Changes to the environment made after this time are not reflected in `os.environ` (except for changes made by 
modifying os.environ directly).

## Python sample usage

```python
import base64
import os
from tempfile import NamedTemporaryFile

from kubernetes import client

api_server = os.environ["APISERVER"]
cacert = os.environ["CACERT"]
token = os.environ["TOKEN"]

# Set the configuration
configuration = client.Configuration()
with NamedTemporaryFile(delete=False) as cert:
    cert.write(base64.b64decode(cacert))
    configuration.ssl_ca_cert = cert.name
configuration.host = api_server
configuration.verify_ssl = True
configuration.debug = False
configuration.api_key = {"authorization": "Bearer " + token}
client.Configuration.set_default(configuration)

v1 = client.CoreV1Api()

print("Listing pods with their IPs:")

ret = v1.list_namespaced_pod(namespace="spark-jobs")
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
```