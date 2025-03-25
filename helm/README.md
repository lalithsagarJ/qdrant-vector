---

# 📘 Qdrant on GKE (Helm-Based Deployment) – Internal Docs

## 📦 What We Deployed
Qdrant vector database deployed via [official Helm chart](https://github.com/qdrant/qdrant-helm) into a GKE cluster, with:

- Node pool pinning (`qdrant-vector`)
- Internal LoadBalancer exposure
- Tolerations for tainted node pool
- Horizontal scaling (4 pods)
- CPU/memory requests per pod (8 CPU, 16Gi RAM)
- Persistent storage via GKE SSD

---

## 🧱 Helm Chart Source

```yaml
repoURL: https://qdrant.github.io/qdrant-helm
chart: qdrant
version: latest
```

---

## 🧠 Helm `values.yaml`

```yaml
replicaCount: 4

image:
  repository: qdrant/qdrant
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: LoadBalancer
  loadBalancerIP: 10.90.128.89  # Static IP reserved via gcloud
  annotations:
    cloud.google.com/load-balancer-type: "Internal"
  ports:
    - name: http
      port: 80
      targetPort: 6333
    - name: grpc
      port: 6334
      targetPort: 6334

nodeSelector:
  cloud.google.com/gke-nodepool: qdrant-vector

tolerations:
  - key: service
    value: qdrant
    effect: NoSchedule

resources:
  requests:
    cpu: "8"
    memory: "16Gi"
  limits:
    cpu: "8"
    memory: "16Gi"

persistence:
  enabled: true
  size: 50Gi
  accessModes:
    - ReadWriteOnce
  storageClass: premium-rwo  # or standard-rwo depending on GKE setup

affinity:
  podAntiAffinity:
    preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - qdrant
          topologyKey: "kubernetes.io/hostname"
```

---

## 🔁 Helm Commands Used

### Add repo & install:

```
helm repo add qdrant https://qdrant.github.io/qdrant-helm
helm repo update
```

### Install:

```
helm install qdrant qdrant/qdrant -n qdrant-vector -f values.yaml
```

### Upgrade:

```
helm upgrade qdrant qdrant/qdrant -n qdrant-vector -f values.yaml
```

---

## 🛡️ GKE Config Required

### Node pool: `qdrant-vector`

- **Machine type:** `n2-standard-16` (for 1 pod per node w/ 8 cores)
- **Taint:** `service=qdrant:NoSchedule`
- **Autoscaling:** enabled (min: 1, max: 6)

```
gcloud container node-pools update qdrant-vector \
  --cluster your-cluster \
  --zone your-zone \
  --enable-autoscaling \
  --min-nodes 1 \
  --max-nodes 6
```

---

## 🌐 Internal LoadBalancer Setup

### Reserved IP (optional but recommended):

```
gcloud compute addresses create qdrant-internal-ip \
  --region your-region \
  --subnet your-subnet \
  --addresses 10.90.128.89 \
  --purpose=GCE_ENDPOINT \
  --network-tier=PREMIUM
```

---

## 🧪 Validation Commands

```
kubectl get pods -n qdrant-vector -o wide
kubectl get svc -n qdrant-vector
kubectl describe node <node-name>  # check taints and allocatable resources
```

---

## 📦 Notes & Lessons Learned

| Topic                  | Outcome                                                                 |
|------------------------|-------------------------------------------------------------------------|
| Helm upgrade behavior  | Modifying service config (e.g., annotations) can recreate the LB & IP   |
| Static IPs             | Must reserve via GCP or GKE will assign new IP on redeploy              |
| Pod scheduling         | Taints + nodeSelector must be aligned to ensure pods stay on right pool |
| Autoscaler             | Needs enough headroom for high CPU pods (8-core per pod)                |
| StorageClass           | Must match what GKE supports (`standard`, `premium-rwo`, etc.)          |

---
