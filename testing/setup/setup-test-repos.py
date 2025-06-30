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
        result = subprocess.run(
            ["git"] + cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        
    def create_simple_repo(self, name: str, files: List[str] = None) -> pathlib.Path:
        """Create a simple git repository with initial files."""
        repo_path = self.base_path / name
        repo_path.mkdir(exist_ok=True)
        
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
        """Create simpler submodule hierarchy for testing."""
        repos = {}
        
        print("Creating Level 2 repositories (leaf nodes)...")
        # Level 2 - Simple submodules (no sub-submodules)
        repos["lib-utils"] = self.create_simple_repo("lib-utils",
            ["utils.py", "helpers.py"])
        repos["vendor-framework"] = self.create_simple_repo("vendor-framework",
            ["framework.py", "setup.py"])
            
        print("Creating Level 1 repositories (main superrepository)...")
        # Level 1 - Top-level superrepository
        repos["main-repo"] = self.create_simple_repo("main-repo",
            ["main.py", "config.yaml", ".gitignore"])
            
        # Add Level 2 submodules to Level 1
        # Create lib directory first
        (repos["main-repo"] / "lib").mkdir(exist_ok=True)
        (repos["main-repo"] / "vendor").mkdir(exist_ok=True)
        
        print("Adding submodules...")
        self.run_git(["submodule", "add", str(repos["lib-utils"]), "lib/utils"],
                    repos["main-repo"])
        self.run_git(["submodule", "add", str(repos["vendor-framework"]), "vendor/framework"],
                    repos["main-repo"])
        self.run_git(["commit", "-m", "Add lib and vendor submodules"], repos["main-repo"])
        
        return repos
        
    def create_test_scenarios(self, repos: Dict[str, pathlib.Path]) -> None:
        """Create different test scenarios."""
        scenarios_path = self.base_path / "scenarios"
        scenarios_path.mkdir(exist_ok=True)
        
        print("Creating test scenarios...")
        
        # Scenario 1: Clean repository clone
        clean_path = scenarios_path / "clean-main-repo"
        self.run_git(["clone", str(repos["main-repo"]), str(clean_path)], self.base_path)
        
        # Scenario 2: Repository with uncommitted changes
        dirty_path = scenarios_path / "dirty-main-repo"
        self.run_git(["clone", str(repos["main-repo"]), str(dirty_path)], self.base_path)
        (dirty_path / "uncommitted.txt").write_text("Uncommitted changes\n")
        
        # Scenario 3: Repository with initialized submodules
        initialized_path = scenarios_path / "initialized-main-repo"
        self.run_git(["clone", str(repos["main-repo"]), str(initialized_path)], self.base_path)
        self.run_git(["submodule", "update", "--init", "--recursive"], initialized_path)
        
        # Scenario 4: Different branch
        branch_path = scenarios_path / "feature-branch-repo"
        self.run_git(["clone", str(repos["main-repo"]), str(branch_path)], self.base_path)
        self.run_git(["checkout", "-b", "feature/test-branch"], branch_path)
        (branch_path / "feature.py").write_text("Feature implementation\n")
        self.run_git(["add", "feature.py"], branch_path)
        self.run_git(["commit", "-m", "Add feature implementation"], branch_path)
        
    def create_info_file(self) -> None:
        """Create info file about test repositories."""
        info = """# Test Repository Information

## Repository Hierarchy

### Level 1 (Superrepositories)
- main-repo: Contains lib/utils and vendor/framework submodules
- lib-utils: Utility library (no submodules)

### Level 2 (Middle-level with submodules)  
- vendor-framework: Contains plugins submodule
- plugins-core: Contains themes/default and auth submodules

### Level 3 (Leaf repositories)
- theme-default: CSS theme files
- plugin-auth: Authentication plugin

## Test Scenarios
- scenarios/clean-main-repo: Fresh clone, no submodules initialized
- scenarios/dirty-main-repo: Has uncommitted changes
- scenarios/initialized-main-repo: All submodules initialized recursively  
- scenarios/feature-branch-repo: On feature branch with changes

## Testing Commands
cd scenarios/clean-main-repo
git-wtsm status
git-wtsm add ../test-worktree
git-wtsm list
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