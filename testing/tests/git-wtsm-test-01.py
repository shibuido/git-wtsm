#!/usr/bin/env python3
"""
git-wtsm-test-01.py: Basic functionality tests
Tests core git-wtsm commands without submodules.
"""

import unittest
import subprocess
import pathlib
import os
import shutil
from termcolor import colored

class BasicFunctionalityTests(unittest.TestCase):
    """Test basic git-wtsm functionality."""
    
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
        test_worktree = self.test_repo.parent / "test-worktree"
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
        
    def test_help_command(self):
        """Test git-wtsm help command."""
        result = self.run_git_wtsm(["help"])
        self.assertEqual(result.returncode, 0, "Help command should succeed")
        self.assertIn("git-wtsm: Git worktree/submodule manager", result.stdout)
        self.assertIn("Usage:", result.stdout)
        
    def test_no_arguments_shows_help(self):
        """Test git-wtsm with no arguments shows help."""
        result = self.run_git_wtsm([])
        self.assertEqual(result.returncode, 0, "No arguments should show help")
        self.assertIn("Usage:", result.stdout)
        
    def test_status_command(self):
        """Test git-wtsm status command."""
        result = self.run_git_wtsm(["status"])
        self.assertEqual(result.returncode, 0, "Status command should succeed")
        self.assertIn("Worktrees:", result.stdout)
        self.assertIn("Submodules:", result.stdout)
        
    def test_list_command_basic(self):
        """Test git-wtsm list command."""
        result = self.run_git_wtsm(["list"])
        self.assertEqual(result.returncode, 0, "List command should succeed")
        # Should show current worktree
        self.assertIn(str(self.test_repo), result.stdout)
        
    def test_list_porcelain(self):
        """Test git-wtsm list --porcelain."""
        result = self.run_git_wtsm(["list", "--porcelain"])
        self.assertEqual(result.returncode, 0, "List --porcelain should succeed")
        self.assertIn("worktree", result.stdout)
        self.assertIn("HEAD", result.stdout)
        
    def test_add_worktree(self):
        """Test adding a worktree."""
        test_worktree = self.test_repo.parent / "test-worktree"
        
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertEqual(result.returncode, 0, f"Add worktree should succeed: {result.stderr}")
        self.assertTrue(test_worktree.exists(), "Worktree directory should exist")
        self.assertTrue((test_worktree / ".git").exists(), "Worktree should have .git file")
        
    def test_add_worktree_with_branch(self):
        """Test adding a worktree with new branch."""
        test_worktree = self.test_repo.parent / "test-worktree-branch"
        
        result = self.run_git_wtsm(["add", str(test_worktree), "test-branch"])
        self.assertEqual(result.returncode, 0, "Add worktree with branch should succeed")
        self.assertTrue(test_worktree.exists(), "Worktree directory should exist")
        
        # Cleanup
        if test_worktree.exists():
            shutil.rmtree(test_worktree)
            
    def test_remove_worktree(self):
        """Test removing a worktree."""
        test_worktree = self.test_repo.parent / "test-worktree"
        
        # First add a worktree
        result = self.run_git_wtsm(["add", str(test_worktree)])
        self.assertEqual(result.returncode, 0, "Add worktree should succeed")
        
        # Then remove it
        result = self.run_git_wtsm(["remove", str(test_worktree)])
        self.assertEqual(result.returncode, 0, "Remove worktree should succeed")
        self.assertFalse(test_worktree.exists(), "Worktree directory should be removed")

def main():
    """Run the tests."""
    print(colored("Running git-wtsm Basic Functionality Tests", "cyan", attrs=["bold"]))
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(BasicFunctionalityTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(colored("✅ All basic functionality tests PASSED", "green", attrs=["bold"]))
        return 0
    else:
        print(colored("❌ Some basic functionality tests FAILED", "red", attrs=["bold"]))
        return 1

if __name__ == "__main__":
    exit(main())