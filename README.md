# 🚀 AI-Powered Kubernetes Auto-Healing Agent

An intelligent system that detects, analyzes, and suggests fixes for failing Kubernetes pods using a hybrid approach combining rule-based logic and AI.

---

## 🧠 Overview

Debugging Kubernetes failures usually requires checking:

- Pod status  
- Events (`kubectl describe`)  
- Logs (`kubectl logs`)  

This project automates that process by:

- Scanning the cluster for failing pods  
- Collecting pod status, events, and logs  
- Using rule-based detection for known issues  
- Using AI for application-level failures  
- Suggesting fixes intelligently  

---

## ⚙️ Architecture

```
Kubernetes Cluster
        ↓
  Pod Detection
        ↓
Status + Events + Logs
        ↓
 Rule-Based Engine
        ↓
    AI Analysis
        ↓
 Fix Recommendation
```

---

## 🔍 Features

- Detects failing pods  
- Uses logs + events + status  
- Hybrid approach:
  - Rule-based → fast  
  - AI-based → deep analysis  
- Differentiates:
  - Infra issues (ImagePull, OOM, Pending)  
  - App issues (runtime errors)  
- Suggests fixes  
- Avoids blind restarts  

---

## 🧪 Failure Scenarios

- ImagePullBackOff → wrong image  
- CrashLoopBackOff → container crash  
- Logic error → division by zero  
- Config error → missing env  
- OOMKilled → memory issue  
- Pending → resource issue  

---

## 🛠 Tech Stack

- Python  
- Kubernetes Python Client  
- Streamlit  
- Cohere LLM  

---

## 🚀 How to Run

### 1. Clone repo

```bash
git clone <your-repo-link>
cd <repo>
```

---

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Add API key

Create a file:

```
api_key.env
```

Add:

```
COHERE_API_KEY=your_api_key
```

---

### 4. Run app

```bash
streamlit run app.py
```

---

### 5. Create test pods

```bash
kubectl apply -f .
```

---

### 6. Use the app

- Open Streamlit UI  
- Click **Scan Cluster**  

---

### 7. Cleanup

```bash
kubectl delete -f .
```

---

## 🧠 Key Design Decisions

- Avoided blind automation  
- Used rules for known issues  
- Used AI only when needed  
- Combined logs + events + status  

---

## 🚧 Future Improvements

- Kubernetes Operator  
- Real-time monitoring  
- Alerts (Slack, Email)  
- Learning system  

---

## ⭐ Note

This project demonstrates how AI can be applied to Kubernetes troubleshooting (AIOps).