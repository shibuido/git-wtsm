#!/usr/bin/env python3
"""
git-wtsm-test-03.py: Worktree list functionality tests
Tests the git-wtsm list command with various flags and scenarios.
"""

import unittest
import subprocess
import pathlib
import os
import shutil
from termcolor import colored

class WorktreeListTests(unittest.TestCase):
    """Test worktree list functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_repo = pathlib.Path("/home/testuser/test-repos/scenarios/initialized-main-repo")
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
        for worktree_name in ["test-list-1", "test-list-2", "test-branch-wt"]:
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
        
    def test_list_default_format(self):
        """Test default list format shows worktree and submodule info."""
        result = self.run_git_wtsm(["list"])
        self.assertEqual(result.returncode, 0, "List command should succeed")
        
        # Should show current worktree path
        self.assertIn(str(self.test_repo), result.stdout)
        
        # Should show branch information
        self.assertIn("[", result.stdout)  # Branch in brackets
        self.assertIn("]", result.stdout)
        
        # Should show submodule information (if any submodules exist)
        output = result.stdout.strip()
        if "submodules:" in output:
            self.assertRegex(output, r"\d+ submodules:", "Should show submodule count")
            
    def test_list_porcelain_format(self):
        """Test porcelain format is machine-readable."""
        result = self.run_git_wtsm(["list", "--porcelain"])
        self.assertEqual(result.returncode, 0, "List --porcelain should succeed")
        
        # Should contain machine-readable fields
        self.assertIn("worktree", result.stdout)
        self.assertIn("HEAD", result.stdout)
        
        # Should be parseable format
        lines = result.stdout.strip().split('\n')
        worktree_line = [line for line in lines if line.startswith("worktree")]
        self.assertTrue(len(worktree_line) > 0, "Should have worktree line")
        
    def test_list_verbose_format(self):
        """Test verbose format provides additional information."""
        result = self.run_git_wtsm(["list", "--verbose"])
        self.assertEqual(result.returncode, 0, "List --verbose should succeed")
        
        # Verbose format should show path and branch info
        self.assertIn(str(self.test_repo), result.stdout)
        
    def test_list_multiple_worktrees(self):
        """Test list with multiple worktrees."""
        # Create additional worktrees
        test_wt1 = self.test_repo.parent / "test-list-1" 
        test_wt2 = self.test_repo.parent / "test-list-2"
        
        # Add worktrees
        result1 = self.run_git_wtsm(["add", str(test_wt1)])
        self.assertEqual(result1.returncode, 0, "Add first worktree should succeed")
        
        result2 = self.run_git_wtsm(["add", str(test_wt2), "feature-branch"])
        self.assertEqual(result2.returncode, 0, "Add second worktree should succeed")
        
        # List all worktrees
        result = self.run_git_wtsm(["list"])
        self.assertEqual(result.returncode, 0, "List command should succeed")
        
        # Should show all three worktrees
        lines = result.stdout.strip().split('\n')
        self.assertGreaterEqual(len(lines), 3, "Should show at least 3 worktrees")
        
        # Should show different paths
        self.assertIn(str(self.test_repo), result.stdout)
        self.assertIn(str(test_wt1), result.stdout)
        self.assertIn(str(test_wt2), result.stdout)
        
    def test_list_branch_information(self):
        """Test that list shows correct branch information."""
        # Create worktree with specific branch
        test_wt = self.test_repo.parent / "test-branch-wt"
        result = self.run_git_wtsm(["add", str(test_wt), "test-feature"])
        self.assertEqual(result.returncode, 0, "Add worktree with branch should succeed")
        
        # List worktrees
        result = self.run_git_wtsm(["list"])
        self.assertEqual(result.returncode, 0, "List command should succeed")
        
        # Should show the branch name
        self.assertIn("test-feature", result.stdout, "Should show branch name")
        
    def test_list_submodule_status_integration(self):
        """Test that list integrates submodule status correctly."""
        result = self.run_git_wtsm(["list"])
        self.assertEqual(result.returncode, 0, "List command should succeed")
        
        output = result.stdout
        
        # If repository has submodules, should show count
        if "submodules:" in output:
            # Should show either clean, uncommitted, or both
            has_status = any(word in output for word in ["clean", "uncommitted"])
            self.assertTrue(has_status, "Should show submodule status")
            
            # Should show numeric counts
            import re
            count_pattern = r'\d+ (clean|uncommitted)'
            self.assertRegex(output, count_pattern, "Should show numeric counts")
            
    def test_list_consistency_with_git_worktree(self):
        """Test that porcelain output is consistent with git worktree list."""
        # Get git-wtsm porcelain output
        result_wtsm = self.run_git_wtsm(["list", "--porcelain"])
        self.assertEqual(result_wtsm.returncode, 0, "git-wtsm list --porcelain should succeed")
        
        # Get git worktree list output for comparison
        result_git = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=self.test_repo
        )
        self.assertEqual(result_git.returncode, 0, "git worktree list should succeed")
        
        # Basic structure should be similar (both should have worktree and HEAD lines)
        wtsm_lines = result_wtsm.stdout.strip().split('\n')
        git_lines = result_git.stdout.strip().split('\n')
        
        wtsm_worktree_lines = [line for line in wtsm_lines if line.startswith("worktree")]
        git_worktree_lines = [line for line in git_lines if line.startswith("worktree")]
        
        self.assertEqual(len(wtsm_worktree_lines), len(git_worktree_lines), 
                        "Should have same number of worktrees")

def main():
    """Run the tests."""
    print(colored("Running git-wtsm Worktree List Tests", "cyan", attrs=["bold"]))
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(WorktreeListTests)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    if result.wasSuccessful():
        print(colored("✅ All worktree list tests PASSED", "green", attrs=["bold"]))
        return 0
    else:
        print(colored("❌ Some worktree list tests FAILED", "red", attrs=["bold"]))
        return 1

if __name__ == "__main__":
    exit(main())