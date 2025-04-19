#!/usr/bin/env python
"""
Automated backup system for Empire - syncs to GitHub repository
"""
import os
import sys
import logging
import subprocess
import time
import argparse
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'backup.log'))
    ]
)
logger = logging.getLogger('empire-backup')

def check_git_installed():
    """Check if git is installed and available"""
    try:
        subprocess.run(['git', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("Git not found. Please install Git to use the backup system.")
        return False

def is_git_repository(path):
    """Check if the path is a git repository"""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            cwd=path,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return result.returncode == 0
    except subprocess.SubprocessError:
        return False

def setup_git_repository(path, remote_url=None):
    """Initialize git repository if needed"""
    if not is_git_repository(path):
        logger.info(f"Initializing git repository at {path}")
        try:
            # Initialize the repository
            subprocess.run(['git', 'init'], cwd=path, check=True)
            
            # Create .gitignore if it doesn't exist
            gitignore_path = os.path.join(path, '.gitignore')
            if not os.path.exists(gitignore_path):
                with open(gitignore_path, 'w') as f:
                    f.write("""
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Environment variables
.env
.venv
env/
venv/
ENV/
.vscode/mcp.json

# Logs
logs/
*.log

# Local configuration
instance/

# Runtime data
.pytest_cache/
.coverage
htmlcov/
                    """)
                    
            # Initial commit
            subprocess.run(['git', 'add', '.'], cwd=path, check=True)
            subprocess.run(['git', 'commit', '-m', 'Initial commit from backup system'], cwd=path, check=True)
            
            # Add remote if provided
            if remote_url:
                subprocess.run(['git', 'remote', 'add', 'origin', remote_url], cwd=path, check=True)
                
            logger.info("Git repository setup complete")
            
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to set up git repository: {str(e)}")
            return False
            
    return True

def create_backup(path, branch="main", push=False, remote="origin"):
    """Create a backup by committing and optionally pushing changes"""
    if not is_git_repository(path):
        logger.error(f"Not a git repository: {path}")
        return False
        
    try:
        # Check if there are any changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'], 
            cwd=path, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        
        if not result.stdout.strip():
            logger.info("No changes detected, backup not needed")
            return True
            
        # Create a backup branch if not on main branch
        current_branch = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=path, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            universal_newlines=True
        ).stdout.strip()
        
        if current_branch != branch:
            logger.info(f"Creating backup from branch: {current_branch}")
            backup_branch = f"backup-{current_branch}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            subprocess.run(['git', 'checkout', '-b', backup_branch], cwd=path, check=True)
        
        # Stage all changes
        subprocess.run(['git', 'add', '-A'], cwd=path, check=True)
        
        # Commit changes
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        commit_message = f"Automated backup - {timestamp}"
        subprocess.run(['git', 'commit', '-m', commit_message], cwd=path, check=True)
        
        logger.info(f"Created backup commit: {commit_message}")
        
        # Push to remote if requested
        if push:
            logger.info(f"Pushing to {remote}/{branch}")
            try:
                subprocess.run(['git', 'push', remote, branch], cwd=path, check=True)
                logger.info("Push successful")
            except subprocess.SubprocessError as e:
                logger.error(f"Failed to push to remote: {str(e)}")
                return False
                
        return True
        
    except subprocess.SubprocessError as e:
        logger.error(f"Backup failed: {str(e)}")
        return False

def run_scheduled_backup(path, interval_minutes, branch="main", push=False, remote="origin"):
    """Run backups at scheduled intervals"""
    logger.info(f"Starting scheduled backup every {interval_minutes} minutes")
    logger.info(f"Repository path: {path}")
    logger.info(f"Push to remote: {'Yes' if push else 'No'}")
    
    if push:
        logger.info(f"Remote: {remote}, Branch: {branch}")
    
    try:
        while True:
            logger.info("Running scheduled backup...")
            create_backup(path, branch, push, remote)
            logger.info(f"Next backup in {interval_minutes} minutes")
            time.sleep(interval_minutes * 60)
    except KeyboardInterrupt:
        logger.info("Backup scheduler stopped by user")
        sys.exit(0)

def main():
    """Main entry point for backup script"""
    parser = argparse.ArgumentParser(description='Empire backup system')
    parser.add_argument('--path', default=os.getcwd(), help='Path to the repository')
    parser.add_argument('--remote', help='Git remote URL (for initial setup)')
    parser.add_argument('--branch', default='main', help='Branch to commit to')
    parser.add_argument('--push', action='store_true', help='Push to remote after backup')
    parser.add_argument('--schedule', type=int, help='Schedule backups every N minutes')
    parser.add_argument('--setup', action='store_true', help='Only setup repository, don\'t create backup')
    
    args = parser.parse_args()
    
    if not check_git_installed():
        sys.exit(1)
    
    # Set up repository if needed
    if not setup_git_repository(args.path, args.remote):
        sys.exit(1)
        
    if args.setup:
        logger.info("Repository setup complete")
        sys.exit(0)
    
    # Run scheduled backups if requested
    if args.schedule:
        run_scheduled_backup(args.path, args.schedule, args.branch, args.push, 'origin')
    else:
        # Run a single backup
        success = create_backup(args.path, args.branch, args.push, 'origin')
        if not success:
            sys.exit(1)
        
    logger.info("Backup completed successfully")

if __name__ == "__main__":
    main()
