In client mode, the driver runs inside a pod.

# Client Mode Networking

Spark executors must be able to connect to the Spark driver by the means of Kubernetes networking. To do that, we use a [headless](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services) service to allow the driver pod to be routable from the executors by a stable hostname. When deploying the headless service, we ensure that the service will only match the driver pod and no other pods by assigning the driver pod a (sufficiently) unique label and by using that label in the `label selector` of the headless service. We can then pass to the executors the driver’s hostname via `spark.driver.host` with the service name and the spark driver’s port to `spark.driver.port`.

# Executor Pod Garbage Collection

We must also set `spark.kubernetes.driver.pod.name` for the executors to the name of the driver pod. When this property is set, the Spark scheduler will deploy the executor pods with an `ownerReference`, which in turn will ensure that once the driver pod is deleted from the cluster, all of the application’s executor pods will also be deleted.