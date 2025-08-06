#!/bin/bash

echo "🚀 Setting up Claude Agent Environment..."

# Install the package
echo "📦 Installing package..."
pip install -e .

# Find where cae was installed
CAE_PATH=$(find ~/Library/Python -name "cae" 2>/dev/null | head -1)

if [ -z "$CAE_PATH" ]; then
    # Try Linux path
    CAE_PATH=$(find ~/.local/bin -name "cae" 2>/dev/null | head -1)
fi

if [ -z "$CAE_PATH" ]; then
    echo "❌ Could not find cae installation. Please check pip output above."
    echo "   If you see permission errors, try: pip install -e . --user"
    exit 1
fi

echo "✅ Found cae at: $CAE_PATH"

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
    SHELL_NAME="zsh"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
    SHELL_NAME="bash"
else
    SHELL_RC="$HOME/.profile"
    SHELL_NAME="default"
fi

# Add to PATH
CAE_DIR=$(dirname "$CAE_PATH")

# Check if already in PATH or alias exists
if ! grep -q "$CAE_DIR" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# Claude Agent Environment" >> "$SHELL_RC"
    echo "export PATH=\"$CAE_DIR:\$PATH\"" >> "$SHELL_RC"
    echo "✅ Added cae to PATH in $SHELL_RC"
else
    echo "ℹ️  cae directory already in $SHELL_RC"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "To start using cae:"
echo "  1. Run: source $SHELL_RC"
echo "     Or open a new terminal window"
echo "  2. Create a cae_config.json in your project directory"
echo "  3. Run: cae <branch-name> <repos...>"
echo ""
echo "Example:"
echo "  cd ~/Development/my-project"
echo "  # Create a cae_config.json with your repositories (see README for example)"
echo "  cae feature/new-feature frontend backend"