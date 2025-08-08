#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def get_org_from_repos(repositories):
    """Extract GitHub organization from repository URLs."""
    for repo_config in repositories.values():
        url = repo_config.get('url', '')
        if url.startswith('https://github.com/'):
            # Extract org from URL: https://github.com/org/repo
            parts = url.replace('https://github.com/', '').split('/')
            if parts and parts[0]:
                return parts[0]
    
    # No valid GitHub URLs found in config
    print("❌ Error: Could not determine GitHub organization from repository URLs.")
    print("   Please ensure at least one repository has a valid GitHub URL in config.json")
    sys.exit(1)

# Load configuration from JSON file
def load_config():
    """Load repository configuration from JSON file in current directory."""
    config_path = Path.cwd() / "cae_config.json"
    
    if not config_path.exists():
        print(f"❌ Error: Configuration file not found: {config_path}")
        print("   Please create a cae_config.json file in your project root directory")
        print("   See https://github.com/kgn/claude_agent_environment for configuration examples")
        sys.exit(1)
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            return config
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing configuration file: {e}")
        print("   Please check that your cae_config.json file contains valid JSON.")
        sys.exit(1)

# Global configuration variables (will be loaded in main or set by tests)
CONFIG = None
REPO_MAPPING = {}
REPO_CONFIGS = {}

def initialize_config():
    """Initialize configuration from file."""
    global CONFIG, REPO_MAPPING, REPO_CONFIGS
    CONFIG = load_config()
    REPO_MAPPING = {name: repo['url'] for name, repo in CONFIG['repositories'].items()}
    REPO_CONFIGS = CONFIG['repositories']


def run_command(cmd, cwd=None):
    """Execute a shell command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr


def check_repo_exists(repo_url):
    """Check if a GitHub repository exists using git ls-remote."""
    success, output = run_command(f"git ls-remote {repo_url} HEAD")
    return success


def clone_or_update_repo(repo_name, repo_url, branch_name, base_dir):
    """Clone repo if it doesn't exist, or fetch latest if it does."""
    repo_path = base_dir / repo_name
    
    if repo_path.exists():
        print(f"📁 Repository '{repo_name}' already exists, fetching latest...")
        success, _ = run_command("git fetch --all", cwd=repo_path)
        if not success:
            print(f"❌ Failed to fetch latest for {repo_name}")
            return False
    else:
        print(f"📥 Cloning {repo_name} from {repo_url}...")
        success, output = run_command(f"git clone {repo_url} {repo_path}")
        if not success:
            # Check if it's a 404 error (repository not found)
            if "Repository not found" in output or "404" in output:
                print(f"❌ Repository '{repo_name}' does not exist at {repo_url}")
                print(f"   Please verify the repository name is correct.")
                if repo_name not in REPO_MAPPING:
                    print(f"   Note: '{repo_name}' is not in your cae_config.json, so it was assumed to be a GitHub repository.")
            else:
                print(f"❌ Failed to clone {repo_name}")
                print(f"   Error: {output.strip()}")
            return False
    
    # First check if branch exists locally
    success, local_branches = run_command(
        f"git branch --list {branch_name}",
        cwd=repo_path
    )
    
    branch_exists_locally = bool(local_branches.strip())
    
    # Check if branch exists remotely
    success, output = run_command(
        f"git ls-remote --heads origin {branch_name}", 
        cwd=repo_path
    )
    
    branch_exists_remotely = bool(output.strip())
    
    if branch_exists_locally:
        # Branch already exists locally, just checkout
        print(f"🔄 Switching to existing local branch '{branch_name}' in {repo_name}...")
        success, output = run_command(f"git checkout {branch_name}", cwd=repo_path)
        if not success:
            print(f"❌ Failed to checkout branch {branch_name} in {repo_name}")
            print(f"   Error: {output.strip()}")
            return False
        
        if branch_exists_remotely:
            # Pull latest changes from remote
            print(f"📥 Pulling latest changes from remote...")
            success, output = run_command(f"git pull origin {branch_name}", cwd=repo_path)
            if not success:
                print(f"⚠️  Warning: Could not pull latest changes: {output.strip()}")
    elif branch_exists_remotely:
        # Branch exists remotely but not locally, checkout from remote
        print(f"🔄 Checking out branch '{branch_name}' from remote in {repo_name}...")
        success, output = run_command(f"git checkout -b {branch_name} origin/{branch_name}", cwd=repo_path)
        if not success:
            # Try without -b in case of detached HEAD or other issues
            success, output = run_command(f"git checkout {branch_name}", cwd=repo_path)
            if not success:
                print(f"❌ Failed to checkout branch {branch_name} from remote")
                print(f"   Error: {output.strip()}")
                return False
    else:
        # Branch doesn't exist anywhere, create new one
        print(f"🌿 Creating new branch '{branch_name}' in {repo_name}...")
        # First ensure we're on main/master
        success, output = run_command("git checkout main || git checkout master", cwd=repo_path)
        if not success:
            print(f"❌ Failed to checkout main branch in {repo_name}")
            print(f"   Error: {output.strip()}")
            return False
        
        # Pull latest from main
        run_command("git pull", cwd=repo_path)
        
        # Create and checkout new branch
        success, output = run_command(f"git checkout -b {branch_name}", cwd=repo_path)
        if not success:
            print(f"❌ Failed to create branch {branch_name} in {repo_name}")
            print(f"   Error: {output.strip()}")
            return False
    
    # Run setup command if configured
    repo_config = REPO_CONFIGS.get(repo_name, {})
    setup_cmd = repo_config.get('setup')
    if setup_cmd:
        print(f"🔧 Running setup command for {repo_name}: {setup_cmd}")
        success, output = run_command(setup_cmd, cwd=repo_path)
        if success:
            print(f"✅ Setup completed for {repo_name}")
        else:
            print(f"⚠️  Setup command failed for {repo_name}, but continuing...")
            print(f"   Error: {output}")
    
    print(f"✅ Successfully set up {repo_name} on branch '{branch_name}'")
    return True


