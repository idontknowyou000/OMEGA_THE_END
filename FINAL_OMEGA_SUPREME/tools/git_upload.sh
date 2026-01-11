#!/bin/bash
# OMEGA PLOUTUS X - GitHub Upload Script
# Initialize git repository and upload to GitHub

echo "🔥 OMEGA PLOUTUS X - GitHub Upload Script"
echo "========================================"

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Git is not installed. Please install git first."
    exit 1
fi

# Check if we're in the right directory
if [[ ! -f "omega_launcher.py" ]] || [[ ! -f "README.md" ]]; then
    echo "❌ Please run this script from the ECOMEGA_X1 directory"
    exit 1
fi

echo "📁 Current directory: $(pwd)"
echo "📂 Repository contents:"
ls -la | head -10

# Initialize git repository
echo ""
echo "🔧 Initializing git repository..."
if [[ -d ".git" ]]; then
    echo "⚠️  Git repository already initialized"
else
    git init
    echo "✅ Git repository initialized"
fi

# Configure git (optional)
echo ""
echo "👤 Git configuration (optional):"
read -p "Enter your name: " git_name
read -p "Enter your email: " git_email

if [[ -n "$git_name" ]]; then
    git config user.name "$git_name"
fi
if [[ -n "$git_email" ]]; then
    git config user.email "$git_email"
fi

# Add .gitignore first
echo ""
echo "📝 Setting up .gitignore..."
git add .gitignore
git commit -m "Add .gitignore for OMEGA PLOUTUS X"

# Add all files
echo ""
echo "📤 Adding all files to git..."
git add .

# Check git status
echo ""
echo "📊 Git status:"
git status --porcelain | head -20

# Commit
echo ""
echo "💾 Creating initial commit..."
git commit -m "Initial commit: OMEGA PLOUTUS X vX.1.0 - Official Cyber Weapon Platform

🎯 Features:
- Automated ecoATM deployment system
- AI-driven cyber exploitation framework
- Professional Metasploit-style interface
- 15+ integrated attack repositories
- Real ARP poisoning and command injection
- Cross-platform compatibility
- Comprehensive documentation

🔥 Core Components:
- omega_launcher.py: Main platform interface
- auto_ecoATM_deploy.sh: Automated deployment
- omega_kiosk_attack/: Complete attack suite
- proxy_servers/: Professional proxy systems
- README.md: Comprehensive documentation

⚠️  For authorized security research only"

# Set up remote repository
echo ""
echo "🌐 Setting up GitHub remote..."
echo "Repository URL: https://github.com/idontknowyou000/ECOMEGAX1.git"
read -p "Is this the correct repository URL? (y/N): " confirm_url

if [[ "$confirm_url" == "y" ]] || [[ "$confirm_url" == "Y" ]]; then
    git remote add origin https://github.com/idontknowyou000/ECOMEGAX1.git
    echo "✅ Remote repository added"
else
    read -p "Enter the correct repository URL: " repo_url
    git remote add origin "$repo_url"
    echo "✅ Remote repository added"
fi

# Push to GitHub
echo ""
echo "🚀 Pushing to GitHub..."
echo "This may require authentication..."
git push -u origin master

if [[ $? -eq 0 ]]; then
    echo ""
    echo "🎉 SUCCESS! OMEGA PLOUTUS X uploaded to GitHub"
    echo "🌐 Repository: https://github.com/idontknowyou000/ECOMEGAX1"
    echo ""
    echo "📋 Next steps:"
    echo "1. Visit your GitHub repository"
    echo "2. Verify all files are uploaded"
    echo "3. Add repository description and topics"
    echo "4. Consider adding GitHub Actions for CI/CD"
    echo ""
    echo "🔥 OMEGA PLOUTUS X is now publicly available!"
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "1. Authentication required - set up SSH keys or personal access token"
    echo "2. Repository doesn't exist - create it on GitHub first"
    echo "3. Branch name issue - try 'main' instead of 'master'"
    echo ""
    echo "🔧 Manual push command:"
    echo "git push -u origin master"
    echo "or: git push -u origin main"
fi

echo ""
echo "📊 Repository statistics:"
echo "Files: $(git ls-files | wc -l)"
echo "Size: $(du -sh .git)"
echo "Commits: $(git rev-list --count HEAD)"

echo ""
echo "🛡️ Security reminder: This repository contains cyber exploitation tools."
echo "Ensure you comply with all applicable laws and use only for authorized testing."
