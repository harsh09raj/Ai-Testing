#!/usr/bin/env python3
"""
Configuration Management for Automate Release Notes

Handles all configuration settings including OpenAI credentials,
Teams webhook settings, and application parameters.

Author: Auto Release Notes System
Date: August 20, 2025
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json

class Config:
    """Configuration manager for the Release Notes Automator."""
    
    def __init__(self, config_file: str = 'config.json'):
        """Initialize configuration from environment variables and config file."""
        self.config_file = Path(config_file)
        self._load_config()
        self._validate_config()
    
    def _load_config(self):
        """Load configuration from environment variables and config file."""
        # Default configuration
        self.config = {
            'openai': {
                'api_key': None,
                'model': 'gpt-5',
                'deployment_name': 'gpt 5',  # Azure deployment name
                'max_tokens': 4000,
                'temperature': 0.3,
                'timeout': 60
            },
            'teams': {
                'webhook_url': None,
                'channel_name': 'Release Notes',
                'mention_users': [],
                'enable_notifications': True
            },
            'git': {
                'default_branch': 'main',
                'ignore_patterns': ['.git', '__pycache__', '*.pyc', '.env'],
                'file_extensions': ['.py', '.js', '.ts', '.java', '.go', '.cpp', '.h']
            },
            'monitoring': {
                'interval_seconds': 300,  # 5 minutes
                'max_commits_per_check': 10,
                'enable_continuous_mode': True
            },
            'output': {
                'log_level': 'INFO',
                'log_file': 'release_notes.log',
                'backup_readme': True,
                'output_format': 'markdown'
            }
        }
        
        # Load from config file if exists
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                self._merge_config(self.config, file_config)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        # Override with environment variables
        self._load_from_env()
    
    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]):
        """Recursively merge configuration dictionaries."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        # OpenAI configuration
        if os.getenv('OPENAI_API_KEY'):
            self.config['openai']['api_key'] = os.getenv('OPENAI_API_KEY')
        
        if os.getenv('OPENAI_MODEL'):
            self.config['openai']['model'] = os.getenv('OPENAI_MODEL')
        
        if os.getenv('OPENAI_DEPLOYMENT_NAME'):
            self.config['openai']['deployment_name'] = os.getenv('OPENAI_DEPLOYMENT_NAME')
        
        # Teams configuration
        if os.getenv('TEAMS_WEBHOOK_URL'):
            self.config['teams']['webhook_url'] = os.getenv('TEAMS_WEBHOOK_URL')
        
        if os.getenv('TEAMS_CHANNEL_NAME'):
            self.config['teams']['channel_name'] = os.getenv('TEAMS_CHANNEL_NAME')
        
        # Git configuration
        if os.getenv('GIT_DEFAULT_BRANCH'):
            self.config['git']['default_branch'] = os.getenv('GIT_DEFAULT_BRANCH')
        
        # Monitoring configuration
        if os.getenv('MONITORING_INTERVAL'):
            try:
                self.config['monitoring']['interval_seconds'] = int(os.getenv('MONITORING_INTERVAL'))
            except ValueError:
                pass
        
        # Output configuration
        if os.getenv('LOG_LEVEL'):
            self.config['output']['log_level'] = os.getenv('LOG_LEVEL')
    
    def _validate_config(self):
        """Validate essential configuration parameters."""
        # Check OpenAI API key
        if not self.config['openai']['api_key']:
            print("Warning: OpenAI API key not configured. Set OPENAI_API_KEY environment variable or add to config.json")
        
        # Validate model name
        if not self.config['openai']['model']:
            raise ValueError("OpenAI model not specified")
        
        # Validate monitoring interval
        if self.config['monitoring']['interval_seconds'] < 60:
            print("Warning: Monitoring interval is less than 60 seconds. This may cause rate limiting.")
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def create_sample_config(self):
        """Create a sample configuration file."""
        sample_config = {
            "openai": {
                "api_key": "your-openai-api-key-here",
                "model": "gpt-5",
                "deployment_name": "gpt 5",
                "max_tokens": 4000,
                "temperature": 0.3
            },
            "teams": {
                "webhook_url": "https://your-org.webhook.office.com/webhookb2/your-webhook-url",
                "channel_name": "Release Notes",
                "mention_users": ["@channel"],
                "enable_notifications": True
            },
            "git": {
                "default_branch": "main",
                "ignore_patterns": [".git", "__pycache__", "*.pyc", ".env"]
            },
            "monitoring": {
                "interval_seconds": 300,
                "max_commits_per_check": 10
            }
        }
        
        sample_file = 'config.sample.json'
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2)
        
        print(f"Sample configuration created: {sample_file}")
        print("Copy this to config.json and update with your credentials.")
    
    # Properties for easy access to configuration values
    @property
    def OPENAI_API_KEY(self) -> Optional[str]:
        return self.config['openai']['api_key']
    
    @property
    def OPENAI_MODEL(self) -> str:
        return self.config['openai']['model']
    
    @property
    def OPENAI_DEPLOYMENT_NAME(self) -> str:
        return self.config['openai']['deployment_name']
    
    @property
    def OPENAI_MAX_TOKENS(self) -> int:
        return self.config['openai']['max_tokens']
    
    @property
    def OPENAI_TEMPERATURE(self) -> float:
        return self.config['openai']['temperature']
    
    @property
    def OPENAI_TIMEOUT(self) -> int:
        return self.config['openai']['timeout']
    
    @property
    def TEAMS_WEBHOOK_URL(self) -> Optional[str]:
        return self.config['teams']['webhook_url']
    
    @property
    def TEAMS_CHANNEL_NAME(self) -> str:
        return self.config['teams']['channel_name']
    
    @property
    def TEAMS_MENTION_USERS(self) -> list:
        return self.config['teams']['mention_users']
    
    @property
    def TEAMS_ENABLE_NOTIFICATIONS(self) -> bool:
        return self.config['teams']['enable_notifications']
    
    @property
    def GIT_DEFAULT_BRANCH(self) -> str:
        return self.config['git']['default_branch']
    
    @property
    def GIT_IGNORE_PATTERNS(self) -> list:
        return self.config['git']['ignore_patterns']
    
    @property
    def GIT_FILE_EXTENSIONS(self) -> list:
        return self.config['git']['file_extensions']
    
    @property
    def MONITORING_INTERVAL(self) -> int:
        return self.config['monitoring']['interval_seconds']
    
    @property
    def MAX_COMMITS_PER_CHECK(self) -> int:
        return self.config['monitoring']['max_commits_per_check']
    
    @property
    def ENABLE_CONTINUOUS_MODE(self) -> bool:
        return self.config['monitoring']['enable_continuous_mode']
    
    @property
    def LOG_LEVEL(self) -> str:
        return self.config['output']['log_level']
    
    @property
    def LOG_FILE(self) -> str:
        return self.config['output']['log_file']
    
    @property
    def BACKUP_README(self) -> bool:
        return self.config['output']['backup_readme']
    
    @property
    def OUTPUT_FORMAT(self) -> str:
        return self.config['output']['output_format']
    
    def get_openai_config(self) -> Dict[str, Any]:
        """Get OpenAI configuration as a dictionary."""
        return self.config['openai'].copy()
    
    def get_teams_config(self) -> Dict[str, Any]:
        """Get Teams configuration as a dictionary."""
        return self.config['teams'].copy()
    
    def get_git_config(self) -> Dict[str, Any]:
        """Get Git configuration as a dictionary."""
        return self.config['git'].copy()
    
    def print_config_status(self):
        """Print current configuration status."""
        print("\n=== Configuration Status ===")
        print(f"OpenAI API Key: {'✓ Configured' if self.OPENAI_API_KEY else '✗ Not configured'}")
        print(f"OpenAI Model: {self.OPENAI_MODEL}")
        print(f"Teams Webhook: {'✓ Configured' if self.TEAMS_WEBHOOK_URL else '✗ Not configured'}")
        print(f"Teams Channel: {self.TEAMS_CHANNEL_NAME}")
        print(f"Git Branch: {self.GIT_DEFAULT_BRANCH}")
        print(f"Monitoring Interval: {self.MONITORING_INTERVAL} seconds")
        print(f"Log Level: {self.LOG_LEVEL}")
        print("========================\n")

def main():
    """CLI interface for configuration management."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Configuration management for Release Notes Automator'
    )
    parser.add_argument(
        '--create-sample', 
        action='store_true',
        help='Create a sample configuration file'
    )
    parser.add_argument(
        '--status', 
        action='store_true',
        help='Show current configuration status'
    )
    parser.add_argument(
        '--config-file', 
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    
    args = parser.parse_args()
    
    config = Config(args.config_file)
    
    if args.create_sample:
        config.create_sample_config()
    elif args.status:
        config.print_config_status()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