def extract_ticket_id(branch_name):
    """Extract Linear ticket ID from branch name."""
    # Common patterns: eng-346-description, ENG-346, eng-346
    parts = branch_name.split('/')[-1].split('-')
    if len(parts) >= 2:
        # Try to find pattern based on configured prefixes
        ticket_prefixes = CONFIG.get('ticket_prefixes', ['eng', 'des', 'ops'])
        for i in range(len(parts) - 1):
            if parts[i].lower() in ticket_prefixes:
                try:
                    int(parts[i + 1])
                    return f"{parts[i]}-{parts[i + 1]}".upper()
                except ValueError:
                    continue
    return None


def load_template():
    """Load the CLAUDE.md template file."""
    # First try current directory, then fall back to package directory
    template_path = Path.cwd() / "claude_template.md"
    if not template_path.exists():
        # Try package directory as fallback
        template_path = Path(__file__).parent / "claude_template.md"
    
    if not template_path.exists():
        # Return a basic fallback template if file doesn't exist
        return """# Multi-Repository Development Task

## Branch Information
- **Branch Name**: `{branch_name}`
{ticket_section}

## Repositories

{repositories_list}

## Task Description

{ticket_reference}
"""
    
    with open(template_path, 'r') as f:
        return f.read()


def create_claude_markdown(branch_name, repos, base_dir):
    """Create CLAUDE.md file with ticket information."""
    ticket_id = extract_ticket_id(branch_name)
    linear_base_url = CONFIG.get('linear_base_url')
    
    # Load the template
    template = load_template()
    
    # Prepare ticket section
    ticket_section = ""
    ticket_reference = f"ticket {ticket_id if ticket_id else '[TICKET_ID]'}"
    
    if ticket_id and linear_base_url:
        ticket_section = f"- **Linear Ticket**: {ticket_id}\n- **Linear URL**: {linear_base_url}/{ticket_id}"
        ticket_reference = f"Linear ticket [{ticket_id}]({linear_base_url}/{ticket_id})"
    elif ticket_id:
        ticket_section = f"- **Linear Ticket**: {ticket_id}"
        ticket_reference = f"ticket {ticket_id}"
    
    # Build repositories list
    repositories_list = ""
    org_name = get_org_from_repos(CONFIG.get('repositories', {}))
    github_base_url = f"https://github.com/{org_name}"
    
    for repo in repos:
        repo_url = REPO_MAPPING.get(repo, f"{github_base_url}/{repo}")
        repositories_list += f"- **{repo}**: {repo_url}\n"
    
    # Build test commands
    test_commands = ""
    for repo in repos:
        config = REPO_CONFIGS.get(repo, {})
        if config.get('test'):
            test_commands += f"\n# {repo}\ncd {repo} && {config['test']}"
    
    # Build build commands
    build_commands = ""
    for repo in repos:
        config = REPO_CONFIGS.get(repo, {})
        if config.get('build'):
            build_commands += f"\n# {repo}\ncd {repo} && {config['build']}"
    
    # Replace placeholders in template
    content = template.format(
        branch_name=branch_name,
        ticket_section=ticket_section,
        ticket_reference=ticket_reference,
        repositories_list=repositories_list.rstrip(),
        test_commands=test_commands if test_commands else "\n# No test commands configured",
        build_commands=build_commands if build_commands else "\n# No build commands configured"
    )
    
    # Write the file
    claude_path = base_dir / "CLAUDE.md"
    with open(claude_path, "w") as f:
        f.write(content)
    
    print(f"📝 Created CLAUDE.md file at {claude_path}")


