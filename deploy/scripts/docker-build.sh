#!/bin/bash
###############################################
# AI Employee Vault - Docker Build Script
# Usage: ./deploy/scripts/docker-build.sh [tag]
###############################################

set -euo pipefail

TAG="${1:-latest}"
IMAGE_NAME="ai-employee-vault"

echo "Building ${IMAGE_NAME}:${TAG}..."

# Build the image
docker build \
    --tag "${IMAGE_NAME}:${TAG}" \
    --tag "${IMAGE_NAME}:latest" \
    --label "build.date=$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --label "build.version=${TAG}" \
    .

echo ""
echo "Build complete: ${IMAGE_NAME}:${TAG}"
echo "Image size: $(docker image inspect ${IMAGE_NAME}:${TAG} --format='{{.Size}}' | numfmt --to=iec 2>/dev/null || docker image inspect ${IMAGE_NAME}:${TAG} --format='{{.Size}}')"

# Optionally run tests against the built image
echo ""
echo "Running container health check..."
CONTAINER_ID=$(docker run -d --rm -p 8081:8080 "${IMAGE_NAME}:${TAG}")
sleep 5

STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8081/health 2>/dev/null || echo "000")
if [[ "${STATUS}" == "200" ]]; then
    echo "Container health check: PASSED"
else
    echo "Container health check: FAILED (status: ${STATUS})"
fi

docker stop "${CONTAINER_ID}" 2>/dev/null || true
echo "Done."
