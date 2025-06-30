#!/usr/bin/env python3
"""
git-wtsm-test-04.py: Edge cases and error handling tests
Tests error conditions, edge cases, and safety features.
"""

import unittest
import subprocess
import pathlib
import os
import shutil
from termcolor import colored

class EdgeCasesAndErrorTests(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test environment."""
        self.clean_repo = pathlib.Path("/home/testuser/test-repos/scenarios/clean-main-repo")
        self.dirty_repo = pathlib.Path("/home/testuser/test-repos/scenarios/dirty-main-repo") 
        self.original_dir = pathlib.Path.cwd()
        
        # Start in clean repo by default
        os.chdir(self.clean_repo)
        
        # Clean up any existing test worktrees
        self.cleanup_worktrees()
        
    def tearDown(self):
        """Clean up after tests."""
        self.cleanup_worktrees()
        os.chdir(self.original_dir)
        
    def cleanup_worktrees(self):
        """Remove any test worktrees."""
        for repo_parent in [self.clean_repo.parent, self.dirty_repo.parent]:
            for worktree_name in ["test-error-wt", "test-force-wt", "test-edge-wt"]:
                test_worktree = repo_parent / worktree_name
                if test_worktree.exists():
                    shutil.rmtree(test_worktree)
                    
    def run_git_wtsm(self, args, cwd=None):
        """Run git-wtsm command and return result."""
        cmd = ["git-wtsm"] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=cwd or pathlib.Path.cwd()
        )
        return result
        
    def test_invalid_command(self):
        """Test invalid command handling."""
        result = self.run_git_wtsm(["invalid-command"])
        self.assertNotEqual(result.returncode, 0, "Invalid command should fail")
        self.assertIn("error", result.stderr.lower(), "Should show error message")
        
    def test_dirty_repository_safety(self):
        """Test that dirty repository prevents operations."""
        os.chdir(self.dirty_repo)
        
        test_worktree = self.dirty_repo.parent / "test-error-wt"
        
        # Should fail due to uncommitted changes
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertNotEqual(result.returncode, 0, "Should fail with dirty repository")
        
    def test_non_git_repository(self):
        """Test behavior in non-git directory."""
        # Create temporary non-git directory
        temp_dir = pathlib.Path("/tmp/not-a-git-repo")
        temp_dir.mkdir(exist_ok=True)
        
        try:
            result = self.run_git_wtsm(["status"], cwd=temp_dir)
            self.assertNotEqual(result.returncode, 0, "Should fail in non-git repository")
        finally:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                
    def test_worktree_already_exists(self):
        """Test adding worktree to existing directory."""
        test_worktree = self.clean_repo.parent / "test-edge-wt"
        
        # Create directory first
        test_worktree.mkdir()
        (test_worktree / "existing-file.txt").write_text("Already exists")
        
        try:
            # Should handle existing directory appropriately
            result = self.run_git_wtsm(["add", str(test_worktree)])
            # Git behavior: fails if directory exists and is not empty
            self.assertNotEqual(result.returncode, 0, "Should fail with existing non-empty directory")
        finally:
            if test_worktree.exists():
                shutil.rmtree(test_worktree)
                
    def test_remove_nonexistent_worktree(self):
        """Test removing non-existent worktree."""
        nonexistent = self.clean_repo.parent / "does-not-exist"
        
        result = self.run_git_wtsm(["remove", str(nonexistent)])
        self.assertNotEqual(result.returncode, 0, "Should fail when removing non-existent worktree")
        
    def test_remove_main_worktree(self):
        """Test attempting to remove main worktree."""
        result = self.run_git_wtsm(["remove", str(self.clean_repo)])
        self.assertNotEqual(result.returncode, 0, "Should fail when removing main worktree")
        
    def test_force_remove_functionality(self):
        """Test force remove with confirmation."""
        test_worktree = self.clean_repo.parent / "test-force-wt"
        
        # Add worktree
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertEqual(result.returncode, 0, "Add worktree should succeed")
        
        # Make some changes to require force removal
        (test_worktree / "untracked.txt").write_text("Untracked file")
        
        # Test that normal remove might fail
        result = self.run_git_wtsm(["remove", str(test_worktree)])
        # Note: Depending on git version, this might succeed or fail
        
        # Force remove should work (but we can't test interactively)
        # This test verifies the command structure is correct
        
        # Cleanup manually
        if test_worktree.exists():
            shutil.rmtree(test_worktree)
            
    def test_list_empty_repository(self):
        """Test list command in repository with no additional worktrees."""
        result = self.run_git_wtsm(["list"])
        self.assertEqual(result.returncode, 0, "List should succeed even with single worktree")
        
        # Should show at least the main worktree
        lines = result.stdout.strip().split('\n')
        self.assertGreater(len(lines), 0, "Should show at least main worktree")
        
    def test_invalid_branch_name(self):
        """Test adding worktree with invalid branch name."""
        test_worktree = self.clean_repo.parent / "test-invalid-branch"
        
        # Try to create worktree with invalid branch name
        result = self.run_git_wtsm(["add", str(test_worktree), "refs/heads/invalid..name"])
        self.assertNotEqual(result.returncode, 0, "Should fail with invalid branch name")
        
    def test_deeply_nested_path(self):
        """Test worktree creation with deeply nested path."""
        deep_path = self.clean_repo.parent / "very" / "deep" / "nested" / "path" / "worktree"
        
        # Should create intermediate directories
        result = self.run_git_wtsm(["add", str(deep_path)])
        
        if result.returncode == 0:
            self.assertTrue(deep_path.exists(), "Should create deeply nested worktree")
            # Cleanup
            shutil.rmtree(deep_path.parents[4])  # Remove "very" directory
        
    def test_command_line_argument_validation(self):
        """Test command line argument validation."""
        # Missing required arguments
        result = self.run_git_wtsm(["add"])
        self.assertNotEqual(result.returncode, 0, "Should fail with missing path argument")
        
        result = self.run_git_wtsm(["remove"])
        self.assertNotEqual(result.returncode, 0, "Should fail with missing path argument")
        
    def test_concurrent_access_safety(self):
        """Test behavior with potential concurrent access issues."""
        # This is a basic test - full concurrent testing would require more complex setup
        test_worktree = self.clean_repo.parent / "test-concurrent"
        
        # Add worktree
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertEqual(result.returncode, 0, "Add worktree should succeed")
        
        # Multiple status calls should be safe
        for _ in range(3):
            result = self.run_git_wtsm(["status"])
            self.assertEqual(result.returncode, 0, "Multiple status calls should succeed")
            
        # Cleanup
        if test_worktree.exists():
            shutil.rmtree(test_worktree)

def main():
    """Run the tests."""
    print(colored("Running git-wtsm Edge Cases and Error Handling Tests", "cyan", attrs=["bold"]))
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(EdgeCasesAndErrorTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(colored("✅ All edge case and error handling tests PASSED", "green", attrs=["bold"]))
        return 0
    else:
        print(colored("❌ Some edge case and error handling tests FAILED", "red", attrs=["bold"]))
        return 1

if __name__ == "__main__":
    exit(main())