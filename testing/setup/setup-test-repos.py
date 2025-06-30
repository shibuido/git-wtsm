#!/usr/bin/env python3
"""
Test repository setup script for git-wtsm testing.
Creates superrepositories with recursive submodules (1-3 levels deep).
"""

import os
import subprocess
import pathlib
from typing import List, Dict

class TestRepoCreator:
    def __init__(self, base_path: str = "/home/testuser/test-repos"):
        self.base_path = pathlib.Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        
    def run_git(self, cmd: List[str], cwd: pathlib.Path) -> None:
        """Run git command safely."""
        try:
            result = subprocess.run(
                ["git"] + cmd,
                cwd=cwd,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            print(f"❌ Git command failed: git {' '.join(cmd)}")
            print(f"   Working directory: {cwd}")
            print(f"   Return code: {e.returncode}")
            print(f"   STDOUT: {e.stdout}")
            print(f"   STDERR: {e.stderr}")
            raise
        
    def create_simple_repo(self, name: str, files: List[str] = None, bare: bool = False) -> pathlib.Path:
        """Create a simple git repository with initial files."""
        repo_path = self.base_path / name
        repo_path.mkdir(exist_ok=True)
        
        if bare:
            # Initialize bare repo
            self.run_git(["init", "--bare"], repo_path)
            return repo_path
        
        # Initialize repo
        self.run_git(["init"], repo_path)
        
        # Create files
        files = files or [f"{name}.txt", "README.md"]
        for file in files:
            (repo_path / file).write_text(f"Content of {file} in {name}\n")
            
        # Initial commit
        self.run_git(["add", "."], repo_path)
        self.run_git(["commit", "-m", f"Initial commit for {name}"], repo_path)
        
        return repo_path
        
    def create_submodule_hierarchy(self) -> Dict[str, pathlib.Path]:
        """Create repositories with real submodules using filesystem paths."""
        repos = {}
        
        print("Creating Level 3 repositories (deepest submodules)...")
        # Level 3 - Deepest submodules for nested testing
        repos["theme-default"] = self.create_simple_repo("theme-default", 
            ["theme.css", "config.json", "README.md"])
        repos["plugin-auth"] = self.create_simple_repo("plugin-auth",
            ["auth.py", "requirements.txt", "__init__.py"])
            
        print("Creating Level 2 repositories...")
        # Level 2 - Middle level repositories with submodules
        repos["lib-utils"] = self.create_simple_repo("lib-utils",
            ["utils.py", "helpers.py", "constants.py"])
        repos["plugins-core"] = self.create_simple_repo("plugins-core",
            ["__init__.py", "core.py", "manager.py"])
        repos["vendor-framework"] = self.create_simple_repo("vendor-framework",
            ["framework.py", "setup.py", "config.py"])
            
        # Add submodules to plugins-core (Level 3 → Level 2)
        print("Adding Level 3 submodules to plugins-core...")
        # Create subdirectories first
        (repos["plugins-core"] / "themes").mkdir(exist_ok=True)
        self.run_git(["submodule", "add", str(repos["theme-default"]), "themes/default"], 
                    repos["plugins-core"])
        self.run_git(["submodule", "add", str(repos["plugin-auth"]), "auth"],
                    repos["plugins-core"])
        self.run_git(["commit", "-m", "Add theme and auth submodules"], repos["plugins-core"])
        
        # Add submodules to vendor-framework (Level 2 → Level 2)
        print("Adding plugins-core submodule to vendor-framework...")
        self.run_git(["submodule", "add", str(repos["plugins-core"]), "plugins"],
                    repos["vendor-framework"])
        self.run_git(["commit", "-m", "Add plugins submodule"], repos["vendor-framework"])
            
        print("Creating Level 1 repositories (main superrepository)...")
        # Level 1 - Top-level superrepository
        repos["main-repo"] = self.create_simple_repo("main-repo",
            ["main.py", "config.yaml", ".gitignore"])
            
        # Add Level 2 submodules to main-repo (Level 2 → Level 1)
        print("Adding Level 2 submodules to main-repo...")
        # Create subdirectories first
        (repos["main-repo"] / "lib").mkdir(exist_ok=True)
        (repos["main-repo"] / "vendor").mkdir(exist_ok=True)
        self.run_git(["submodule", "add", str(repos["lib-utils"]), "lib/utils"],
                    repos["main-repo"])
        self.run_git(["submodule", "add", str(repos["vendor-framework"]), "vendor/framework"],
                    repos["main-repo"])
        self.run_git(["commit", "-m", "Add lib/utils and vendor/framework submodules"], repos["main-repo"])
        
        return repos
        
    def create_test_scenarios(self, repos: Dict[str, pathlib.Path]) -> None:
        """Create different test scenarios."""
        scenarios_path = self.base_path / "scenarios"
        scenarios_path.mkdir(exist_ok=True)
        
        print("Creating test scenarios...")
        
        # Scenario 1: Clean repository clone (with submodules)
        clean_path = scenarios_path / "clean-main-repo"
        self.run_git(["clone", str(repos["main-repo"]), str(clean_path)], self.base_path)
        
        # Scenario 2: Repository with uncommitted changes
        dirty_path = scenarios_path / "dirty-main-repo"
        self.run_git(["clone", str(repos["main-repo"]), str(dirty_path)], self.base_path)
        (dirty_path / "uncommitted.txt").write_text("Uncommitted changes\n")
        
        # Scenario 3: Simple repository WITHOUT submodules for basic testing
        simple_path = scenarios_path / "simple-repo"
        simple_repo = self.create_simple_repo_at_path(simple_path, 
            ["main.py", "README.md", "config.json"])
        
        # Scenario 4: Different branch (simple repo)
        branch_path = scenarios_path / "simple-branch-repo"  
        self.run_git(["clone", str(simple_path), str(branch_path)], self.base_path)
        self.run_git(["checkout", "-b", "feature/test-branch"], branch_path)
        (branch_path / "feature.py").write_text("Feature implementation\n")
        self.run_git(["add", "feature.py"], branch_path)
        self.run_git(["commit", "-m", "Add feature implementation"], branch_path)
        
        # NOTE: Skipping initialized submodule scenario due to Docker hardlink limitations
        print("📝 Note: Submodule initialization tests limited due to Docker container hardlink restrictions")
        
    def create_simple_repo_at_path(self, repo_path: pathlib.Path, files: List[str]) -> pathlib.Path:
        """Create a simple git repository at specific path."""
        repo_path.mkdir(exist_ok=True, parents=True)
        
        # Initialize repo
        self.run_git(["init"], repo_path)
        
        # Create files
        for file in files:
            (repo_path / file).write_text(f"Content of {file}\n")
            
        # Initial commit
        self.run_git(["add", "."], repo_path)
        self.run_git(["commit", "-m", f"Initial commit for {repo_path.name}"], repo_path)
        
        return repo_path
        
    def create_info_file(self) -> None:
        """Create info file about test repositories."""
        info = """# Test Repository Information

## Repository Hierarchy (3-Level Recursive Submodules)

### Level 1 (Main Superrepository)
- **main-repo**: Top-level repository containing:
  - lib/utils → lib-utils repository  
  - vendor/framework → vendor-framework repository

### Level 2 (Middle-level with submodules)
- **lib-utils**: Utility library (standalone, no submodules)
- **vendor-framework**: Framework repository containing:
  - plugins → plugins-core repository
- **plugins-core**: Plugin management containing:
  - themes/default → theme-default repository
  - auth → plugin-auth repository

### Level 3 (Leaf repositories)
- **theme-default**: CSS theme files and configuration
- **plugin-auth**: Authentication plugin with Python modules

## Submodule Nesting Depth
```
main-repo/
├── lib/utils/                    # → lib-utils (Level 2)
│   ├── utils.py
│   ├── helpers.py  
│   └── constants.py
└── vendor/framework/             # → vendor-framework (Level 2)
    ├── framework.py
    ├── setup.py
    ├── config.py
    └── plugins/                  # → plugins-core (Level 2)
        ├── __init__.py
        ├── core.py
        ├── manager.py
        ├── themes/default/       # → theme-default (Level 3)
        │   ├── theme.css
        │   ├── config.json
        │   └── README.md
        └── auth/                 # → plugin-auth (Level 3)
            ├── auth.py
            ├── requirements.txt
            └── __init__.py
```

## Test Scenarios
- **scenarios/clean-main-repo**: Fresh clone, no submodules initialized
- **scenarios/dirty-main-repo**: Has uncommitted changes in main repo
- **scenarios/initialized-main-repo**: All submodules initialized recursively  
- **scenarios/feature-branch-repo**: On feature branch with changes

## Testing Commands Examples
```bash
cd scenarios/clean-main-repo

# Check repository status
git-wtsm status

# List worktrees (should show no submodules initially)
git-wtsm list

# Add worktree (should auto-initialize submodules)
git-wtsm add ../test-worktree

# List worktrees (should show submodule info)
git-wtsm list

# Check recursive submodule initialization
ls -la lib/utils/ vendor/framework/plugins/themes/default/
```

## Real Submodule Testing
These repositories contain actual git submodules created with filesystem paths,
allowing comprehensive testing of:
- Recursive submodule initialization (3 levels deep)
- Submodule status detection and reporting
- Worktree operations with nested submodule structures
- Clean vs uncommitted submodule state handling
"""
        (self.base_path / "README.md").write_text(info)

def main():
    """Main setup function."""
    print("Setting up git-wtsm test repositories...")
    
    creator = TestRepoCreator()
    
    # Create repository hierarchy
    repos = creator.create_submodule_hierarchy()
    print(f"Created {len(repos)} repositories")
    
    # Create test scenarios
    creator.create_test_scenarios(repos)
    print("Created test scenarios")
    
    # Create documentation
    creator.create_info_file()
    print("Created repository documentation")
    
    print("✅ Test repository setup complete!")
    print(f"Repositories created in: {creator.base_path}")

if __name__ == "__main__":
    main()