#!/bin/bash
# Docker test runner script for git-wtsm

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE_NAME="git-wtsm-testing"
IMAGE_TAG="latest"

# Parse command line arguments
DOCKER_ARGS=""
TEST_ARGS=""
INTERACTIVE=false
BUILD_FIRST=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --build|-b)
            BUILD_FIRST=true
            shift
            ;;
        --interactive|-i)
            INTERACTIVE=true
            shift
            ;;
        --test|-t)
            TEST_ARGS="--test $2"
            shift 2
            ;;
        --list|-l)
            TEST_ARGS="--list"
            shift
            ;;
        --env|-e)
            TEST_ARGS="--env"
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --build, -b         Build image before running tests"
            echo "  --interactive, -i   Run interactive shell instead of tests"
            echo "  --test, -t <name>   Run specific test (e.g., git-wtsm-test-01)"
            echo "  --list, -l          List available tests"
            echo "  --env, -e           Show environment information"
            echo "  --help, -h          Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests"
            echo "  $0 --build           # Build image and run all tests"
            echo "  $0 -t test-01        # Run specific test"
            echo "  $0 --interactive     # Interactive shell"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build image if requested
if [ "$BUILD_FIRST" = true ]; then
    echo "🔨 Building Docker image first..."
    "$SCRIPT_DIR/docker-build.sh"
    echo ""
fi

# Check if image exists
if ! docker images "$IMAGE_NAME:$IMAGE_TAG" --format "{{.Repository}}" | grep -q "$IMAGE_NAME"; then
    echo "❌ Docker image $IMAGE_NAME:$IMAGE_TAG not found."
    echo "Build it first with: ./docker-build.sh"
    exit 1
fi

echo "🧪 Running git-wtsm tests in Docker..."

if [ "$INTERACTIVE" = true ]; then
    echo "🔧 Starting interactive shell..."
    docker run --rm -it "$IMAGE_NAME:$IMAGE_TAG" bash
else
    # Run tests
    echo "📋 Test arguments: $TEST_ARGS"
    
    # Use --rm to automatically clean up container
    # Use -t to allocate pseudo-TTY for colored output
    docker run --rm -t "$IMAGE_NAME:$IMAGE_TAG" $TEST_ARGS
    
    # Capture exit code
    exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo "🎉 All tests completed successfully!"
    else
        echo "💥 Some tests failed (exit code: $exit_code)"
    fi
    
    exit $exit_code
fi