#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Occupation Classifier - Cleanup${NC}"
echo -e "${YELLOW}========================================${NC}"
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}Error: kubectl is not installed${NC}"
    exit 1
fi

# Check if namespace exists
if ! kubectl get namespace occupation-classifier &> /dev/null; then
    echo -e "${YELLOW}Namespace 'occupation-classifier' does not exist${NC}"
    exit 0
fi

echo -e "${YELLOW}This will delete all resources in the 'occupation-classifier' namespace.${NC}"
echo -e "${RED}This action cannot be undone!${NC}"
echo ""
echo -e "${YELLOW}Are you sure you want to continue? (yes/no)${NC}"
read -r CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo -e "${GREEN}Cleanup cancelled${NC}"
    exit 0
fi

echo ""
echo -e "${YELLOW}Deleting resources in occupation-classifier namespace...${NC}"

# Delete all resources in the namespace
kubectl delete all --all -n occupation-classifier

# Delete secrets
kubectl delete secret --all -n occupation-classifier

# Delete ingress if exists
kubectl delete ingress --all -n occupation-classifier 2>/dev/null || true

# Delete the namespace
echo -e "${YELLOW}Deleting namespace...${NC}"
kubectl delete namespace occupation-classifier

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Cleanup completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
