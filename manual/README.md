---

# 📘 Qdrant on GKE – Manual Kubernetes Deployment (No Helm)

This document outlines a raw, no-Helm deployment of [Qdrant](https://qdrant.tech) on **Google Kubernetes Engine (GKE)** using pure YAML manifests.

> This is the approach we switched to after Helm proved too abstract for fine-grained control.

---

## 📂 Files Used

Single file deployment: `qdrant-full.yaml`

Contents:
- Namespace `qdrant-vector`
- PVC (50Gi SSD)
- 4-replica Deployment (8 CPU, 16Gi RAM each)
- Internal LoadBalancer with static IP
- Node pool targeting and taint toleration

---

## 💾 Storage Prerequisites

You need to know which **StorageClass** is available in your GKE cluster. Run:

```
kubectl get storageclass
```

Choose one of:
- `standard`
- `standard-rwo`
- `premium-rwo`
- `balanced-rwo`

> We used: `premium-rwo`

---

## 📡 Reserve Static Internal IP (Recommended)

Prevent IP flip-flops on redeploy:

```
gcloud compute addresses create qdrant-internal-ip \
  --region=YOUR_REGION \
  --subnet=YOUR_SUBNET \
  --addresses=10.90.128.89 \
  --purpose=GCE_ENDPOINT \
  --network-tier=PREMIUM
```

---

## 🔧 Final Manifest: `qdrant-full.yaml`

```yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: qdrant-vector
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: qdrant-storage
  namespace: qdrant-vector
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
  storageClassName: premium-rwo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: qdrant
  namespace: qdrant-vector
spec:
  replicas: 4
  selector:
    matchLabels:
      app: qdrant
  template:
    metadata:
      labels:
        app: qdrant
    spec:
      containers:
        - name: qdrant
          image: qdrant/qdrant:latest
          ports:
            - containerPort: 6333
            - containerPort: 6334
          resources:
            requests:
              cpu: "8"
              memory: "16Gi"
            limits:
              cpu: "8"
              memory: "16Gi"
          volumeMounts:
            - name: storage
              mountPath: /qdrant/storage
      volumes:
        - name: storage
          persistentVolumeClaim:
            claimName: qdrant-storage
      nodeSelector:
        cloud.google.com/gke-nodepool: qdrant-vector
      tolerations:
        - key: service
          value: qdrant
          effect: NoSchedule
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
---
apiVersion: v1
kind: Service
metadata:
  name: qdrant
  namespace: qdrant-vector
  annotations:
    cloud.google.com/load-balancer-type: "Internal"
spec:
  type: LoadBalancer
  selector:
    app: qdrant
  ports:
    - name: http
      port: 80
      targetPort: 6333
    - name: grpc
      port: 6334
      targetPort: 6334
```

---

## 🚀 Deploy All Resources

```
kubectl apply -f qdrant-full.yaml
```

---

## 🔍 Validation

```
kubectl get all -n qdrant-vector -o wide
kubectl describe svc qdrant -n qdrant-vector
kubectl describe pod <qdrant-pod> -n qdrant-vector
```

---

## 🧠 GKE Node Pool Requirements

- **Node Pool Name:** `qdrant-vector`
- **Taint (optional):** `service=qdrant:NoSchedule`
- **Machine Type:** `n2-standard-16` or larger (to fit 8-core pods)
- **Autoscaling:** recommended 4–6 nodes

```
gcloud container node-pools update qdrant-vector \
  --cluster=<cluster-name> \
  --enable-autoscaling \
  --min-nodes=1 \
  --max-nodes=6
```

---

## 📝 Notes

| Area               | Description                                                  |
|--------------------|--------------------------------------------------------------|
| Static IP          | Avoids IP churn on service updates                           |
| PVC                | Mounted at `/qdrant/storage`                                 |
| Scaling            | Change `replicas:` in Deployment                             |
| Debug Scheduling   | `kubectl describe pod ...` to check why pods might be stuck  |
| Node Pool Targeting| Enforced via `nodeSelector + tolerations`                    |
| StorageClass       | Must exist, else PVC will remain in "Pending" state          |

---
