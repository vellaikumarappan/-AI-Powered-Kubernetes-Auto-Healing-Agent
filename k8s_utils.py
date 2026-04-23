from kubernetes import client, config

def load_k8s():
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()

def get_failed_pods():
    load_k8s()
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces(watch=False)

    failed = []
    for pod in pods.items:
        name = pod.metadata.name
        namespace = pod.metadata.namespace
        phase = pod.status.phase

        reason = ""
        message = ""

        if pod.status.container_statuses:
            for cs in pod.status.container_statuses:
                if cs.state.waiting:
                    reason = cs.state.waiting.reason
                    message = cs.state.waiting.message
                elif cs.state.terminated:
                    reason = cs.state.terminated.reason
                    message = cs.state.terminated.message

        if phase != "Running" or reason:
            failed.append({
                "name": name,
                "namespace": namespace,
                "status": phase,
                "reason": reason,
                "message": message
            })

    return failed

def get_pod_logs(name, namespace):
    load_k8s()
    v1 = client.CoreV1Api()
    try:
        return v1.read_namespaced_pod_log(name=name, namespace=namespace, tail_lines=100, previous=True)
    except:
        return "No logs available"

def delete_pod(name, namespace):
    load_k8s()
    v1 = client.CoreV1Api()
    v1.delete_namespaced_pod(name=name, namespace=namespace)

def get_pod_description(name, namespace):
    load_k8s()
    v1 = client.CoreV1Api()

    try:
        pod = v1.read_namespaced_pod(name=name, namespace=namespace)
        events = v1.list_namespaced_event(namespace)

        event_messages = []

        for event in events.items:
            if event.involved_object.name == name:
                event_messages.append(
                    f"{event.reason}: {event.message}"
                )

        return "\n".join(event_messages) if event_messages else "No events found"

    except Exception as e:
        return f"Error fetching description: {str(e)}"