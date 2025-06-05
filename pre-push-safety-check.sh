#!/bin/bash
# PRE-PUSH SAFETY CHECK
# Run this before ANY git push to production

set -e

echo "🚨 PRODUCTION SAFETY CHECK 🚨"
echo "=================================="

# Check repository identity
echo "1. Verifying repository..."
REMOTE_URL=$(git remote get-url origin)
echo "Remote URL: $REMOTE_URL"

if [[ $REMOTE_URL != *"eva_web"* ]]; then
    echo "❌ ERROR: This doesn't look like the eva_web repository!"
    echo "Expected: eva_web repository"
    echo "Got: $REMOTE_URL"
    exit 1
fi

# Check deployment config
echo "2. Checking deployment configuration..."
if [ ! -f "railway.json" ]; then
    echo "❌ ERROR: No railway.json found!"
    exit 1
fi

START_COMMAND=$(grep -o '"startCommand": "[^"]*"' railway.json | cut -d'"' -f4)
echo "Start command: $START_COMMAND"

if [[ $START_COMMAND != "python core/eva.py" ]]; then
    echo "❌ ERROR: Wrong start command!"
    echo "Expected: python core/eva.py"
    echo "Got: $START_COMMAND"
    exit 1
fi

# Check main EVA file exists
echo "3. Verifying main EVA files..."
if [ ! -f "core/eva.py" ]; then
    echo "❌ ERROR: core/eva.py not found!"
    echo "This doesn't look like the main EVA repository!"
    exit 1
fi

# Check git status
echo "4. Checking git status..."
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Uncommitted changes detected:"
    git status --short
    echo ""
fi

# Show what will be pushed
echo "5. Changes to be pushed:"
git log --oneline origin/main..HEAD

# Final confirmation
echo ""
echo "🎯 DEPLOYMENT TARGET"
echo "Repository: eva_web (Main EVA Web App)"
echo "URL: https://evaweb-production.up.railway.app"
echo "Command: python core/eva.py"
echo ""

read -p "⚠️  Are you SURE you want to push to PRODUCTION? (type 'YES' to confirm): " confirm

if [ "$confirm" != "YES" ]; then
    echo "❌ Push cancelled for safety"
    exit 1
fi

echo "✅ Safety checks passed. Proceeding with push..."
echo "🚀 Pushing to production..."

# Actually push
git push "$@"

echo "✅ Push completed successfully!"
echo "📊 Monitor deployment at: https://railway.app"