def main():
    # Initialize configuration
    initialize_config()
    
    # Load available repos from config for help text
    available_repos = ', '.join(CONFIG.get('repositories', {}).keys())
    org_name = get_org_from_repos(CONFIG.get('repositories', {}))
    
    parser = argparse.ArgumentParser(
        description=f"Checkout branches across multiple {org_name} repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  %(prog)s eng-346-implement-feature ios backend
  %(prog)s feature/new-feature frontend backend docs
  
Available repositories:
  {available_repos}
  
You can also use any other repo name and it will try:
  https://github.com/{org_name}/<repo-name>
  
Repositories will be organized in: ./<branch-name-with-hyphens>/
        """
    )
    
    parser.add_argument(
        "branch", 
        help="Branch name to checkout/create"
    )
    parser.add_argument(
        "repos", 
        nargs="+",
        help="Repository names to checkout (e.g., ios backend web)"
    )
    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="Continue with valid repositories if some are not found (non-interactive mode)"
    )
    
    args = parser.parse_args()
    
    # Create directory structure in current directory: ./<branch-name-with-hyphens>
    # Convert slashes to hyphens in branch name for directory
    dir_name = args.branch.replace('/', '-')
    base_dir = Path.cwd() / dir_name
    base_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 Starting multi-repo checkout")
    print(f"📌 Branch: {args.branch}")
    print(f"📁 Directory: {base_dir}")
    print(f"📦 Repositories: {', '.join(args.repos)}")
    print("-" * 50)
    
    # First, validate all repositories exist
    invalid_repos = []
    repo_urls = {}
    org_name = get_org_from_repos(CONFIG.get('repositories', {}))
    github_base_url = f"https://github.com/{org_name}"
    
    print("🔍 Validating repositories...")
    for repo in args.repos:
        repo_url = REPO_MAPPING.get(repo, f"{github_base_url}/{repo}")
        repo_urls[repo] = repo_url
        
        # Skip validation for repos defined in config (assume they're correct)
        if repo in REPO_MAPPING:
            continue
            
        # Check if the repository exists
        if not check_repo_exists(repo_url):
            invalid_repos.append(repo)
    
    if invalid_repos:
        print(f"\n❌ The following repositories could not be found:")
        for repo in invalid_repos:
            print(f"   • {repo} (expected at {repo_urls[repo]})")
        print(f"\n💡 Suggestions:")
        print(f"   1. Check if the repository name is spelled correctly")
        print(f"   2. Verify the repository exists in the {org_name} organization")
        print(f"   3. Add the repository to your cae_config.json if it's in a different location")
        
        # Ask if user wants to continue with valid repos only
        valid_repos = [r for r in args.repos if r not in invalid_repos]
        if valid_repos:
            print(f"\n📋 Valid repositories found: {', '.join(valid_repos)}")
            if args.continue_on_error:
                print("   Continuing with valid repositories (--continue-on-error flag set)")
                args.repos = valid_repos
            else:
                response = input("Continue with valid repositories only? (y/N): ")
                if response.lower() != 'y':
                    return 1
                args.repos = valid_repos
        else:
            print("\n❌ No valid repositories to process.")
            return 1
    
    print()
    success_count = 0
    for repo in args.repos:
        repo_url = repo_urls.get(repo, REPO_MAPPING.get(repo, f"{github_base_url}/{repo}"))
        if clone_or_update_repo(repo, repo_url, args.branch, base_dir):
            success_count += 1
        print()
    
    print("-" * 50)
    print(f"✨ Successfully set up {success_count}/{len(args.repos)} repositories")
    
    # Create CLAUDE.md file in the base directory
    create_claude_markdown(args.branch, args.repos, base_dir)
    
    if success_count == len(args.repos):
        print(f"\n🎉 All repositories set up successfully in {base_dir}!")
        
        # Change to the directory and run Claude
        print(f"\n📂 Changing to {base_dir} and launching Claude...")
        os.chdir(base_dir)
        
        # Launch Claude in the new directory
        # Try common locations for Claude CLI
        claude_paths = [
            "claude",  # In PATH
            os.path.expanduser("~/.claude/local/claude"),  # Common local install
            "/usr/local/bin/claude",  # Common system install
        ]
        
        claude_found = False
        for claude_path in claude_paths:
            try:
                subprocess.run([claude_path], check=False)
                claude_found = True
                break
            except (FileNotFoundError, OSError):
                continue
        
        if not claude_found:
            print("⚠️  Claude CLI not found. Please run 'claude' manually.")
            print(f"📍 You are now in: {base_dir.absolute()}")
        
        return 0
    else:
        print(f"\n⚠️  Some repositories failed to set up")
        return 1


if __name__ == "__main__":
    sys.exit(main())