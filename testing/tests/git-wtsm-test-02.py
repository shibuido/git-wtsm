#!/usr/bin/env python3
"""
git-wtsm-test-02.py: Submodule initialization tests
Tests automatic submodule initialization when adding worktrees.
"""

import unittest
import subprocess
import pathlib
import os
import shutil
from termcolor import colored

class SubmoduleInitializationTests(unittest.TestCase):
    """Test submodule initialization functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_repo = pathlib.Path("/home/testuser/test-repos/scenarios/clean-main-repo")
        self.original_dir = pathlib.Path.cwd()
        os.chdir(self.test_repo)
        
        # Clean up any existing test worktrees
        self.cleanup_worktrees()
        
    def tearDown(self):
        """Clean up after tests."""
        self.cleanup_worktrees()
        os.chdir(self.original_dir)
        
    def cleanup_worktrees(self):
        """Remove any test worktrees."""
        for worktree_name in ["test-submodule-worktree", "test-branch-worktree"]:
            test_worktree = self.test_repo.parent / worktree_name
            if test_worktree.exists():
                shutil.rmtree(test_worktree)
                
    def run_git_wtsm(self, args):
        """Run git-wtsm command and return result."""
        cmd = ["git-wtsm"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=self.test_repo
        )
        return result
        
    def run_git(self, args, cwd=None):
        """Run git command and return result."""
        cmd = ["git"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or self.test_repo
        )
        return result
        
    def test_submodule_detection(self):
        """Test that git-wtsm detects submodules in repository."""
        result = self.run_git_wtsm(["status"])
        self.assertEqual(result.returncode, 0, "Status command should succeed")
        # Should show submodules section
        self.assertIn("Submodules:", result.stdout)
        
    def test_add_worktree_initializes_submodules(self):
        """Test that adding worktree automatically initializes submodules."""
        test_worktree = self.test_repo.parent / "test-submodule-worktree"
        
        # Add worktree
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertEqual(result.returncode, 0, f"Add worktree should succeed: {result.stderr}")
        
        # Check that worktree exists
        self.assertTrue(test_worktree.exists(), "Worktree directory should exist")
        
        # Check that submodules are initialized
        lib_utils = test_worktree / "lib" / "utils"
        vendor_framework = test_worktree / "vendor" / "framework"
        
        self.assertTrue(lib_utils.exists(), "lib/utils submodule should exist")
        self.assertTrue(vendor_framework.exists(), "vendor/framework submodule should exist")
        
        # Check that submodule files are present
        self.assertTrue((lib_utils / "utils.py").exists(), "Submodule files should be checked out")
        self.assertTrue((vendor_framework / "framework.py").exists(), "Submodule files should be checked out")
        
    def test_recursive_submodule_initialization(self):
        """Test that nested submodules are initialized recursively."""
        test_worktree = self.test_repo.parent / "test-recursive-worktree"
        
        # Add worktree
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertEqual(result.returncode, 0, "Add worktree should succeed")
        
        # Check that nested submodules are initialized
        plugins_path = test_worktree / "vendor" / "framework" / "plugins"
        theme_path = plugins_path / "themes" / "default"
        auth_path = plugins_path / "auth"
        
        self.assertTrue(plugins_path.exists(), "Nested plugins submodule should exist")
        self.assertTrue(theme_path.exists(), "Deeply nested theme submodule should exist")
        self.assertTrue(auth_path.exists(), "Deeply nested auth submodule should exist")
        
        # Check that deeply nested files are present
        self.assertTrue((theme_path / "theme.css").exists(), "Deep submodule files should exist")
        self.assertTrue((auth_path / "auth.py").exists(), "Deep submodule files should exist")
        
        # Cleanup
        if test_worktree.exists():
            shutil.rmtree(test_worktree)
            
    def test_list_shows_submodule_status(self):
        """Test that list command shows submodule status."""
        test_worktree = self.test_repo.parent / "test-list-worktree"
        
        # Add worktree
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertEqual(result.returncode, 0, "Add worktree should succeed")
        
        # List worktrees with submodule info
        result = self.run_git_wtsm(["list"])
        self.assertEqual(result.returncode, 0, "List command should succeed")
        
        # Should show submodule information
        output_lines = result.stdout.strip().split('\n')
        submodule_info_found = any("submodules:" in line for line in output_lines)
        self.assertTrue(submodule_info_found, "List should show submodule status")
        
        # Cleanup
        if test_worktree.exists():
            shutil.rmtree(test_worktree)
            
    def test_submodule_status_after_changes(self):
        """Test submodule status detection after making changes."""
        test_worktree = self.test_repo.parent / "test-changes-worktree"
        
        # Add worktree
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertEqual(result.returncode, 0, "Add worktree should succeed")
        
        # Make changes in a submodule
        submodule_path = test_worktree / "lib" / "utils"
        test_file = submodule_path / "test_change.txt"
        test_file.write_text("This is a test change")
        
        # Check that git-wtsm detects the change
        result = self.run_git_wtsm(["list"])
        self.assertEqual(result.returncode, 0, "List command should succeed")
        
        # Should show uncommitted changes
        self.assertIn("uncommitted", result.stdout.lower(), "Should detect uncommitted changes")
        
        # Cleanup
        if test_worktree.exists():
            shutil.rmtree(test_worktree)

def main():
    """Run the tests."""
    print(colored("Running git-wtsm Submodule Initialization Tests", "cyan", attrs=["bold"]))
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(SubmoduleInitializationTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(colored("✅ All submodule initialization tests PASSED", "green", attrs=["bold"]))
        return 0
    else:
        print(colored("❌ Some submodule initialization tests FAILED", "red", attrs=["bold"]))
        return 1

if __name__ == "__main__":
    exit(main())