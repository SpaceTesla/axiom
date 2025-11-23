# Quick Deployment Guide for Civo

## Prerequisites Checklist

- [ ] Civo account created
- [ ] Civo CLI installed (`civo` command)
- [ ] Docker installed
- [ ] kubectl installed
- [ ] Google API key ready
- [ ] GitHub account (for GHCR) or Docker Hub account

## Complete Deployment Workflow (Quick Reference)

**This is the exact sequence we used to deploy successfully:**

```bash
# 1. Build and push image to GHCR
docker build -t axiom-api:latest .
docker tag axiom-api:latest ghcr.io/spacetesla/axiom-api:latest
docker push ghcr.io/spacetesla/axiom-api:latest

# 2. Connect to Civo cluster (if not already connected)
civo kubernetes config axiom-cluster --save

# 3. Create secrets
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=spacetesla \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL

kubectl create secret generic axiom-secrets \
  --from-literal=google-api-key='YOUR_GOOGLE_API_KEY'

# 4. Deploy
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# 5. Expose with LoadBalancer
kubectl patch service axiom-api-service -p '{"spec":{"type":"LoadBalancer"}}'

# 6. Get your public IP
kubectl get service axiom-api-service
# Access your API at: http://EXTERNAL-IP
```

## Detailed Steps

### 1. Build and Push Image to Registry (REQUIRED)

**The image MUST be pushed to a container registry that your cluster can access.**

#### Option A: Docker Hub (Easiest)

```bash
# Build
docker build -t axiom-api:latest .

# Tag with your Docker Hub username
docker tag axiom-api:latest YOUR_DOCKERHUB_USERNAME/axiom-api:latest

# Login to Docker Hub
docker login

# Push to Docker Hub
docker push YOUR_DOCKERHUB_USERNAME/axiom-api:latest

# Update deployment.yaml to use: YOUR_DOCKERHUB_USERNAME/axiom-api:latest
```

#### Option B: GitHub Container Registry

```bash
# Build
docker build -t axiom-api:latest .

# Tag for GHCR
docker tag axiom-api:latest ghcr.io/YOUR_GITHUB_USERNAME/axiom-api:latest

# Login to GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin

# Push
docker push ghcr.io/YOUR_GITHUB_USERNAME/axiom-api:latest

# Update deployment.yaml to use: ghcr.io/YOUR_GITHUB_USERNAME/axiom-api:latest
```

#### Option C: Other Registries (AWS ECR, Google GCR, etc.)

Follow your registry's specific push instructions, then update `k8s/deployment.yaml` with the full image path.

### 2. Create Civo Cluster

```bash
# Login to Civo
civo apikey save YOUR_API_KEY my-key

# Create cluster (adjust size and region as needed)
civo kubernetes create axiom-cluster \
  --size g4s.kube.medium \
  --nodes 2 \
  --region NYC1

# Get kubeconfig
civo kubernetes config axiom-cluster --save
```

### 3. Create Secrets

**Step 1: Create GHCR Image Pull Secret (Required for private images)**

If using GitHub Container Registry with a private image, create a secret for authentication:

```bash
# Create GitHub Personal Access Token with 'read:packages' permission
# Go to: https://github.com/settings/tokens

# Create the secret
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL
```

**Step 2: Create Google API Key Secret**

```bash
kubectl create secret generic axiom-secrets \
  --from-literal=google-api-key='YOUR_GOOGLE_API_KEY'
```

**Note:** If secrets already exist, you can update them using:

```bash
kubectl create secret docker-registry ghcr-secret \
  --docker-server=ghcr.io \
  --docker-username=YOUR_GITHUB_USERNAME \
  --docker-password=YOUR_GITHUB_TOKEN \
  --docker-email=YOUR_EMAIL \
  --dry-run=client -o yaml | kubectl apply -f -

kubectl create secret generic axiom-secrets \
  --from-literal=google-api-key='YOUR_GOOGLE_API_KEY' \
  --dry-run=client -o yaml | kubectl apply -f -
```

### 4. Deploy

**Option A: Apply individual manifests (Recommended)**

```bash
# Apply all manifests (excludes kustomization.yaml)
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
# Note: ingress.yaml is optional - we use LoadBalancer instead
```

**Verify pods are starting:**

```bash
kubectl get pods -l app=axiom-api
# Wait until you see STATUS: Running and READY: 1/1
```

**Option B: Use Kustomize**

```bash
# If deployment already exists and you get selector errors, delete it first:
kubectl delete deployment axiom-api

# Then apply using kustomize
kubectl apply -k k8s/
```

**Note:**

- `kustomization.yaml` is only used with `kubectl apply -k` (kustomize). Don't apply it directly with `kubectl apply -f`.
- If you see "selector is immutable" errors, the deployment already exists with a different selector. Delete it first, then reapply.

