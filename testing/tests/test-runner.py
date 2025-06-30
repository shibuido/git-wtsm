#!/usr/bin/env python3
"""
Test runner for git-wtsm testing suite.
Orchestrates execution of all test scripts and provides summary reporting.
"""

import sys
import subprocess
import pathlib
import argparse
from termcolor import colored
from typing import List, Dict, Tuple

class TestRunner:
    """Main test orchestrator for git-wtsm."""
    
    def __init__(self):
        self.test_dir = pathlib.Path("/home/testuser/tests")
        self.test_scripts = [
            "git-wtsm-test-01.py",  # Basic functionality
            "git-wtsm-test-02.py",  # Submodule initialization  
            "git-wtsm-test-03.py",  # Worktree list functionality
            "git-wtsm-test-04.py",  # Edge cases and errors
        ]
        self.results: List[Tuple[str, bool, str]] = []
        
    def run_single_test(self, test_script: str) -> Tuple[bool, str]:
        """Run a single test script and return (success, output)."""
        script_path = self.test_dir / test_script
        
        if not script_path.exists():
            return False, f"Test script {test_script} not found"
            
        print(f"\n{'='*60}")
        print(colored(f"Running {test_script}", "yellow", attrs=["bold"]))
        print('='*60)
        
        try:
            result = subprocess.run(
                ["python", str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test
            )
            
            # Print the test output
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(colored(result.stderr, "red"))
                
            success = result.returncode == 0
            output = result.stdout + result.stderr
            
            return success, output
            
        except subprocess.TimeoutExpired:
            return False, f"Test {test_script} timed out after 5 minutes"
        except Exception as e:
            return False, f"Error running {test_script}: {str(e)}"
            
    def run_all_tests(self) -> None:
        """Run all test scripts and collect results."""
        print(colored("🚀 Starting git-wtsm Test Suite", "cyan", attrs=["bold"]))
        print(f"Running {len(self.test_scripts)} test scripts...")
        
        for test_script in self.test_scripts:
            success, output = self.run_single_test(test_script)
            self.results.append((test_script, success, output))
            
    def run_specific_test(self, test_name: str) -> None:
        """Run a specific test script."""
        if not test_name.endswith('.py'):
            test_name += '.py'
            
        if test_name not in self.test_scripts:
            print(colored(f"❌ Test {test_name} not found", "red"))
            available = ", ".join(self.test_scripts)
            print(f"Available tests: {available}")
            sys.exit(1)
            
        success, output = self.run_single_test(test_name)
        self.results.append((test_name, success, output))
        
    def print_summary(self) -> None:
        """Print test execution summary."""
        print(f"\n{'='*80}")
        print(colored("🏁 TEST EXECUTION SUMMARY", "cyan", attrs=["bold"]))
        print('='*80)
        
        passed = 0
        failed = 0
        
        for test_name, success, _ in self.results:
            status = colored("PASS", "green") if success else colored("FAIL", "red")
            print(f"{test_name:<30} {status}")
            
            if success:
                passed += 1
            else:
                failed += 1
                
        total = passed + failed
        
        print(f"\n{'='*80}")
        print(f"Total Tests: {total}")
        print(colored(f"Passed: {passed}", "green", attrs=["bold"]))
        
        if failed > 0:
            print(colored(f"Failed: {failed}", "red", attrs=["bold"]))
            print(f"\nOverall Result: {colored('FAILED', 'red', attrs=['bold'])}")
        else:
            print(f"Failed: {failed}")
            print(f"\nOverall Result: {colored('PASSED', 'green', attrs=['bold'])}")
            
        print('='*80)
        
    def get_exit_code(self) -> int:
        """Return appropriate exit code based on test results."""
        for _, success, _ in self.results:
            if not success:
                return 1
        return 0
        
    def print_environment_info(self) -> None:
        """Print environment information."""
        print(colored("🔧 Environment Information", "blue", attrs=["bold"]))
        
        # Check git-wtsm availability
        try:
            result = subprocess.run(
                ["git-wtsm", "help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                print("✅ git-wtsm is available")
            else:
                print("❌ git-wtsm command failed")
        except Exception as e:
            print(f"❌ git-wtsm not available: {e}")
            
        # Check git version
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"✅ {version}")
        except Exception:
            print("❌ Git not available")
            
        # Check Python version
        print(f"✅ Python {sys.version.split()[0]}")
        
        # Check test repositories
        test_repos_path = pathlib.Path("/home/testuser/test-repos")
        if test_repos_path.exists():
            print("✅ Test repositories are set up")
        else:
            print("❌ Test repositories not found")
            
        print()

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="git-wtsm test runner")
    parser.add_argument("--all", action="store_true", 
                       help="Run all tests (default)")
    parser.add_argument("--test", "-t", 
                       help="Run specific test (e.g., git-wtsm-test-01)")
    parser.add_argument("--list", "-l", action="store_true",
                       help="List available tests")
    parser.add_argument("--env", "-e", action="store_true",
                       help="Show environment information")
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    if args.list:
        print("Available tests:")
        for test in runner.test_scripts:
            print(f"  {test}")
        return 0
        
    if args.env:
        runner.print_environment_info()
        return 0
        
    # Show environment info by default
    runner.print_environment_info()
    
    if args.test:
        runner.run_specific_test(args.test)
    else:
        runner.run_all_tests()
        
    runner.print_summary()
    return runner.get_exit_code()

if __name__ == "__main__":
    sys.exit(main())