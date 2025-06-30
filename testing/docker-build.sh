#!/bin/bash
# Docker build script for git-wtsm testing environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="git-wtsm-testing"
IMAGE_TAG="latest"

echo "🐳 Building git-wtsm testing Docker image..."
echo "Project root: $PROJECT_ROOT"
echo "Build context: $SCRIPT_DIR"

# Change to testing directory for build context
cd "$SCRIPT_DIR"

# Build the Docker image
echo "Building image: $IMAGE_NAME:$IMAGE_TAG"
docker build \
    --tag "$IMAGE_NAME:$IMAGE_TAG" \
    --file Dockerfile \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg VCS_REF="$(cd "$PROJECT_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo 'unknown')" \
    .

echo "✅ Docker image built successfully: $IMAGE_NAME:$IMAGE_TAG"

# Show image information
echo "📊 Image information:"
docker images "$IMAGE_NAME:$IMAGE_TAG" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
echo "🚀 Usage examples:"
echo "  # Run all tests:"
echo "  ./docker-test.sh"
echo ""
echo "  # Run specific test:"
echo "  docker run --rm $IMAGE_NAME:$IMAGE_TAG --test git-wtsm-test-01"
echo ""
echo "  # Interactive shell:"
echo "  docker run --rm -it $IMAGE_NAME:$IMAGE_TAG bash"
echo ""
echo "  # List available tests:"
echo "  docker run --rm $IMAGE_NAME:$IMAGE_TAG --list"