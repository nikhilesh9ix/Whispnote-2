#!/bin/bash
# WhispNote 2.0 - Manual Deployment Script for Swecha Repository
# This script helps deploy the enhanced WhispNote 2.0 to code.swecha.org

echo "🚀 WhispNote 2.0 - Swecha Repository Deployment Script"
echo "======================================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the WhispNote project root directory"
    exit 1
fi

echo "📂 Current directory: $(pwd)"
echo "🔍 Verifying project structure..."

# Verify essential files
ESSENTIAL_FILES=("app.py" "pyproject.toml" "src/ai/llama_summarizer.py" "src/utils/swecha_storage.py")
for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - Found"
    else
        echo "❌ $file - Missing"
        exit 1
    fi
done

echo ""
echo "🔧 Git Configuration for Swecha Push"
echo "====================================="

# Configure git for large pushes
git config http.postBuffer 524288000
git config http.timeout 600
git config pack.windowMemory 256m
git config pack.packSizeLimit 128m

echo "✅ Git configured for large repository push"

echo ""
echo "📊 Repository Status"
echo "==================="

echo "📋 Current branch: $(git branch --show-current)"
echo "📋 Last commit: $(git log -1 --oneline)"
echo "📋 Remote repositories:"
git remote -v

echo ""
echo "🚀 Deployment Options"
echo "====================="

echo "Option 1: Direct Push (may timeout)"
echo "git push origin main"
echo ""

echo "Option 2: Force Push (requires admin permissions)"
echo "git push origin main --force-with-lease"
echo ""

echo "Option 3: Create Bundle for Manual Transfer"
echo "git bundle create whispnote-2.bundle HEAD"
echo ""

echo "Option 4: Clone from GitHub to Swecha (Recommended)"
echo "# On a machine with access to Swecha:"
echo "git clone https://github.com/nikhilesh9ix/Whispnote-2.git temp-whispnote"
echo "cd temp-whispnote"
echo "git remote set-url origin https://code.swecha.org/soai2025/techleads/soai-techlead-hackathon/whispnote.git"
echo "git push origin main --force"
echo ""

echo "📞 If all options fail, contact Swecha admin with:"
echo "- HTTP 524 timeout error"
echo "- Repository size: ~35MB"
echo "- Request increased timeout limits"
echo ""

echo "✅ WhispNote 2.0 is fully functional and ready for deployment!"
echo "📁 Complete backup available at: https://github.com/nikhilesh9ix/Whispnote-2.git"
