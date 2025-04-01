---
```markdown
# 🧠 Qdrant Vector Database – Production Helm Setup on GKE

This document outlines a full-scale deployment of Qdrant on Google Kubernetes Engine (GKE) using Helm, optimized for internal search workloads and snapshot management.

---

## 🚀 Deployment Overview

| Component  | Description                               |
|------------|-------------------------------------------|
| **Qdrant** | Vector DB (StatefulSet, 4 pods, 8 vCPU each) |
| **GKE**    | Cluster with tainted node pool (`qdrant-vector`) |
| **Storage**| 50Gi SSD PVC (`premium-rwo`) mounted to `/qdrant/storage` |
| **Exposure**| Internal LoadBalancer + per-pod LBs for snapshots |
| **Monitoring**| Prometheus, Grafana with PVC + Qdrant dashboards |
| **Alerts**| PVC usage, pod crashes, memory, Qdrant health |

---

## 📦 Helm Chart Used

```bash
helm repo add qdrant https://qdrant.github.io/qdrant-helm
helm install qdrant qdrant/qdrant -n qdrant-vector -f values.yaml
```

---

## ⚙️ Key `values.yaml` Highlights

```yaml
replicaCount: 4
resources:
  requests:
    cpu: "8"
    memory: "16Gi"
  limits:
    cpu: "8"
    memory: "16Gi"

nodeSelector:
  cloud.google.com/gke-nodepool: qdrant-vector

tolerations:
  - key: service
    value: qdrant
    effect: NoSchedule

service:
  type: LoadBalancer
  annotations:
    cloud.google.com/load-balancer-type: "Internal"

persistence:
  enabled: true
  size: 50Gi
  storageClass: premium-rwo
```

---

## 📡 Networking Setup

### 🔹 Internal LoadBalancer
- Qdrant exposed on internal IP: `10.90.140.70`
- Only accessible within the VPC

### 🔹 Per-Pod Snapshot Access (via additional LBs)
Each pod (`qdrant-0` to `qdrant-3`) has its own `LoadBalancer` service:

| Pod        | LB IP           | URL                              |
|------------|------------------|----------------------------------|
| qdrant-0   | `10.90.140.80`   | `http://10.90.140.80/snapshots`  |
| qdrant-1   | `10.90.140.81`   | `http://10.90.140.81/snapshots`  |
| qdrant-2   | `10.90.140.82`   | `http://10.90.140.82/snapshots`  |
| qdrant-3   | `10.90.140.83`   | `http://10.90.140.83/snapshots`  |

---

## 📈 Monitoring & Alerting

### 🔧 Tools Used
- Prometheus (via kube-prometheus-stack)
- Grafana
- Alertmanager (Slack/Email/Teams)

### ✅ Dashboards Imported
- `13646` – Kubernetes PVC Usage (Grafana)
- Custom dashboard for:
  - Qdrant memory
  - Search traffic
  - Snapshot activity
  - Uptime & restarts

### 🔔 Alerts Configured
| Alert Name            | Trigger                                            |
|-----------------------|----------------------------------------------------|
| PVCUsageHigh          | PVC usage > 90%                                    |
| QdrantPodDown         | Qdrant pod not ready                               |
| SnapshotFailure       | Snapshot count stops increasing                    |
| MemorySpike           | > 14Gi memory used                                 |
| PodRestartSpike       | Restarts > 3 in 10min                              |

---

## 🛠 Maintenance Notes

- **Scale Pods**: edit `replicaCount` in `values.yaml`
- **Access Pod**: use per-pod LoadBalancer IPs
- **Restart / Rollout**: via `helm upgrade`
- **Clean snapshots**: manually via `/snapshots` HTTP endpoint
- **Static IPs**: reserved via `gcloud compute addresses`

---

## 📁 Directory Layout (Git Repo)

```
/qdrant-helm/
├── values.yaml                     # Main config
├── snapshot-lb-services.yaml      # One LB per pod for snapshots
├── serviceMonitor-qdrant.yaml     # For /metrics
└── README.md                      # This file
```

---

## 🤠 Built & Managed By

DevOps Cowboy Lalith Sagar J 🧠💀  
Partnered with GPT-4 and pure YAML rage.

---
