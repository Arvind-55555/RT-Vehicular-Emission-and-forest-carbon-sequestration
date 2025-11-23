#!/usr/bin/env python3
"""
Script to push all improvements to GitHub repository
"""

import os
import subprocess
import sys
from pathlib import Path

class GitHubPusher:
    def __init__(self, repo_path: str = "."):
        self.repo_path = Path(repo_path).absolute()
        self.branch_name = "feature/comprehensive-improvements"
        self.commit_message = """Implement comprehensive code improvements and CI/CD pipeline

This commit includes:
- Fixed code errors and inconsistencies
- Enhanced project structure and organization
- Added comprehensive CI/CD pipeline with GitHub Actions
- Improved error handling and type hints
- Added unit tests and code quality checks
- Enhanced visualization capabilities
- Updated documentation and requirements
- Security scanning and data validation
- Performance optimizations
- Code quality metrics and analysis"""
    
    def run_command(self, command: str, check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and return result"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=self.repo_path,
                capture_output=True, 
                text=True,
                check=check
            )
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Command failed: {command}")
            print(f"Error: {e.stderr}")
            if check:
                raise
            return e
    
    def check_git_installed(self) -> bool:
        """Check if git is installed and available"""
        try:
            result = self.run_command("git --version")
            print(f"✅ Git version: {result.stdout.strip()}")
            return True
        except:
            print("❌ Git is not installed or not in PATH")
            return False
    
    def check_repository_status(self) -> bool:
        """Check if we're in a git repository"""
        try:
            self.run_command("git status")
            return True
        except:
            print("❌ Not a git repository or git not initialized")
            return False
    
    def initialize_repository(self):
        """Initialize git repository if needed"""
        if not self.check_repository_status():
            print("🔄 Initializing git repository...")
            self.run_command("git init")
            self.run_command("git remote add origin https://github.com/Arvind-55555/RT-Vehicular-Emission-and-forest-carbon-sequestration.git")
    
    def setup_user_info(self):
        """Setup git user information if not configured"""
        try:
            # Check if user email is set
            self.run_command("git config user.email", check=False)
        except:
            print("🔧 Setting up git user information...")
            self.run_command('git config user.name "GitHub Actions"')
            self.run_command('git config user.email "actions@github.com"')
    
    def create_project_structure(self):
        """Create the improved project structure"""
        print("📁 Creating project structure...")
        
        directories = [
            "src",
            "tests", 
            "data/raw",
            "data/processed",
            "data/external",
            "notebooks",
            "docs",
            "scripts",
            "config",
            "logs",
            ".github/workflows",
            "reports/daily"
        ]
        
        for directory in directories:
            dir_path = self.repo_path / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"  Created: {directory}")
        
        # Create __init__.py files for Python packages
        init_files = ["src/__init__.py", "tests/__init__.py"]
        for init_file in init_files:
            file_path = self.repo_path / init_file
            file_path.touch()
    
    def stage_all_changes(self):
        """Stage all changes for commit"""
        print("📦 Staging changes...")
        
        # Add all files
        result = self.run_command("git add .")
        
        # Show what will be committed
        status_result = self.run_command("git status --short")
        if status_result.stdout:
            print("📝 Files to be committed:")
            print(status_result.stdout)
        else:
            print("⚠️  No changes to commit")
            return False
        
        return True
    
    def commit_changes(self):
        """Commit all staged changes"""
        print("💾 Committing changes...")
        
        # Check if there are changes to commit
        result = self.run_command("git diff --cached --quiet", check=False)
        if result.returncode == 0:
            print("⚠️  No changes to commit")
            return False
        
        self.run_command(f'git commit -m "{self.commit_message}"')
        return True
    
    def push_changes(self):
        """Push changes to GitHub"""
        print("📤 Pushing to GitHub...")
        
        # Check if branch exists remotely
        result = self.run_command(
            f"git ls-remote --heads origin {self.branch_name}", 
            check=False
        )
        
        if result.returncode == 0:
            # Branch exists remotely, pull first
            print("🔄 Branch exists remotely, pulling latest changes...")
            self.run_command(f"git pull origin {self.branch_name}")
        
        # Push to GitHub
        self.run_command(f"git push -u origin {self.branch_name}")
        
        print(f"✅ Successfully pushed to branch: {self.branch_name}")
        
        # Show PR creation URL
        pr_url = f"https://github.com/Arvind-55555/RT-Vehicular-Emission-and-forest-carbon-sequestration/compare/main...{self.branch_name}"
        print(f"🔗 Create a Pull Request: {pr_url}")
    
    def main(self):
        """Main execution function"""
        print("🚀 Starting GitHub push process...")
        print(f"📁 Repository path: {self.repo_path}")
        
        # Check prerequisites
        if not self.check_git_installed():
            sys.exit(1)
        
        # Ensure we're in the repository
        os.chdir(self.repo_path)
        
        # Initialize repository if needed
        self.initialize_repository()
        
        # Setup user info
        self.setup_user_info()
        
        # Create branch
        print(f"🌿 Creating/checking out branch: {self.branch_name}")
        
        # Check if branch exists locally
        result = self.run_command(f"git show-ref --verify --quiet refs/heads/{self.branch_name}", check=False)
        if result.returncode == 0:
            # Branch exists, checkout
            self.run_command(f"git checkout {self.branch_name}")
        else:
            # Create new branch
            self.run_command(f"git checkout -b {self.branch_name}")
        
        # Create project structure (this would be where you create all the improved files)
        self.create_project_structure()
        
        # Stage changes
        if not self.stage_all_changes():
            print("❌ No changes to stage. Make sure you've added the improved files.")
            return
        
        # Commit changes
        if not self.commit_changes():
            print("❌ No changes to commit.")
            return
        
        # Push to GitHub
        self.push_changes()
        
        print("🎉 All changes successfully pushed to GitHub!")

if __name__ == "__main__":
    # Get repository path from command line or use current directory
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    pusher = GitHubPusher(repo_path)
    pusher.main()