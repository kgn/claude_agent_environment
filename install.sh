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
DIR_NAME="claude_agent_environment"

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}     Claude Agent Environment (CAE) Installer${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo

# Check if directory already exists
if [ -d "$DIR_NAME" ]; then
    echo -e "${YELLOW}⚠️  Directory '$DIR_NAME' already exists!${NC}"
    echo
    
    # Check if we're running interactively or piped
    if [ -t 0 ]; then
        # Interactive mode - can read user input
        read -p "Do you want to remove it and do a fresh install? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${YELLOW}Removing existing directory...${NC}"
            rm -rf "$DIR_NAME"
            echo -e "${GREEN}✓ Directory removed${NC}"
        else
            echo -e "${YELLOW}Installation cancelled. To update existing installation:${NC}"
            echo "  cd $DIR_NAME && git pull && ./setup.sh"
            exit 0
        fi
    else
        # Non-interactive mode (piped) - exit with instructions
        echo -e "${RED}Cannot proceed: directory already exists${NC}"
        echo
        echo "Please run one of these commands:"
        echo -e "${GREEN}  # For fresh install:${NC}"
        echo "  rm -rf $DIR_NAME && curl -sSL https://raw.githubusercontent.com/kgn/claude_agent_environment/main/install.sh | bash"
        echo
        echo -e "${GREEN}  # To update existing:${NC}"
        echo "  cd $DIR_NAME && git pull && ./setup.sh"
        echo
        echo -e "${GREEN}  # For interactive install (recommended):${NC}"
        echo "  curl -O https://raw.githubusercontent.com/kgn/claude_agent_environment/main/install.sh && bash install.sh"
        exit 1
    fi
fi

# Clone the repository
echo -e "${GREEN}📥 Cloning repository...${NC}"
git clone "$REPO_URL"

# Enter directory and run setup
cd "$DIR_NAME"

echo -e "${GREEN}🔧 Running setup...${NC}"
echo

# Make setup.sh executable if it isn't already
chmod +x setup.sh

# Run the setup
./setup.sh