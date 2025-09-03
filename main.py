#!/usr/bin/env python3
"""
Automate Release Notes - Main Application

This is the main entry point for the automated release notes system.
It coordinates git monitoring, LLM processing, and Teams integration.

Author: Auto Release Notes System
Date: August 20, 2025
"""

import os
import sys
import time
import logging
from pathlib import Path

# Import our custom modules
from config import Config
from git_monitor import GitMonitor
from llm_handler import LLMHandler
from teams_integration import TeamsIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('release_notes.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ReleaseNotesAutomator:
    """Main class for automating release notes generation and distribution."""
    
    def __init__(self):
        """Initialize the release notes automator."""
        logger.info("Initializing Release Notes Automator")
        
        # Load configuration
        self.config = Config()
        
        # Initialize components
        self.git_monitor = GitMonitor(self.config)
        self.llm_handler = LLMHandler(self.config)
        self.teams_integration = TeamsIntegration(self.config)
        
        # Track last processed commit
        self.last_commit_hash = self._get_last_processed_commit()
        
        logger.info("Release Notes Automator initialized successfully")
    
    def _get_last_processed_commit(self):
        """Get the hash of the last processed commit."""
        try:
            with open('.last_commit', 'r') as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def _save_last_processed_commit(self, commit_hash):
        """Save the hash of the last processed commit."""
        with open('.last_commit', 'w') as f:
            f.write(commit_hash)
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring of git commits."""
        logger.info("Starting continuous monitoring mode")
        
        while True:
            try:
                self.process_new_commits()
                time.sleep(self.config.MONITORING_INTERVAL)
            except KeyboardInterrupt:
                logger.info("Stopping continuous monitoring")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def process_new_commits(self):
        """Process any new commits since last check."""
        try:
            # Get new commits
            new_commits = self.git_monitor.get_commits_since(self.last_commit_hash)
            
            if not new_commits:
                logger.debug("No new commits found")
                return
            
            logger.info(f"Found {len(new_commits)} new commits to process")
            
            # Process each commit
            for commit in new_commits:
                self._process_single_commit(commit)
            
            # Update last processed commit
            if new_commits:
                self.last_commit_hash = new_commits[0]['hash']
                self._save_last_processed_commit(self.last_commit_hash)
                
        except Exception as e:
            logger.error(f"Error processing new commits: {e}")
    
    def _process_single_commit(self, commit):
        """Process a single commit for release notes generation."""
        try:
            logger.info(f"Processing commit: {commit['hash'][:8]} - {commit['message'][:50]}...")
            
            # Extract commit changes
            changes = self.git_monitor.get_commit_changes(commit['hash'])
            
            # Generate release notes with LLM
            release_notes = self.llm_handler.generate_release_notes(
                commit, changes
            )
            
            # Update README if needed
            if self._should_update_readme(commit, changes):
                self._update_readme(commit, changes, release_notes)
            
            # Send to Teams if configured
            if self.config.TEAMS_WEBHOOK_URL:
                self.teams_integration.send_release_notes(
                    commit, release_notes
                )
            
            logger.info(f"Successfully processed commit {commit['hash'][:8]}")
            
        except Exception as e:
            logger.error(f"Error processing commit {commit['hash'][:8]}: {e}")
    
    def _should_update_readme(self, commit, changes):
        """Determine if README should be updated based on commit changes."""
        # Update README for:
        # - New features
        # - Major changes
        # - Version updates
        # - Documentation changes
        
        significant_keywords = [
            'feature', 'add', 'new', 'version', 'release',
            'update', 'improve', 'enhance', 'docs', 'readme'
        ]
        
        message_lower = commit['message'].lower()
        return any(keyword in message_lower for keyword in significant_keywords)
    
    def _update_readme(self, commit, changes, release_notes):
        """Update README.md with new information."""
        try:
            logger.info("Updating README.md")
            
            # Read current README
            readme_path = Path('README.md')
            if readme_path.exists():
                with open(readme_path, 'r', encoding='utf-8') as f:
                    current_readme = f.read()
            else:
                current_readme = ""
            
            # Generate updated README content
            updated_readme = self.llm_handler.update_readme(
                current_readme, commit, changes, release_notes
            )
            
            # Write updated README
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_readme)
            
            logger.info("README.md updated successfully")
            
        except Exception as e:
            logger.error(f"Error updating README: {e}")
    
    def generate_manual_release_notes(self, start_commit=None, end_commit=None):
        """Generate release notes manually for a specific range of commits."""
        try:
            logger.info("Generating manual release notes")
            
            # Get commits in range
            commits = self.git_monitor.get_commits_in_range(start_commit, end_commit)
            
            if not commits:
                logger.info("No commits found in specified range")
                return
            
            # Generate comprehensive release notes
            all_changes = []
            for commit in commits:
                changes = self.git_monitor.get_commit_changes(commit['hash'])
                all_changes.extend(changes)
            
            release_notes = self.llm_handler.generate_comprehensive_release_notes(
                commits, all_changes
            )
            
            # Save to file
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'release_notes_{timestamp}.md'
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(release_notes)
            
            logger.info(f"Release notes saved to {filename}")
            
            # Send to Teams if configured
            if self.config.TEAMS_WEBHOOK_URL:
                self.teams_integration.send_manual_release_notes(
                    release_notes, commits
                )
            
            return filename
            
        except Exception as e:
            logger.error(f"Error generating manual release notes: {e}")
            return None

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Automate Release Notes Generation and Distribution'
    )
    parser.add_argument(
        '--mode', 
        choices=['monitor', 'manual'], 
        default='monitor',
        help='Run in continuous monitoring mode or generate manual release notes'
    )
    parser.add_argument(
        '--start-commit',
        help='Start commit hash for manual release notes generation'
    )
    parser.add_argument(
        '--end-commit',
        help='End commit hash for manual release notes generation'
    )
    
    args = parser.parse_args()
    
    # Check if we're in a git repository
    if not Path('.git').exists():
        logger.error("Not in a git repository. Please run from the root of your git project.")
        sys.exit(1)
    
    # Initialize the automator
    try:
        automator = ReleaseNotesAutomator()
    except Exception as e:
        logger.error(f"Failed to initialize Release Notes Automator: {e}")
        sys.exit(1)
    
    # Run based on mode
    try:
        if args.mode == 'monitor':
            logger.info("Starting in continuous monitoring mode")
            automator.run_continuous_monitoring()
        elif args.mode == 'manual':
            logger.info("Generating manual release notes")
            filename = automator.generate_manual_release_notes(
                args.start_commit, args.end_commit
            )
            if filename:
                print(f"Release notes generated: {filename}")
            else:
                print("Failed to generate release notes")
                sys.exit(1)
    except Exception as e:
        logger.error(f"Error running application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
