#!/bin/bash

# Script to push all improvements to GitHub
# Make executable: chmod +x push_changes.sh

set -e  # Exit on any error

echo "🚀 Starting GitHub push process..."

# Configuration
REPO_DIR="/home/arvind/Downloads/projects/Completed/Real-Time-Vehicular-Emission"
COMMIT_MESSAGE="Implement comprehensive code improvements and CI/CD pipeline"
BRANCH_NAME="feature/comprehensive-improvements"

cd "$REPO_DIR"

# Check if git repository exists
if [ ! -d ".git" ]; then
    echo "❌ Not a git repository. Initializing..."
    git init
    git remote add origin https://github.com/Arvind-55555/RT-Vehicular-Emission-and-forest-carbon-sequestration.git
fi

# Check current status
echo "📊 Checking repository status..."
git status

# Create new branch for improvements
echo "🌿 Creating new branch: $BRANCH_NAME"
git checkout -b "$BRANCH_NAME"

# Add all new and modified files
echo "📦 Staging changes..."
git add .

# Check what's being committed
echo "📝 Files to be committed:"
git status --short

# Commit changes
echo "💾 Committing changes..."
git commit -m "$COMMIT_MESSAGE" \
           -m "This commit includes:
           - Fixed code errors and inconsistencies
           - Enhanced project structure and organization
           - Added comprehensive CI/CD pipeline with GitHub Actions
           - Improved error handling and type hints
           - Added unit tests and code quality checks
           - Enhanced visualization capabilities
           - Updated documentation and requirements
           - Security scanning and data validation"

# Push to GitHub
echo "📤 Pushing to GitHub..."
git push -u origin "$BRANCH_NAME"

echo "✅ Successfully pushed all changes to branch: $BRANCH_NAME"
echo "🔗 Create a Pull Request: https://github.com/Arvind-55555/RT-Vehicular-Emission-and-forest-carbon-sequestration/compare/main...$BRANCH_NAME"