# Axiom API

A hyper-rational debate API built with FastAPI and LangChain, powered by Google Gemini.

## Features

- FastAPI with modern async/await patterns
- LangChain integration with Google Gemini
- Industry-standard project structure
- Kubernetes-ready deployment
- Health checks and monitoring
- Type-safe configuration with Pydantic

## Local Development

### Prerequisites

- Python 3.13+
- UV package manager (or pip)

### Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   # Or with UV:
   uv pip install -e .
   ```

4. Create a `.env` file:
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

5. Run the application:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.

## Deployment on Civo

### Prerequisites

- Civo account ([Sign up here](https://www.civo.com/))
- Civo CLI installed (`civo` command)
- Docker installed (for building images)
- kubectl configured for your Civo cluster

### Step 1: Build Docker Image

```bash
# Build the image
docker build -t axiom-api:latest .

# Tag for your container registry (if using one)
# docker tag axiom-api:latest your-registry/axiom-api:latest
# docker push your-registry/axiom-api:latest
```

### Step 2: Create Civo Kubernetes Cluster

```bash
# Install Civo CLI if not already installed
# See: https://www.civo.com/docs/cli

# Login to Civo
civo apikey save YOUR_API_KEY your-key-name

# Create a Kubernetes cluster
civo kubernetes create axiom-cluster --size g4s.kube.medium --nodes 2 --region NYC1

# Wait for cluster to be ready (usually ~90 seconds)
civo kubernetes config axiom-cluster --save

# Verify connection
kubectl get nodes
```

### Step 3: Create Kubernetes Secrets

```bash
# Create secret for Google API key
kubectl create secret generic axiom-secrets \
  --from-literal=google-api-key='YOUR_GOOGLE_API_KEY'

# Verify secret was created
kubectl get secret axiom-secrets
```

### Step 4: Deploy to Kubernetes

```bash
# Apply ConfigMap
kubectl apply -f k8s/configmap.yaml

# Apply Deployment and Service
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Apply Ingress (optional, only if using ingress)
# First, check your cluster's ingress class: kubectl get ingressclass
# Then update k8s/ingress.yaml with the correct ingressClassName
kubectl apply -f k8s/ingress.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services
```

**Note:** If you see errors about `kustomization.yaml`, that's normal - it's only used with `kubectl apply -k` (kustomize). Use individual `kubectl apply -f` commands instead.

### Step 5: Expose the API (Optional)

#### Option A: Using Civo Load Balancer

```bash
# Update service to use LoadBalancer type
kubectl patch service axiom-api-service -p '{"spec":{"type":"LoadBalancer"}}'

# Get external IP
kubectl get service axiom-api-service
```

#### Option B: Using Ingress

1. Update `k8s/ingress.yaml` with your domain
2. Apply ingress:
   ```bash
   kubectl apply -f k8s/ingress.yaml
   ```

### Step 6: Verify Deployment

```bash
# Check pod logs
kubectl logs -l app=axiom-api

# Test health endpoint
kubectl port-forward service/axiom-api-service 8000:80
curl http://localhost:8000/health
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|----------|----------|
| `GOOGLE_API_KEY` | Google API key for Gemini | - | Yes |
| `PORT` | Server port | 8000 | No |
| `DEBUG` | Enable debug mode | false | No |
| `ENVIRONMENT` | Environment (development/production) | production | No |
| `LLM_MODEL` | LLM model name | gemini-3-pro-preview | No |
| `CORS_ORIGINS` | Allowed CORS origins (comma-separated) | * | No |

### Kubernetes Configuration

Edit `k8s/configmap.yaml` for non-sensitive configuration and `k8s/secret.yaml.template` for secrets.

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check (liveness probe)
- `GET /ready` - Readiness check (readiness probe)
- `POST /api/v1/debate` - Submit an argument for debate
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation

## Project Structure

```
axiom/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   └── routes.py      # API routes
│   │   └── deps.py            # API dependencies
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── dependencies.py    # Shared dependencies
│   │   └── logging.py         # Logging setup
│   ├── services/
│   │   └── llm_service.py    # LLM service
│   ├── schemas/
│   │   └── debate.py          # Pydantic models
│   ├── prompts/
│   │   └── system_prompt.md  # System prompt
│   └── main.py               # FastAPI app
├── k8s/                      # Kubernetes manifests
├── Dockerfile                # Production Dockerfile
├── pyproject.toml            # Dependencies
└── main.py                  # Entry point
```

## Monitoring

### Health Checks

- **Liveness Probe**: `/health` - Checks if the app is running
- **Readiness Probe**: `/ready` - Checks if the app is ready to serve traffic

### Logs

View logs in Kubernetes:
```bash
kubectl logs -l app=axiom-api -f
```

## Scaling

Scale the deployment:
```bash
kubectl scale deployment axiom-api --replicas=3
```

Or update `k8s/deployment.yaml` and reapply.

## Troubleshooting

### Pods not starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
```

### API key issues

```bash
# Verify secret
kubectl get secret axiom-secrets -o yaml

# Update secret
kubectl create secret generic axiom-secrets \
  --from-literal=google-api-key='NEW_KEY' \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods
kubectl rollout restart deployment axiom-api
```

## License

[Your License Here]

