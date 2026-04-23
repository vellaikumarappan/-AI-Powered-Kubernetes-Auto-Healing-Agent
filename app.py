import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="K8s AI Auto-Healer",
    layout="wide"
)

st.title("🚀 AI-Powered Kubernetes Auto-Healing Agent")

if st.button("Scan Cluster"):
    with st.spinner("Analyzing cluster..."):
        results = run_agent()

    # ✅ Handle healthy cluster
    if not results:
        st.success("✅ All pods are healthy. No issues detected in the cluster.")
        st.info("Nothing to analyze or fix.")
    else:
        st.warning(f"⚠️ Found {len(results)} problematic pod(s)")

        for item in results:
            pod = item["pod"]

            st.subheader(f"Pod: {pod['name']} ({pod['namespace']})")

            # 🔥 Severity highlighting
            analysis = item["analysis"]

            if isinstance(analysis, dict):
                severity = analysis.get("severity", "Unknown")
            else:
                severity = str(analysis)

            if "High" in severity:
                st.error("🔴 High Severity Issue")
            elif "Medium" in severity:
                st.warning("🟠 Medium Severity Issue")
            else:
                st.success("🟢 Low Severity")

            # 🔹 Pod Status Info
            st.markdown("**Pod Status Info**")
            st.json({
                "status": pod.get("status"),
                "reason": pod.get("reason"),
                "message": pod.get("message", "")
            })

            # 🔹 Logs
            with st.expander("📄 Logs"):
                if item["logs"]:
                    st.code(item["logs"])
                else:
                    st.write("No logs available")

            # 🔥 NEW: Pod Events (Describe)
            with st.expander("📌 Pod Events (Describe)"):
                if item.get("describe"):
                    st.code(item["describe"])
                else:
                    st.write("No events found")

            # 🔹 Analysis
            with st.expander("🧠 AI Analysis"):
                if isinstance(analysis, dict):
                    st.json(analysis)
                else:
                    st.write(analysis)

            # 🔹 Fix Applied
            with st.expander("🛠 Fix Applied"):
                st.write(item["fix"])

            st.markdown("---")