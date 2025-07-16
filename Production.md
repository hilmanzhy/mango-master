# Mango – Production-Ready Deployment on Kubernetes (via Minikube)

## Step 1 – Build Docker Images

Build image Django & Celery worker:

```bash
docker build -t mango-web .
docker build -f docker/worker.Dockerfile -t mango-worker .
```

```bash
minikube start --driver=docker
```

```bash
minikube addons enable ingress
```

```bash
minikube image load mango-web
minikube image load mango-worker
```

```bash
kubectl apply -f k8s/
```
Add to /etc/hosts

```
127.0.0.1 mango.local
```

```bash
minikube tunnel
```

```
http://mango.local
```

```bash
kubectl get pods
kubectl get svc
kubectl get ingress
```

```bash
kubectl logs deploy/mango-web
kubectl logs deploy/mango-worker
```