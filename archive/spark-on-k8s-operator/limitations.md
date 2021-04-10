# Spark Operator limitations

Some Spark properties are related to "deployment", typically set through configuration file or `spark-submit` command line options with "native" Spark. 
These properties will not be applied if passed directly to `.spec.sparkConf` in the `SparkApplication` custom resource. Indeed, `.spec.sparkConf` is only intended for properties that affect Spark runtime control, like `spark.task.maxFailures`.

**Example:**
Setting `spark.executor.instances` in `.spec.sparkConf` will not affect the number of executors. Instead, we have to set the field `.spec.executor.instances` in the `SparkApplication` yaml file.

It would be nice if we could set/override such properties in `.spec.sparkConf`. Thus, we could easily "templatize" a SparkApplication and set runtime parameters with Spark semantics. In other terms, we should be able to move the cursor as we want between native Spark and Spark Operator semantics.

The concerned properties identified so far:

- spark.kubernetes.driver.request.cores
- spark.kubernetes.executor.request.cores
- spark.kubernetes.executor.deleteOnTermination
- spark.driver.cores
- spark.executor.cores
- spark.executor.instances
- spark.kubernetes.container.image
- spark.kubernetes.driver.container.image
- spark.kubernetes.executor.container.image
- spark.kubernetes.container.image.pullPolicy

`spark.submit.pyFiles` and `spark.jars` may also be concerned. If they are, it is a problem as these properties are multi-valued: `.spec.deps.pyFiles` must be an array of strings, while the Spark property is only a string containing comma-separated Python dependencies, and in this case it is not easy to switch from the Spark semantics to the Spark Operator logic...

At the time of writing this manual, an [issue](https://github.com/GoogleCloudPlatform/spark-on-k8s-operator/issues/1109) has been opened in the Spark Operator Github repository. Case to follow...

