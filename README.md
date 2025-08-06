# Claude Agent Environment

A powerful tool for managing multi-repository development workflows with Claude AI. This script automates the process of checking out branches across multiple repositories, creating a structured workspace, and launching Claude with contextual information about your development task.

## Features

- 🚀 **Multi-Repository Management**: Clone or update multiple repositories simultaneously
- 🌿 **Smart Branch Handling**: Automatically creates or checks out branches across all repositories
- 📝 **Claude Integration**: Generates CLAUDE.md files with task context and launches Claude CLI
- 🎫 **Ticket Integration**: Extracts ticket IDs from branch names and links to issue trackers
- ⚙️ **Configurable**: JSON-based configuration for easy customization
- 🏗️ **Organized Workspace**: Creates structured directories for each feature/task

## Installation

### Quick Setup (Recommended)

Run this one-line installer:
```bash
curl -sSL https://raw.githubusercontent.com/kgn/claude_agent_environment/main/install.sh | bash
```

Or manually clone and setup:
```bash
git clone https://github.com/kgn/claude_agent_environment.git
cd claude_agent_environment
./setup.sh
```

This will:
- Install the package
- Add `cae` to your PATH automatically
- Provide next steps for configuration

After running, either:
- Open a new terminal window, or
- Run `source ~/.zshrc` (or `~/.bashrc` for bash)

### Manual Installation

#### Option 1: Install as a command-line tool

1. Clone and install the package:
```bash
git clone https://github.com/kgn/claude_agent_environment.git
cd claude_agent_environment
pip install -e .
```

This installs the `cae` command globally.

**Note**: 
- If you get a warning about pip being outdated, upgrade it with: `python3 -m pip install --upgrade pip`
- For user installations, pip may install scripts to a directory not in your PATH (e.g., `~/Library/Python/3.x/bin` on macOS). If `cae` command is not found after installation, add this directory to your PATH or use Option 2 below.

#### Option 2: Use directly from source

1. Clone this repository:
```bash
git clone https://github.com/kgn/claude_agent_environment.git
```

2. Add to your PATH or create an alias:
```bash
alias cae="python3 /path/to/claude_agent_environment/cae"
```

## Setup

1. Navigate to your project root directory (where you want branches to be created):
```bash
cd ~/Development/my-workspace
```

2. Create a `cae_config.json` file in this directory (see example below in Configuration section)

3. Edit `cae_config.json` with your organization's repositories (see Configuration section below)

4. (Optional) Install Claude CLI if you want automatic launching:
```bash
# Follow Claude's installation instructions
```

## Configuration

Edit `cae_config.json` to match your organization's setup:

```json
{
  "repositories": {
    "frontend": {
      "url": "https://github.com/your-org/frontend",
      "type": "node",
      "build": "npm run build",
      "test": "npm run test"
    },
    "backend": {
      "url": "https://github.com/your-org/backend",
      "type": "python",
      "build": "python -m build",
      "test": "pytest"
    },
    "docs": {
      "url": "https://github.com/your-org/documentation",
      "type": "markdown"
    }
  },
  "linear_base_url": "https://linear.app/your-workspace/issue",
  "ticket_prefixes": ["eng", "bug", "feat"]
}
```

### Configuration Fields

- **repositories**: Define your repositories with their URLs and optional build/test commands
  - `url`: GitHub repository URL (required)
  - `type`: Repository type (e.g., node, python, swift)
  - `build`: Build command (optional)
  - `test`: Test command (optional)
- **linear_base_url**: Linear workspace URL for ticket linking (optional)
- **ticket_prefixes**: Prefixes used in your branch naming convention (e.g., eng-123, bug-456)

**Note**: 
- The GitHub organization name is automatically extracted from repository URLs
- Branches are created in the current directory where you run `cae`
- Each branch gets its own subdirectory with all specified repositories

## Usage

### Basic Usage

1. Navigate to your workspace root:
```bash
cd ~/Development/my-workspace
```

2. Check out a branch across multiple repositories:
```bash
cae feature/new-feature frontend backend docs
```

### With Ticket-Based Branches

```bash
cae eng-123-implement-new-feature frontend backend
```

This will:
1. Create a directory structure: `./eng-123-implement-new-feature/` in your current directory
2. Clone or update the specified repositories
3. Check out or create the branch in each repository
4. Generate a CLAUDE.md file with:
   - Branch information
   - Ticket links (if detected)
   - Repository URLs
   - Build and test commands
