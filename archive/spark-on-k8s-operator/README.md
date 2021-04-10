# Configuring and installing the Kubernetes Operator for Apache Spark

In this section, you use [Helm](https://github.com/kubernetes/helm) to deploy the [Kubernetes Operator for Apache Spark](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator) from the incubator [Chart](https://github.com/helm/charts/tree/master/incubator/sparkoperator) repository. Helm is a package manager you can use to configure and deploy Kubernetes apps.

## Install Helm

1. Downlad and install the `Helm` binary:

```bash
wget https://get.helm.sh/helm-v3.3.4-linux-amd64.tar.gz
```

2. Unzip the file to your local system:

```bash
tar zxfv helm-v2.12.3-linux-amd64.tar.gz
cp linux-amd64/helm .
```

3. Ensure that Helm is properly installed by running the following command:

```bash
./helm version
```

If Helm is correctly installed, you should see the following output:

```bash
version.BuildInfo{Version:"v3.3.4", GitCommit:"a61ce5633af99708171414353ed49547cf05013d", GitTreeState:"clean", GoVersion:"go1.14.9"}
```

## Install the chart

```bash
helm repo add incubator http://storage.googleapis.com/kubernetes-charts-incubator
kubectl create namespace spark-operator
helm install spark-operator incubator/sparkoperator --namespace spark-operator --set enableWebhook=true --set enableBatchScheduler=true
```

The flag`enableBatchScheduler=true` enables Volcano. To install the operator with Vocano enabled, you must also install 
the mutating admission webhook with the flag `enableWebhook=true`.

Now you should see the operator running in the cluster by checking the status of the Helm release:


```bash
./helm status spark-operator --namespace spark-operator
```

## About the Spark Job Namespace and the Service Account for Driver Pods

We did not set a specific value for the Helm chart property `sparkJobNamespace` when installing the operator, that means 
the Spark Operator supports deploying `SparkApplications` to all namespaces.
As a consequence, the Spark Operator did not automatically create the service account for driver pods, and we must set 
up the RBAC for driver pods of our `SparkApplications` to be able to manipulate executor pods in a specific namespace.

See [Service Account for Driver Pods](../docs/gke.md#service-account-for-driver-pods) to set up the RBAC for driver 
pods.

See [About the Spark Job Namespace](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/quick-start-guide.md#about-the-spark-job-namespace) and [About the Service Account for Driver Pods](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/quick-start-guide.md#about-the-service-account-for-driver-pods) sections for more details.

# Running the Examples

To run the Spark Pi example, run the following command:

```bash
kubectl apply -f k8s/examples/spark-py-pi.yaml
```

According to our [configuration](../docs/gke.md#service-account-for-driver-pods), `.metadata.namespace` must be set to 
"spark-jobs" and  `.spec.driver.serviceAccount` is set to the name of the service account "hippi-spark" previously 
created.

# See also

- [Kubernetes Operator for Apache Spark - Quick Start Guide](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/quick-start-guide.md)
- [Integration with Volcano for Batch Scheduling](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/blob/master/docs/volcano-integration.md)
