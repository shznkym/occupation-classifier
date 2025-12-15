#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Occupation Classifier - Kubernetes Deploy${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check cluster connectivity
echo -e "${YELLOW}Checking Kubernetes cluster connectivity...${NC}"
if ! kubectl cluster-info &> /dev/null; then
    echo -e "${RED}Error: Cannot connect to Kubernetes cluster${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Connected to Kubernetes cluster${NC}"
echo ""

# Prompt for Gemini API Key
echo -e "${YELLOW}Enter your Gemini API Key:${NC}"
read -s GEMINI_API_KEY
echo ""

if [ -z "$GEMINI_API_KEY" ]; then
    echo -e "${RED}Error: Gemini API Key cannot be empty${NC}"
    exit 1
fi

# Base64 encode the API key
ENCODED_API_KEY=$(echo -n "$GEMINI_API_KEY" | base64)

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${YELLOW}Deploying to Kubernetes...${NC}"
echo ""

# Step 1: Create namespace
echo -e "${YELLOW}1. Creating namespace...${NC}"
kubectl apply -f "${SCRIPT_DIR}/namespace.yaml"
echo -e "${GREEN}✓ Namespace created${NC}"
echo ""

# Step 2: Create secret
echo -e "${YELLOW}2. Creating secret...${NC}"
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: gemini-secret
  namespace: occupation-classifier
type: Opaque
data:
  api-key: ${ENCODED_API_KEY}
EOF
echo -e "${GREEN}✓ Secret created${NC}"
echo ""

# Step 3: Deploy backend
echo -e "${YELLOW}3. Deploying backend...${NC}"
kubectl apply -f "${SCRIPT_DIR}/backend-deployment.yaml"
kubectl apply -f "${SCRIPT_DIR}/backend-service.yaml"
echo -e "${GREEN}✓ Backend deployed${NC}"
echo ""

# Step 4: Deploy frontend
echo -e "${YELLOW}4. Deploying frontend...${NC}"
kubectl apply -f "${SCRIPT_DIR}/frontend-deployment.yaml"
kubectl apply -f "${SCRIPT_DIR}/frontend-service.yaml"
echo -e "${GREEN}✓ Frontend deployed${NC}"
echo ""

# Step 5: Deploy ingress (optional)
if [ -f "${SCRIPT_DIR}/ingress.yaml" ]; then
    echo -e "${YELLOW}5. Would you like to deploy Ingress? (y/N)${NC}"
    read -r DEPLOY_INGRESS
    if [[ "$DEPLOY_INGRESS" =~ ^[Yy]$ ]]; then
        kubectl apply -f "${SCRIPT_DIR}/ingress.yaml"
        echo -e "${GREEN}✓ Ingress deployed${NC}"
    else
        echo -e "${YELLOW}⚠ Skipping Ingress deployment${NC}"
    fi
    echo ""
fi

# Wait for deployments to be ready
echo -e "${YELLOW}Waiting for deployments to be ready...${NC}"
kubectl wait --for=condition=available --timeout=300s \
    deployment/backend deployment/frontend \
    -n occupation-classifier

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Show deployment status
echo -e "${YELLOW}Deployment Status:${NC}"
kubectl get pods -n occupation-classifier
echo ""

echo -e "${YELLOW}Services:${NC}"
kubectl get svc -n occupation-classifier
echo ""

# Provide access instructions
echo -e "${GREEN}Access Instructions:${NC}"
echo ""
echo -e "${YELLOW}1. Port-forward to access frontend:${NC}"
echo "   kubectl port-forward -n occupation-classifier svc/frontend-service 3000:3000"
echo "   Then open: http://localhost:3000"
echo ""
echo -e "${YELLOW}2. Port-forward to access backend API:${NC}"
echo "   kubectl port-forward -n occupation-classifier svc/backend-service 8000:8000"
echo "   Then open: http://localhost:8000/docs"
echo ""
echo -e "${YELLOW}3. Check logs:${NC}"
echo "   kubectl logs -n occupation-classifier -l component=backend -f"
echo "   kubectl logs -n occupation-classifier -l component=frontend -f"
echo ""
