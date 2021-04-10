We use [Kustomize](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/) to customise the sample 
`SparkApplications` that are shipped within the Spark Operator and to compose our own `SparkApplications` that suit our 
needs and match the Kubernetes backend's configuration.

The **base** directory is `k8s/examples` in which the [`kustomization.yaml`](k8s/examples/kustomization.yaml) contains a 
single resource resolving to [`spark-py-pi.yaml`](k8s/examples/spark-py-pi.yaml). Here, the YAML files are as they are 
found in the Spark Operator and they are never changed.
 
We have one **overlay** directory which is `k8s/hippi-env`, with the `kustomization.yaml` referring to the base 
directory and containing merge patches. This allows to configure the targeted namespace, service account, node 
affinities, priorities..and so on, while separating the concerns.

To see the result of the "Kustomization", simply run the following command:

```bash
kubectl kustomize k8s/hippi-env
```

Actually, it is a little bit more complicated than that: we need to parameterize the `kustomization.yaml` in the 
overlay, as some specific parameters will only be known at runtime, in particular the `priorityClassName`, and the 
`SparkApplication`'s name which must be unique (if we intend to launch multiple applications).
Thus, we make a template out of a [`kustomization.template.yaml`](k8s/hippi-env/kustomization.template.yaml), that we 
instantiate as follows:

```bash
export NAMESPACE="spark-jobs"
export PRIORITY_CLASS="urgent"
export NAME_SUFFIX="-a-unique-suffix"

# Here, we create dynamically the actual kustomization.yaml
envsubst < k8s/hippi-env/kustomization.template.yaml > k8s/hippi-env/kustomization.yaml
kubectl kustomize k8s/hippi-env | kubectl apply -f -
```

We use `envsubst` to substitute the values of environment variables in the template. We then directly apply the YAML 
output of `kustomize` with `kubectl` by stdin. 






