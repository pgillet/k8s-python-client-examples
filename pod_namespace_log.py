import os
import time
from Queue import Queue, Empty
from threading import Thread

from kubernetes import client, config, watch

from pick import pick

# Configs can be set in Configuration class directly or using helper utility
config_file = os.path.join(os.path.dirname(__file__), "kubeconfig-sa")
config.load_kube_config(config_file)

v1 = client.CoreV1Api()
namespace = "spark-jobs"

print("Listing pods with their IPs:")

ret = v1.list_namespaced_pod(namespace=namespace)
options = []
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    options.append(i.metadata.name)

title = "Please choose a Pod: "
pod_name, index = pick(options, title)


def logs():
    w = watch.Watch()
    for event in w.stream(v1.read_namespaced_pod_log, pod_name, namespace, _request_timeout=300):
        yield event

# iter = logs()
# while True:
#     try:
#         print(next(iter))
#     except StopIteration:
#         break

# for log in logs():
#     print(log)


def async_logs():
    q = Queue()

    def producer():
        for log in logs():
            q.put(log)

    t = Thread(target=producer)
    t.start()
    return q


q = async_logs()


def consumer(timeout_seconds=120):
    try:
        while True:
            item = q.get(timeout=timeout_seconds)
            print(item)
            q.task_done()
    except Empty:
        pass


num_worker_threads = 1
for i in range(num_worker_threads):
     t = Thread(target=consumer)
     t.start()

for i in range(10):
    print("Hello! Is anyone there in the main thread!?")
    time.sleep(10)

q.join()       # block until all tasks are done
