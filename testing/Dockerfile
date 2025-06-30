# Multi-stage Dockerfile for git-wtsm testing
# Optimized for caching - git-wtsm script copied last

FROM python:3.11-alpine AS base
LABEL description="git-wtsm testing environment"

# Install system dependencies
RUN apk add --no-cache \
    git \
    bash

# Install Python testing dependencies
COPY requirements-test.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements-test.txt

# Create test user and workspace
RUN addgroup -g 1000 testuser && \
    adduser -u 1000 -G testuser -D testuser
USER testuser
WORKDIR /home/testuser

# Configure git for testuser
RUN git config --global user.name "Test User" \
    && git config --global user.email "test@example.com" \
    && git config --global init.defaultBranch main

# Setup stage - Create test repositories (cached)
FROM base AS setup
COPY --chown=testuser:testuser setup/ /home/testuser/setup/
RUN cd /home/testuser/setup && python setup-test-repos.py

# Test stage - Copy git-wtsm script (rebuilt on changes)
FROM setup AS test
COPY --chown=testuser:testuser tests/ /home/testuser/tests/
COPY --chown=testuser:testuser git-wtsm /usr/local/bin/git-wtsm
RUN chmod +x /usr/local/bin/git-wtsm

# Set default command to run test orchestrator
ENTRYPOINT ["python", "/home/testuser/tests/test-runner.py"]
CMD ["--all"]