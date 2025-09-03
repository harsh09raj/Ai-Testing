#!/usr/bin/env python3
"""
README Update Script

This script scans the 'app' directory for Python files, analyzes their
functions and dependencies, and updates the README.md file with:
1. A summary section for all files in the 'app' directory
2. A section listing all dependencies used in the app

Usage:
    python update_readme.py
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime


class PythonFileAnalyzer:
    """Analyzes Python files to extract information about functions and imports."""
    
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.content = ""
        self.imports = set()
        self.functions = []
        self.classes = []
        self.docstring = ""
        
    def analyze(self):
        """Analyze the Python file for imports, functions, and documentation."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            # Parse the AST
            tree = ast.parse(self.content)
            
            # Extract module docstring
            if (tree.body and isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                self.docstring = tree.body[0].value.value.strip()
            
            # Walk through the AST
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self.imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self.imports.add(node.module.split('.')[0])
                elif isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or 'No description available'
                    }
                    self.functions.append(func_info)
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'docstring': ast.get_docstring(node) or 'No description available'
                    }
                    self.classes.append(class_info)
                    
        except Exception as e:
            print(f"Error analyzing {self.file_path}: {e}")
    
    def get_summary(self) -> str:
        """Generate a summary of the file."""
        if self.docstring:
            # Extract first line of docstring as summary
            first_line = self.docstring.split('\n')[0].strip()
            if first_line:
                return first_line
        
        # Fallback to analyzing functions and classes
        if self.functions or self.classes:
            purpose_parts = []
            if self.functions:
                purpose_parts.append(f"Contains {len(self.functions)} function(s)")
            if self.classes:
                purpose_parts.append(f"Contains {len(self.classes)} class(es)")
            return " and ".join(purpose_parts)
        
        return "Python module"


class ReadmeUpdater:
    """Updates README.md with app directory analysis."""
    
    def __init__(self, app_dir: str = "app", readme_path: str = "README.md"):
        self.app_dir = Path(app_dir)
        self.readme_path = Path(readme_path)
        self.python_files = []
        self.all_dependencies = set()
        self.builtin_modules = {
            'os', 'sys', 'datetime', 'time', 'json', 'csv', 'math', 'random',
            'collections', 'itertools', 'functools', 'operator', 'pathlib',
            'typing', 'enum', 'dataclasses', 'logging', 'argparse', 'configparser',
            're', 'urllib', 'http', 'socket', 'threading', 'multiprocessing',
            'subprocess', 'tempfile', 'shutil', 'glob', 'fnmatch', 'linecache',
            'pickle', 'copy', 'pprint', 'textwrap', 'string', 'difflib', 'hashlib',
            'hmac', 'uuid', 'ast', 'dis', 'inspect', 'gc', 'weakref', 'abc'
        }
    
    def scan_app_directory(self):
        """Scan the app directory for Python files."""
        if not self.app_dir.exists():
            print(f"App directory '{self.app_dir}' does not exist.")
            return
        
        print(f"Scanning {self.app_dir} for Python files...")
        
        for py_file in self.app_dir.glob('**/*.py'):
            if py_file.name != '__pycache__':
                print(f"Analyzing {py_file}...")
                analyzer = PythonFileAnalyzer(py_file)
                analyzer.analyze()
                
                self.python_files.append(analyzer)
                self.all_dependencies.update(analyzer.imports)
    
    def get_third_party_dependencies(self) -> Set[str]:
        """Filter out built-in modules to get third-party dependencies."""
        return {dep for dep in self.all_dependencies if dep not in self.builtin_modules}
    
    def read_requirements_txt(self) -> Set[str]:
        """Read dependencies from requirements.txt if it exists."""
        req_file = Path('requirements.txt')
        dependencies = set()
        
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Extract package name (before version specifier)
                            package = re.split(r'[>=<!=]', line)[0].strip()
                            dependencies.add(package)
            except Exception as e:
                print(f"Error reading requirements.txt: {e}")
        
        return dependencies
    
    def generate_app_summary_section(self) -> str:
        """Generate the app summary section for README."""
        if not self.python_files:
            return "\n## App Directory\n\nNo Python files found in the app directory.\n"
        
        section = "\n## App Directory\n\n"
        section += "The `app` directory contains the following Python files:\n\n"
        
        for analyzer in sorted(self.python_files, key=lambda x: x.file_path.name):
            relative_path = analyzer.file_path.relative_to(Path.cwd())
            section += f"### {relative_path}\n\n"
            section += f"**Purpose:** {analyzer.get_summary()}\n\n"
            
            if analyzer.functions:
                section += "**Functions:**\n"
                for func in analyzer.functions:
                    # Clean up docstring for display
                    doc_summary = func['docstring'].split('\n')[0].strip()
                    section += f"- `{func['name']}()`: {doc_summary}\n"
                section += "\n"
            
            if analyzer.classes:
                section += "**Classes:**\n"
                for cls in analyzer.classes:
                    doc_summary = cls['docstring'].split('\n')[0].strip()
                    section += f"- `{cls['name']}`: {doc_summary}\n"
                section += "\n"
        
        return section
    
    def generate_dependencies_section(self) -> str:
        """Generate the dependencies section for README."""
        section = "\n## Dependencies\n\n"
        
        # Get third-party dependencies from code analysis
        code_deps = self.get_third_party_dependencies()
        
        # Get dependencies from requirements.txt
        req_deps = self.read_requirements_txt()
        
        # Combine both sources
        all_deps = code_deps.union(req_deps)
        
        if not all_deps:
            section += "This project uses only Python standard library modules.\n"
        else:
            section += "This project depends on the following third-party packages:\n\n"
            for dep in sorted(all_deps):
                section += f"- `{dep}`"
                if dep in req_deps:
                    section += " (listed in requirements.txt)"
                if dep in code_deps:
                    section += " (imported in code)"
                section += "\n"
            
            section += "\nTo install dependencies, run:\n"
            section += "```bash\n"
            section += "pip install -r requirements.txt\n"
            section += "```\n"
        
        return section
    
    def update_readme(self):
        """Update the README.md file with app directory and dependencies information."""
        print("Updating README.md...")
        
        # Read existing README
        readme_content = ""
        if self.readme_path.exists():
            with open(self.readme_path, 'r', encoding='utf-8') as f:
                readme_content = f.read()
        
        # Generate new sections
        app_section = self.generate_app_summary_section()
        deps_section = self.generate_dependencies_section()
        
        # Remove existing sections if they exist
        # Pattern to match our generated sections
        app_pattern = r'\n## App Directory\n.*?(?=\n## |$)'
        deps_pattern = r'\n## Dependencies\n.*?(?=\n## |$)'
        
        readme_content = re.sub(app_pattern, '', readme_content, flags=re.DOTALL)
        readme_content = re.sub(deps_pattern, '', readme_content, flags=re.DOTALL)
        
        # Add new sections at the end
        updated_content = readme_content.rstrip() + app_section + deps_section
        
        # Add update timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_content += f"\n---\n*This README was automatically updated on {timestamp} by update_readme.py*\n"
        
        # Write updated README
        with open(self.readme_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"README.md has been updated with {len(self.python_files)} Python files and {len(self.get_third_party_dependencies())} third-party dependencies.")


def main():
    """Main function to run the README updater."""
    print("Starting README update process...")
    
    updater = ReadmeUpdater()
    
    # Scan the app directory
    updater.scan_app_directory()
    
    # Update the README
    updater.update_readme()
    
    print("README update completed successfully!")


if __name__ == "__main__":
    main()
