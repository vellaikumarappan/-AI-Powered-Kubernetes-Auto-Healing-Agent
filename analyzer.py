import os
from langchain_cohere import ChatCohere
from dotenv import load_dotenv
import json
import re

load_dotenv("api_key.env")

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

llm = ChatCohere(
    cohere_api_key=COHERE_API_KEY,
    temperature=0.2,
    model="command-a-03-2025"
)

def rule_based_analysis(pod, combined_input):
    """
    Hybrid rule engine:
    - Uses structured pod data (reason, status)
    - Uses combined_input (logs + events) for pattern detection
    - Returns None if AI should handle
    """

    reason = (pod.get("reason") or "").lower()
    status = (pod.get("status") or "").lower()
    message = (pod.get("message") or "").lower()
    text = combined_input.lower()

    # =========================================================
    # 🔥 PRIORITY 1: STRONG K8S SIGNALS (pod.reason)
    # =========================================================

    if reason in ["imagepullbackoff", "errimagepull"] or "pull image" in text:
        return {
            "root_cause": "Invalid or inaccessible container image",
            "severity": "High",
            "fix": "Verify image name, tag, and registry credentials",
            "confidence": 98,
            "source": "rule"
        }

    if reason == "oomkilled" or "oomkilled" in text or "out of memory" in text:
        return {
            "root_cause": "Container killed due to out-of-memory",
            "severity": "High",
            "fix": "Increase memory limits or optimize application memory usage",
            "confidence": 97,
            "source": "rule"
        }

    if status == "pending":
        if "insufficient" in text or "not enough" in text:
            return {
                "root_cause": "Pod not scheduled due to insufficient resources",
                "severity": "Medium",
                "fix": "Reduce resource requests or add more nodes",
                "confidence": 92,
                "source": "rule"
            }

        return {
            "root_cause": "Pod pending (unknown scheduling issue)",
            "severity": "Medium",
            "fix": "Check node capacity and scheduling constraints",
            "confidence": 80,
            "source": "rule"
        }

    # =========================================================
    # 🔥 PRIORITY 2: LOG / EVENT PATTERNS
    # =========================================================

    if "connection refused" in text:
        return {
            "root_cause": "Service endpoint not reachable",
            "severity": "Medium",
            "fix": "Check service availability and network connectivity",
            "confidence": 85,
            "source": "rule"
        }

    if "permission denied" in text:
        return {
            "root_cause": "Permission issue",
            "severity": "High",
            "fix": "Check file permissions or security context",
            "confidence": 90,
            "source": "rule"
        }

    if "no such file or directory" in text:
        return {
            "root_cause": "Missing file or incorrect path",
            "severity": "High",
            "fix": "Verify file paths and container image contents",
            "confidence": 90,
            "source": "rule"
        }

    if "back-off restarting failed container" in text and not any(err in text for err in ["exception", "traceback", "error"]):
        return {
            "root_cause": "Container repeatedly failing to start",
            "severity": "High",
            "fix": "Inspect application startup logs and configuration",
            "confidence": 88,
            "source": "rule"
        }

    # =========================================================
    # 🔥 SPECIAL: CrashLoopBackOff (SMART HANDLING)
    # =========================================================

    if reason == "crashloopbackoff":
        # 👉 If logs show application error → let AI analyze
        if any(err in text for err in ["error", "exception", "traceback", "failed"]):
            return None  # 🔥 route to AI

        # 👉 Otherwise treat as generic crash
        return {
            "root_cause": "Container crashing repeatedly (no clear application error)",
            "severity": "High",
            "fix": "Restart pod or inspect startup configuration",
            "confidence": 85,
            "source": "rule"
        }

    # =========================================================
    # 🔥 DEFAULT: LET AI HANDLE
    # =========================================================

    return None

def ai_analysis(combined_input):
    prompt = f"""
You are a Kubernetes debugging expert.

Return ONLY valid JSON. No explanation. No markdown.

FORMAT:
{{
  "root_cause": "...",
  "severity": "Low/Medium/High",
  "fix": "...",
  "confidence": 0-100
}}

Rules:
- Do NOT include markdown
- Do NOT include ```json
- Do NOT include explanation
- Output must start with {{ and end with }}

INPUT:
{combined_input}
"""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()

        # 🔥 Clean markdown if present
        content = content.replace("```json", "").replace("```", "").strip()

        # 🔥 Extract JSON safely (non-greedy)
        match = re.search(r'\{.*?\}', content, re.DOTALL)

        if match:
            return json.loads(match.group())

        raise ValueError("No JSON found")

    except Exception as e:
        return {
            "root_cause": f"AI parsing failed: {str(e)}",
            "severity": "Low",
            "fix": "Manual investigation required",
            "confidence": 50,
            "source": "fallback"
        }
    
def analyze_logs(combined_input, pod):
    """
    Hybrid analyzer:
    1. Rule-based detection (fast + accurate)
    2. AI fallback for unknown/app issues
    """

    # ✅ Step 1: Rule-based
    rule_result = rule_based_analysis(pod, combined_input)
    if rule_result:
        return rule_result

    # ✅ Step 2: AI fallback
    return ai_analysis(combined_input)