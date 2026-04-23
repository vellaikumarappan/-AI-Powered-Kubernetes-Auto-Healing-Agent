from k8s_utils import get_failed_pods

def check_cluster():
    return get_failed_pods()