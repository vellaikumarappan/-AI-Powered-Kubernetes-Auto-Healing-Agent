from monitor import check_cluster
from k8s_utils import get_pod_logs, get_pod_description
from analyzer import analyze_logs
from fixer import apply_fix
from concurrent.futures import ThreadPoolExecutor

# def process_pod(pod):
#     logs = get_pod_logs(pod["name"], pod["namespace"])

#     combined_input = f"""
#     Status: {pod['status']}
#     Reason: {pod['reason']}
#     Logs:
#     {logs}
#     """

#     # 🔥 Smart routing
#     if pod["reason"] == "CrashLoopBackOff":
#         if logs and ("Error" in logs or "Traceback" in logs) :
#             # Application failure → send to AI
#             analysis = analyze_logs(combined_input, pod)
#         else:
#             # Infra failure → rule-based
#             analysis = {
#                 "root_cause": "Container crashing",
#                 "severity": "High",
#                 "fix": "Restart pod",
#                 "confidence": 80
#             }
#     else:
#         analysis = analyze_logs(combined_input, pod)

#     fix_result = apply_fix(pod, analysis)

#     return {
#         "pod": pod,
#         "logs": logs,
#         "analysis": analysis,
#         "fix": fix_result
#     }

def process_pod(pod):
    logs = get_pod_logs(pod["name"], pod["namespace"])
    describe = get_pod_description(pod["name"], pod["namespace"])

    combined_input = f"""
Pod Name: {pod['name']}
Namespace: {pod['namespace']}

Status: {pod['status']}
Reason: {pod['reason']}
Message: {pod.get('message', '')}

Events:
{describe}

Logs:
{logs}
"""

    analysis = analyze_logs(combined_input, pod)
    fix_result = apply_fix(pod, analysis)

    return {
        "pod": pod,
        "logs": logs,
        "describe": describe,
        "analysis": analysis,
        "fix": fix_result
    }

def run_agent():
    pods = check_cluster()

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(process_pod, pods))

    return results