#!/bin/bash -eux

# Priorities: routine urgent exceptional rush
PRIORITY_CLASS_NAME=${1:-routine}
# Spark image
SPARK_IMAGE=eu.gcr.io/hippi-spark-k8s/spark-py:3.0.1
# K8S cluster
# Use 'kubectl proxy' to communicate to the Kubernetes API
K8S_URL=http://127.0.0.1:8001
NAMESPACE=spark-jobs
SERVICE_ACCOUNT_NAME=hippi-spark

# Templates
DRIVER_TMPL=/tmp/driver-template_$$.yaml
cat > ${DRIVER_TMPL} << EOF
apiVersion: v1
kind: Pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
            - key: type
              operator: In
              values:
                - driver
  priorityClassName: ${PRIORITY_CLASS_NAME}
  schedulerName: volcano
EOF

EXECUTOR_TMPL=/tmp/executor-template_$$.yaml
cat > ${EXECUTOR_TMPL} << EOF
apiVersion: v1
kind: Pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
          - matchExpressions:
            - key: type
              operator: In
              values:
                - compute
  priorityClassName: ${PRIORITY_CLASS_NAME}
  schedulerName: volcano
EOF

# Start
cd ../../spark-3.0.1-bin-hadoop2.7

./bin/spark-submit \
    --master k8s://${K8S_URL} \
    --deploy-mode cluster \
    --name pyspark-pi-${PRIORITY_CLASS_NAME} \
    --conf spark.driver.cores=1 \
    --conf spark.driver.memory=512m \
    --conf spark.kubernetes.driver.limit.cores=1200m \
    --conf spark.executor.instances=2 \
    --conf spark.executor.cores=1 \
    --conf spark.executor.memory=512m \
    --conf spark.kubernetes.container.image=${SPARK_IMAGE} \
    --conf spark.kubernetes.container.image.pullPolicy=IfNotPresent \
    --conf spark.kubernetes.namespace=${NAMESPACE} \
    --conf spark.kubernetes.authenticate.driver.serviceAccountName=${SERVICE_ACCOUNT_NAME} \
    --conf spark.kubernetes.driver.podTemplateFile=${DRIVER_TMPL} \
    --conf spark.kubernetes.executor.podTemplateFile=${EXECUTOR_TMPL} \
    --conf spark.kubernetes.pyspark.pythonVersion=2 \
    https://storage.googleapis.com/hippi-spark-k8s-bucket/long_running_pi.py \
    2 0.001



