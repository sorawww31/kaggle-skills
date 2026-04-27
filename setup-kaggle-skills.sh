#!/bin/bash
# setup-kaggle-skills.sh
# Integrate kaggle-skills into an existing project using git submodule

set -e

REPO_URL="https://github.com/kaggle-project/kaggle-skills"
SUBMODULE_PATH=".agents-source"

echo "🚀 Kaggle Skills Setup"
echo ""

# Check if git repository exists
if [ ! -d .git ]; then
    echo "❌ Error: Not a git repository. Please run this from your project root."
    exit 1
fi

# Check if submodule already exists
if [ -d "$SUBMODULE_PATH" ]; then
    echo "⚠️  $SUBMODULE_PATH already exists. Skipping submodule addition."
else
    echo "📦 Adding kaggle-skills as submodule..."
    git submodule add "$REPO_URL" "$SUBMODULE_PATH"
fi

echo "🔄 Syncing agent assets..."
python "$SUBMODULE_PATH/sync_agent_assets.py"
echo "✅ Agent assets synced"

echo ""
echo "⚙️  Setting up .env..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
    else
        echo "KAGGLE_API_TOKEN=" > .env
        echo "✅ Created .env"
    fi
    echo "📝 Please edit .env and add your KAGGLE_API_TOKEN"
else
    echo "✅ .env already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your KAGGLE_API_TOKEN"
echo "  2. If you already had local MCP/Codex settings, review .mcp.json and .codex/config.toml"
echo "  3. Run 'python sync_agent_assets.py' to update local assets anytime"
echo "  4. Check README.md for usage examples"
echo ""
