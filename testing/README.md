# Git-wtsm Docker Testing Infrastructure

Comprehensive testing environment for git-wtsm using Docker containers with isolated, automated testing.

## 🏗️ Architecture

### Multi-Stage Docker Build
- **Base stage**: System dependencies (Git, Python, Alpine Linux)
- **Setup stage**: Pre-created test repositories with submodule hierarchies (cached)
- **Test stage**: Copy git-wtsm script (rebuilt on changes for fast iteration)

### Test Repository Hierarchy
```
test-repos/
├── Level 1 (Superrepositories)
│   ├── main-repo → lib/utils + vendor/framework
│   └── lib-utils (standalone)
├── Level 2 (Middle-level with submodules)  
│   ├── vendor-framework → plugins
│   └── plugins-core → themes/default + auth
└── Level 3 (Leaf repositories)
    ├── theme-default (CSS files)
    └── plugin-auth (Python auth module)
```

### Test Scenarios
- `scenarios/clean-main-repo`: Fresh clone, no submodules initialized
- `scenarios/dirty-main-repo`: Has uncommitted changes  
- `scenarios/initialized-main-repo`: All submodules initialized recursively
- `scenarios/feature-branch-repo`: On feature branch with changes

## 🚀 Quick Start

### Build Testing Image
```bash
./docker-build.sh
```

### Run All Tests
```bash
./docker-test.sh
```

### Run Specific Test
```bash
./docker-test.sh --test git-wtsm-test-01
# or
docker run --rm git-wtsm-testing --test git-wtsm-test-01
```

### Interactive Testing Shell
```bash
./docker-test.sh --interactive
# or  
docker run --rm -it git-wtsm-testing bash
```

## 📋 Available Tests

| Test Script | Purpose | Coverage |
|-------------|---------|----------|
| `git-wtsm-test-01.py` | Basic functionality | help, status, add, remove, list |
| `git-wtsm-test-02.py` | Submodule initialization | Automatic init, recursive submodules |
| `git-wtsm-test-03.py` | Worktree list features | --verbose, --porcelain, submodule status |
| `git-wtsm-test-04.py` | Edge cases & errors | Error handling, safety checks |

## 🔧 Advanced Usage

### Build and Test in One Command
```bash
./docker-test.sh --build
```

### List Available Tests
```bash
./docker-test.sh --list
```

### Show Environment Information
```bash
./docker-test.sh --env
```

### Run Single Test Container
```bash
# Basic functionality tests
docker run --rm git-wtsm-testing git-wtsm-test-01.py

# Submodule tests
docker run --rm git-wtsm-testing git-wtsm-test-02.py
```

## 🐳 Docker Commands Reference

### Manual Docker Operations
```bash
# Build image manually
docker build -t git-wtsm-testing .

# Run all tests
docker run --rm git-wtsm-testing

# Run with specific arguments
docker run --rm git-wtsm-testing --test git-wtsm-test-03 

# Interactive debugging
docker run --rm -it git-wtsm-testing bash

# Check image size
docker images git-wtsm-testing
```

### Container Cleanup
```bash
# Remove all test containers
docker container prune

# Remove test image
docker rmi git-wtsm-testing
```

## 📁 Directory Structure

```
testing/
├── Dockerfile                    # Multi-stage build definition
├── .dockerignore                 # Build context exclusions
├── docker-build.sh              # Image build script
├── docker-test.sh               # Test execution script  
├── requirements-test.txt         # Python dependencies
├── setup/
│   ├── setup-test-repos.py      # Creates test repo hierarchy
│   └── repo-templates/          # Future: repo templates
└── tests/
    ├── git-wtsm-test-01.py      # Basic functionality tests
    ├── git-wtsm-test-02.py      # Submodule initialization tests
    ├── git-wtsm-test-03.py      # Worktree list tests
    ├── git-wtsm-test-04.py      # Edge cases & error handling
    └── test-runner.py            # Test orchestrator
```

## 🔍 Test Development

### Adding New Tests
1. Create new test script in `tests/` directory
2. Follow naming convention: `git-wtsm-test-XX.py`
3. Use unittest framework with colored output
4. Add script to `test-runner.py` test list

### Test Script Template
```python
#!/usr/bin/env python3
import unittest
from termcolor import colored

class MyNewTests(unittest.TestCase):
    def test_something(self):
        # Test implementation
        pass

def main():
    print(colored("Running My New Tests", "cyan", attrs=["bold"]))
    suite = unittest.TestLoader().loadTestsFromTestCase(MyNewTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    exit(main())
```

## 🚦 CI/CD Integration

### GitHub Actions (Future)
The Docker testing infrastructure is designed for easy GitHub Actions integration:

```yaml
name: Test git-wtsm
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and test
        run: |
          cd testing
          ./docker-build.sh
          ./docker-test.sh
```

### Local CI Simulation
```bash
# Simulate CI workflow locally
git clean -fdx testing/
./testing/docker-build.sh  
./testing/docker-test.sh
```

## 🐛 Troubleshooting

### Common Issues

**Image build fails:**
```bash
# Check Docker daemon
docker info

# Build with verbose output
docker build --no-cache -t git-wtsm-testing .
```

**Tests fail to run:**
```bash
# Check image exists
docker images git-wtsm-testing

# Run environment check
docker run --rm git-wtsm-testing --env

# Interactive debugging
docker run --rm -it git-wtsm-testing bash
```

**Submodule tests fail:**
```bash
# Check test repo setup
docker run --rm git-wtsm-testing bash -c "ls -la /home/testuser/test-repos/"

# Manual submodule check
docker run --rm git-wtsm-testing bash -c "cd /home/testuser/test-repos/scenarios/clean-main-repo && git submodule status"
```

## 📊 Performance

### Caching Strategy
- **Base dependencies**: Cached across builds
- **Test repositories**: Cached across builds (only rebuilt if setup scripts change)
- **git-wtsm script**: Rebuilt on every change (fast layer)

### Typical Build Times
- **Cold build**: ~2-3 minutes (full image + test repos)
- **Warm build**: ~10-20 seconds (just git-wtsm script copy)
- **Test execution**: ~30-60 seconds (all tests)

This testing infrastructure provides comprehensive, isolated, and automated testing for git-wtsm with fast iteration cycles and clear reporting.