#!/usr/bin/env python3
"""
Repository Documentation Generator Script - genrate_for_this_repo.py

USAGE:
    python genrate_for_this_repo.py
    
PURPOSE:
    This script summarizes every file in the repository EXCEPT those in the 'app' directory.
    It generates beginner-friendly summaries using Azure OpenAI and updates the root README.md
    with documentation for all non-app files.
    
PREREQUISITES:
    - Azure OpenAI credentials must be set in .env file:
      * OPENAI_API_KEY
      * OPENAI_API_BASE  
      * OPENAI_API_VERSION
      * OPENAI_DEPLOYMENT_NAME
    - Required packages: openai, python-dotenv
    
OUTPUT:
    - Updates root README.md with summaries of all files except those in app/
    - Creates comprehensive documentation for the entire repository structure
"""

import os
import openai
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Azure OpenAI configuration (same as other scripts)
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
api_version = os.getenv("OPENAI_API_VERSION")
deployment = os.getenv("OPENAI_DEPLOYMENT_NAME")

# Configure OpenAI for Azure
openai.api_type = 'azure'
openai.api_key = api_key
openai.api_base = api_base
openai.api_version = api_version

def summarize_file(filepath):
    """
    Generate a beginner-friendly summary of a file using Azure OpenAI.
    
    Args:
        filepath (str): Path to the file to summarize
        
    Returns:
        str: AI-generated summary of the file
    """
    try:
        with open(filepath, 'r', encoding="utf-8", errors="replace") as file:
            content = file.read(1500)  # Read first 1500 characters
            
        prompt = (
            f"I have a project file at '{filepath}'. Here is a snippet of its content:\n"
            f"-----\n{content}\n-----\n"
            "Explain in simple, beginner-friendly language what this file is for, what it does, and how it fits in the project."
        )
        
        response = openai.ChatCompletion.create(
            engine=deployment,
            messages=[
                {"role": "system", "content": "You are a helpful project documentation tool."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Could not summarize {filepath}: {str(e)}"

def list_all_files_except_app():
    """
    List all files in the repository except those in the 'app' directory.
    
    Returns:
        list: List of file paths excluding app directory and common ignore patterns
    """
    skipped_dirs = {".git", "__pycache__", "env", "venv", ".idea", ".vscode", ".pytest_cache", "app"}
    skipped_files = {".env", ".DS_Store"}
    files = []
    
    for root, dirs, filenames in os.walk("."):
        # Remove skipped directories from the walk
        dirs[:] = [d for d in dirs if d not in skipped_dirs]
        
        for name in filenames:
            if name in skipped_files or name.endswith('.pyc'):
                continue
                
            path = os.path.join(root, name)
            # Normalize path and remove leading './'
            path = path.replace("\\", "/")
            if path.startswith("./"):
                path = path[2:]
            
            # Skip if path contains any skipped directory
            if not any(skip in path for skip in skipped_dirs):
                files.append(path)
    
    return sorted(files)

def generate_table_of_contents(files):
    """
    Generate a table of contents for the README.
    
    Args:
        files (list): List of file paths
        
    Returns:
        str: Formatted table of contents
    """
    toc_lines = []
    for fp in files:
        if not fp.endswith(('.md', '.txt')):  # Skip documentation files in TOC
            # Create anchor link (GitHub style)
            anchor = fp.replace('.', '').replace('/', '').replace('_', '').replace('-', '').lower()
            toc_lines.append(f"- [{fp}](#{anchor})")
    
    return "\n".join(toc_lines)

def update_root_readme(files):
    """
    Update the root README.md with summaries of all non-app files.
    
    Args:
        files (list): List of file paths to document
    """
    print("Generating documentation for all non-app files...")
    
    doc_sections = []
    processed_files = []
    
    for fp in files:
        if fp.endswith(('.md', '.txt')):
            print(f"Skipping documentation file: {fp}")
            continue
            
        print(f"Summarizing: {fp}")
        summary = summarize_file(fp)
        
        # Create anchor-friendly heading
        anchor = fp.replace('.', '').replace('/', '').replace('_', '').replace('-', '').lower()
        section = f"### {fp}\n\n{summary}\n"
        doc_sections.append(section)
        processed_files.append(fp)
    
    # Generate table of contents
    toc = generate_table_of_contents(processed_files)
    
    # Create the complete README content
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    readme_content = f"""# Repository Documentation (Auto-Generated)

This README is auto-generated and documents all files in the repository EXCEPT those in the 'app' directory. It explains every file in simple language, so anyone can quickly understand the purpose of each file in the project.

*Last updated: {timestamp}*

## Table of Contents

{toc}

---

{"---".join(doc_sections)}

---

## How to Regenerate This Documentation

To update this README with the latest file summaries, run:

```bash
python genrate_for_this_repo.py
```

*Note: This script processes all files EXCEPT those in the 'app' directory. Azure OpenAI credentials must be configured in your .env file.*
"""
    
    # Write to root README.md
    readme_path = "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"\n✅ Updated {readme_path} with documentation for {len(processed_files)} files.")
    print(f"📁 Documented files: {', '.join(processed_files)}")

def main():
    """
    Main function to execute the documentation generation process.
    """
    print("🚀 Starting repository documentation generation (excluding app directory)...")
    
    # Verify Azure OpenAI configuration
    if not all([api_key, api_base, api_version, deployment]):
        print("❌ Error: Missing Azure OpenAI configuration in .env file.")
        print("Required variables: OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_API_VERSION, OPENAI_DEPLOYMENT_NAME")
        return
    
    print("✅ Azure OpenAI configuration found.")
    
    # Get all files except those in app directory
    all_files = list_all_files_except_app()
    
    if not all_files:
        print("❌ No files found to document.")
        return
    
    print(f"📋 Found {len(all_files)} files to process (excluding app directory):")
    for f in all_files[:10]:  # Show first 10 files
        print(f"   - {f}")
    if len(all_files) > 10:
        print(f"   ... and {len(all_files) - 10} more files")
    
    # Update README.md with summaries
    update_root_readme(all_files)
    
    print("\n🎯 Repository documentation generation completed successfully!")
    print("📖 The root README.md now contains summaries of all non-app files.")
    print("\n💡 To include app directory files in documentation, use the existing generate_docs_and_release.py script.")

if __name__ == "__main__":
    main()
