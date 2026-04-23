from k8s_utils import delete_pod

def apply_fix(pod, analysis):
    reason = (pod.get("reason") or "").lower()

    fix = analysis.get("fix", "").lower()
    root_cause = analysis.get("root_cause", "").lower()

    # 🚫 DO NOT restart for application logic errors
    if any(err in root_cause for err in ["exception", "error", "division", "traceback"]):
        return "Manual fix required: Application logic error"

    # 🔥 SAFE AUTO-HEAL: CrashLoop without app error
    if reason == "crashloopbackoff":
        if "no clear application error" in root_cause or "repeatedly crashing" in root_cause:
            delete_pod(pod["name"], pod["namespace"])
            return "Pod restarted (auto-healed)"

        return "Manual fix required: Investigate application crash"

    # ❌ Image issues → manual
    if reason == "imagepullbackoff":
        return "Manual fix required: Invalid image"

    # ❌ OOM → manual (for now)
    if reason == "oomkilled":
        return "Manual fix required: Increase memory limits"

    return "No automatic fix applied"