### 5. Expose Service with LoadBalancer

**The service is created as ClusterIP by default. Change it to LoadBalancer to get a public IP:**

```bash
# Change service type to LoadBalancer
kubectl patch service axiom-api-service -p '{"spec":{"type":"LoadBalancer"}}'

# Wait a few seconds, then get the external IP
kubectl get service axiom-api-service

# The EXTERNAL-IP column will show your public IP (may take 1-2 minutes)
# Example output:
# NAME                TYPE           CLUSTER-IP     EXTERNAL-IP    PORT(S)
# axiom-api-service   LoadBalancer   10.43.75.150   212.2.247.40   80:30422/TCP
```

**Your API will be accessible at:** `http://YOUR_EXTERNAL_IP`

**Alternative: Using Ingress (Optional)**

If you prefer using Ingress instead of LoadBalancer:

1. Update `k8s/ingress.yaml` with your domain
2. Check your cluster's ingress class: `kubectl get ingressclass`
3. Update `k8s/ingress.yaml` with the correct `ingressClassName`
4. Apply: `kubectl apply -f k8s/ingress.yaml`

## Verify Deployment

```bash
# Check pods are running
kubectl get pods -l app=axiom-api
# Should show STATUS: Running and READY: 1/1

# Check service and get external IP
kubectl get service axiom-api-service
# Note the EXTERNAL-IP address

# View logs (optional)
kubectl logs -l app=axiom-api -f

# Test the API endpoints
# Replace EXTERNAL_IP with your actual external IP from above
curl http://EXTERNAL_IP/health
curl http://EXTERNAL_IP/
curl http://EXTERNAL_IP/docs  # Open in browser for Swagger UI
```

**Your API endpoints:**

- **Root:** `http://YOUR_EXTERNAL_IP/`
- **Health Check:** `http://YOUR_EXTERNAL_IP/health`
- **API Docs:** `http://YOUR_EXTERNAL_IP/docs`
- **Debate Endpoint:** `http://YOUR_EXTERNAL_IP/api/v1/debate` (POST)

**Test the debate endpoint:**

```bash
curl -X POST http://YOUR_EXTERNAL_IP/api/v1/debate \
  -H "Content-Type: application/json" \
  -d '{"message": "Your argument here"}'
```

## Update Deployment

**When you make code changes and want to redeploy:**

```bash
# 1. Build new image
docker build -t axiom-api:latest .

# 2. Tag and push to registry (replace with your registry)
docker tag axiom-api:latest ghcr.io/YOUR_USERNAME/axiom-api:latest
docker push ghcr.io/YOUR_USERNAME/axiom-api:latest

# 3. Update deployment with new image
kubectl set image deployment/axiom-api axiom-api=ghcr.io/YOUR_USERNAME/axiom-api:latest

# 4. Watch rollout status
kubectl rollout status deployment/axiom-api

# 5. Verify new pods are running
kubectl get pods -l app=axiom-api
```

**Or restart deployment (if no code changes):**

```bash
kubectl rollout restart deployment/axiom-api
```

## Troubleshooting

### Pods not starting

```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

### Secret issues

```bash
# Verify secret exists
kubectl get secret axiom-secrets

# Update secret
kubectl create secret generic axiom-secrets \
  --from-literal=google-api-key='NEW_KEY' \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart deployment
kubectl rollout restart deployment axiom-api
```

### Image pull errors

**Error: "unauthorized" or "pull access denied"**

- Your image is private and needs authentication
- Create the GHCR secret (see Step 3 above)
- Verify secret exists: `kubectl get secret ghcr-secret`

**Error: "ImagePullBackOff"**

- Check image name in `k8s/deployment.yaml` matches your registry
- Verify image exists: `docker pull YOUR_IMAGE_NAME`
- Ensure imagePullSecrets is configured in deployment.yaml

**Error: "repository does not exist"**

- Verify you pushed the image to the registry
- Check the image path is correct
- For GHCR: Ensure image is `ghcr.io/USERNAME/axiom-api:latest`

## Scaling

```bash
# Scale manually
kubectl scale deployment axiom-api --replicas=3

# Or enable HPA (Horizontal Pod Autoscaler)
kubectl autoscale deployment axiom-api --cpu-percent=70 --min=2 --max=10
```

## Cleanup

**To remove the deployment (but keep cluster):**

```bash
kubectl delete -f k8s/configmap.yaml
kubectl delete -f k8s/deployment.yaml
kubectl delete -f k8s/service.yaml
kubectl delete secret axiom-secrets
kubectl delete secret ghcr-secret
```

**To delete the entire Civo cluster:**

```bash
civo kubernetes delete axiom-cluster
```

**Note:** Deleting the cluster will remove all resources and stop billing.