5. Launch Claude CLI in the workspace directory

### Examples

```bash
# Feature development across frontend and backend
cae feature/user-authentication frontend backend

# Bug fix in mobile app  
cae bug-456-fix-login-crash mobile backend

# Documentation update
cae docs/api-updates docs backend

# Using a Linear ticket ID directly
cae eng-123 frontend backend provider
```

## Directory Structure

After running `cae`, your current directory will contain:

```
my-workspace/
├── cae_config.json        # Your configuration
├── claude_template.md     # Optional custom template
└── feature-branch-name/   # Created by cae
    ├── CLAUDE.md          # Context file for Claude
    ├── frontend/          # Repository 1  
    ├── backend/           # Repository 2
    └── docs/              # Repository 3
```

## CLAUDE.md File

The generated CLAUDE.md file provides Claude with:
- Branch and ticket information
- Links to issue trackers
- Repository URLs
- Build and test commands for each repository
- Task checklist
- Implementation notes

This context helps Claude understand your development environment and provide more accurate assistance.

### Customizing the CLAUDE.md Template

You can customize the CLAUDE.md template by editing `claude_template.md`. The template uses Python string formatting with the following placeholders:

- `{branch_name}` - The current branch name
- `{ticket_section}` - Ticket information (if detected)
- `{ticket_reference}` - Reference to the ticket in text
- `{repositories_list}` - List of repositories with URLs
- `{test_commands}` - Test commands for each repository
- `{build_commands}` - Build commands for each repository

Edit the template to match your team's workflow and documentation style.

## Advanced Usage

### Adding New Repositories

Simply add them to your `config.json`:

```json
"new-service": {
  "url": "https://github.com/your-org/new-service",
  "type": "go",
  "build": "go build ./...",
  "test": "go test ./..."
}
```

### Working with Multiple Projects

You can have different cae_config.json files in different directories:

```bash
# Project A
cd ~/Development/project-a
# Has its own cae_config.json with project-a repositories
cae feature/new-feature frontend backend

# Project B  
cd ~/Development/project-b
# Has its own cae_config.json with project-b repositories
cae feature/new-feature api web mobile
```

### Repository Types

Supported repository types with appropriate build/test commands:
- `node`: Node.js/JavaScript projects
- `python`: Python projects
- `swift`: iOS/macOS projects
- `go`: Go projects
- `rust`: Rust projects
- `java`: Java projects
- `markdown`: Documentation repositories (typically no build/test needed)

### Optional Fields

- **build** and **test**: Commands are optional for each repository. Omit them for repos that don't need building or testing (e.g., documentation)
- **linear_base_url**: Only needed if you use Linear for issue tracking. Omit if using GitHub Issues or other trackers

## Troubleshooting

### Common Installation Issues

#### Outdated pip warning
If you see a warning about pip being outdated:
```bash
python3 -m pip install --upgrade pip
```

#### Permission denied during installation
If pip fails with permission errors, use the `--user` flag:
```bash
pip install -e . --user
```

#### Command not found: cae
After installation, if `cae` command is not found:

1. **Check if it was installed to a non-PATH directory:**
   ```bash
   # macOS
   find ~/Library/Python -name "cae"
   
   # Linux
   find ~/.local/bin -name "cae"
   ```

2. **Add the directory to your PATH:**
   ```bash
   # Add to ~/.zshrc (macOS) or ~/.bashrc (Linux)
   export PATH="$HOME/Library/Python/3.x/bin:$PATH"  # Replace 3.x with your Python version
   ```

3. **Or create an alias:**
   ```bash
   alias cae="/path/to/cae"  # Use the path from step 1
   ```

### Runtime Issues

#### Claude CLI not launching
- Verify Claude is installed: `which claude`
- The script will try to find Claude in common locations
- Try running Claude manually: `cd your-branch && claude`

#### Permission denied when cloning repositories
- Ensure you have SSH keys set up for GitHub
- Or use HTTPS URLs with authentication in your `cae_config.json`

#### Branch already exists
The script will automatically check out existing branches and pull the latest changes.

#### Configuration file not found
Create a `cae_config.json` in your project root directory. See the Configuration section above for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

David Keegan - [davidkeegan.com](https://davidkeegan.com)

## Acknowledgments

- Built for use with [Claude Code](https://www.anthropic.com/claude-code) by Anthropic
- Designed to streamline multi-repository development workflows