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
    echo "What would you like to do?"
    echo "  1) Remove existing directory and do fresh install"
    echo "  2) Update existing installation (git pull)"
    echo "  3) Cancel installation"
    echo
    read -p "Please choose (1-3): " choice
    
    case $choice in
        1)
            echo -e "${YELLOW}Removing existing directory...${NC}"
            rm -rf "$DIR_NAME"
            echo -e "${GREEN}✓ Directory removed${NC}"
            ;;
        2)
            echo -e "${YELLOW}Updating existing installation...${NC}"
            cd "$DIR_NAME"
            git pull
            ./setup.sh
            exit 0
            ;;
        3)
            echo -e "${RED}Installation cancelled${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Invalid choice. Installation cancelled${NC}"
            exit 1
            ;;
    esac
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