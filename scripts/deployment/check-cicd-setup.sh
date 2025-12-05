#!/bin/bash

# Quick CI/CD Setup Script
# This script helps you verify your CI/CD setup

echo "🔍 Checking CI/CD Setup Prerequisites..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check Git
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Git repository detected"
    BRANCH=$(git branch --show-current)
    echo "  Current branch: $BRANCH"
else
    echo -e "${RED}✗${NC} Not a git repository"
    exit 1
fi

# Check GitHub remote
if git remote -v | grep -q "github.com"; then
    echo -e "${GREEN}✓${NC} GitHub remote configured"
    REPO=$(git remote get-url origin | sed 's/.*github.com[:/]\(.*\)\.git/\1/')
    echo "  Repository: $REPO"
else
    echo -e "${RED}✗${NC} GitHub remote not found"
    exit 1
fi

# Check workflow file
if [ -f ".github/workflows/github-cicd.yml" ]; then
    echo -e "${GREEN}✓${NC} CI/CD workflow file exists"
else
    echo -e "${RED}✗${NC} CI/CD workflow file missing"
    exit 1
fi

# Check compose file
if [ -f "compose.yml" ]; then
    echo -e "${GREEN}✓${NC} compose.yml exists"
else
    echo -e "${RED}✗${NC} compose.yml missing"
    exit 1
fi

# Check scripts
SCRIPTS=("start.sh" "test.sh" "init-databases.sh" "kong/configure-kong.sh")
for script in "${SCRIPTS[@]}"; do
    if [ -f "$script" ]; then
        if [ -x "$script" ]; then
            echo -e "${GREEN}✓${NC} $script exists and is executable"
        else
            echo -e "${YELLOW}⚠${NC} $script exists but not executable (run: chmod +x $script)"
        fi
    else
        echo -e "${RED}✗${NC} $script missing"
    fi
done

echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Configure GitHub Secrets (Settings → Secrets → Actions):"
echo "   - DEV_HOST, DEV_USER, DEV_SSH_KEY"
echo "   - STAGING_HOST, STAGING_USER, STAGING_SSH_KEY"
echo "   - PROD_HOST, PROD_USER, PROD_SSH_KEY"
echo ""
echo "2. Configure GitHub Environments (Settings → Environments):"
echo "   - development (no protection)"
echo "   - staging (no protection)"
echo "   - production (require reviewers)"
echo ""
echo "3. Generate SSH keys:"
echo "   ssh-keygen -t ed25519 -C 'github-actions' -f ~/.ssh/github_deploy"
echo ""
echo "4. Test deployment:"
echo "   git checkout develop"
echo "   git add ."
echo "   git commit -m 'test: CI/CD setup'"
echo "   git push origin develop"
echo ""
echo "5. Monitor in GitHub Actions tab"
echo ""
echo "📖 Full documentation: docs/CICD_SETUP.md"
