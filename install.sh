#!/bin/bash

# Claude Agent Environment Install Script
# This script handles cloning and setup with proper checks

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

REPO_URL="https://github.com/kgn/claude_agent_environment.git"
INSTALL_DIR="$HOME/.claude_agent_environment"
DIR_NAME="$(basename "$INSTALL_DIR")"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     Claude Agent Environment (CAE) Installer${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo

# Check if directory already exists
if [ -d "$INSTALL_DIR" ]; then
    # Check if we're running interactively or piped
    if [ -t 0 ]; then
        # Interactive mode - can read user input
        echo -e "${YELLOW}Directory '$INSTALL_DIR' already exists${NC}"
        read -p "Would you like to override? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            # Default to Yes (Y or Enter or any other key)
            echo -e "${YELLOW}Removing existing directory...${NC}"
            rm -rf "$INSTALL_DIR"
        else
            echo -e "${YELLOW}Installation cancelled${NC}"
            exit 0
        fi
    else
        # Non-interactive mode (piped) - auto-remove with warning
        echo -e "${YELLOW}Directory '$INSTALL_DIR' already exists${NC}"
        echo -e "${YELLOW}Auto-removing for fresh install (non-interactive mode)...${NC}"
        rm -rf "$INSTALL_DIR"
    fi
fi

# Clone the repository to the specific location
echo -e "${GREEN}📥 Cloning repository to $INSTALL_DIR...${NC}"
git clone "$REPO_URL" "$INSTALL_DIR"

# Enter directory and run setup
cd "$INSTALL_DIR"

echo -e "${GREEN}🔧 Running setup...${NC}"
echo

# Make setup.sh executable if it isn't already
chmod +x setup.sh

# Run the setup
./setup.sh