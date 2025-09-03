"""
Generate Documentation and Release Notes for Target Directory Only
This script uses Azure OpenAI to generate project documentation and release notes.
It processes files within a specified target directory and places documentation in that directory.
Updated for Azure OpenAI integration - uses api_type='azure' and engine parameter.
"""
import os
import openai
from dotenv import load_dotenv
import subprocess
import requests
from datetime import datetime

# Load environment variables
load_dotenv()
api_type = os.getenv("OPENAI_API_TYPE")
api_key = os.getenv("OPENAI_API_KEY")
api_base = os.getenv("OPENAI_API_BASE")
api_version = os.getenv("OPENAI_API_VERSION")
deployment = os.getenv("OPENAI_DEPLOYMENT_NAME")
teams_webhook = os.getenv("TEAMS_WEBHOOK_URL")

# Define the target directory for processing
target_directory = os.getenv("TARGET_DIRECTORY", "app")

# Configure OpenAI for Azure
openai.api_type = api_type
openai.api_key = api_key
openai.api_base = api_base
openai.api_version = api_version

def summarize_file(filepath):
    try:
        with open(filepath, 'r', encoding="utf-8", errors="replace") as file:
            content = file.read(1500)
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

def list_files_in_target_directory():
    """Only list files within the target directory."""
    if not os.path.exists(target_directory):
        print(f"Warning: '{target_directory}' directory does not exist.")
        return []
    
    skipped = {".git", "__pycache__", "env", "venv", ".idea", ".vscode", ".pytest_cache"}
    files = []
    for root, dirs, filenames in os.walk(target_directory):
        dirs[:] = [d for d in dirs if d not in skipped]
        for name in filenames:
            path = os.path.join(root, name)
            if not any(skip in path for skip in skipped) and not path.endswith('.pyc'):
                files.append(path)
    return files

def get_target_commit_info():
    """Get commit information for files in the target directory only."""
    try:
        result = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%B', '--', f'{target_directory}/']
        ).decode().strip()
        if result:
            return result
        else:
            return f"No commits found for {target_directory} directory"
    except subprocess.CalledProcessError:
        return f"Unable to retrieve commit information for {target_directory} directory"

def get_target_commit_diff():
    """Get diff for the latest commit that affected the target directory."""
    try:
        commit_hash = subprocess.check_output(
            ['git', 'log', '-1', '--pretty=%H', '--', f'{target_directory}/']
        ).decode().strip()
        
        if commit_hash:
            result = subprocess.check_output(
                ['git', 'show', '--pretty=medium', '--stat', '--patch', commit_hash, '--', f'{target_directory}/']
            ).decode(errors='replace')
            return result
        else:
            return f"No diffs found for {target_directory} directory"
    except subprocess.CalledProcessError:
        return f"Unable to retrieve diff information for {target_directory} directory"

def generate_release_note(commit_message, commit_diff):
    if not commit_diff.strip():
        return "No meaningful changes detected."

    try:
        prompt = (
            f"Commit message:\n{commit_message}\n\n"
            f"Changes:\n{commit_diff}\n\n"
            "Generate a concise and actionable release note summarizing the meaningful updates in the target directory. "
            "Focus on providing clear information that helps developers and stakeholders understand the changes.\n\n"
            "Include the following details:\n"
            "- A high-level summary of the changes.\n"
            "- The purpose of the changes and the problem they solve.\n"
            "- Any new features, bug fixes, or improvements introduced.\n"
            "- Highlight breaking changes, if any, and how they might affect the system.\n"
            "- Mention any dependencies or configurations that need to be updated.\n\n"
            "Additionally:\n"
            "- Suggest 1–2 possible future improvements or optimizations related to these changes.\n"
            "- Identify the commit type (choose one: Feature, Bugfix, Refactor, Docs, Chore).\n"
            "- Check for any secrets (API keys, tokens, passwords) that may have been committed.\n"
            "- Highlight any potential security risks (e.g., hardcoded credentials, missing input validation, insecure configs).\n"
            "- Provide a summary that can be directly used in a changelog or release note.\n\n"
            "Ensure the output is structured, concise, and developer-friendly."
        )
        response = openai.ChatCompletion.create(
            engine=deployment,
            messages=[
                {"role": "system", "content": "You are a release note generator focusing on target directory changes."},
                {"role": "user", "content": prompt}
            ]
        )
        # Safe extraction of content
        content = response.choices[0].message.content if response and response.choices else None
        if not content:
            return "Release note generation failed: empty response from API"
        return content.strip()
    except Exception as e:
        return f"Release note generation failed: {str(e)}"

def send_to_teams(message):
    if not teams_webhook:
        print("TEAMS_WEBHOOK_URL not configured.")
        return
    resp = requests.post(teams_webhook, json={"text": message})
    if resp.status_code == 200:
        print("Release note sent to Teams.")
    else:
        print(f"Failed to send to Teams: {resp.status_code}: {resp.text}")

def update_target_changelog(commit_message, commit_diff, release_note):
    """Update or create CHANGELOG.md in the target directory."""
    if not release_note or release_note.strip() == "No meaningful changes detected.":
        print("No meaningful changes detected. Skipping changelog update.")
        return  # Skip updating the changelog if no meaningful changes

    changelog_path = os.path.join(target_directory, "CHANGELOG.md")
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    new_entry = f"""
## [{timestamp}] - Latest Changes

### Commit Message
{commit_message}

### Release Notes
{release_note}

### Technical Details
```
{commit_diff}
```

---
"""
    
    if os.path.exists(changelog_path):
        # Read existing changelog
        with open(changelog_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Add new entry at the top (after title if it exists)
        if existing_content.startswith("# Changelog"):
            lines = existing_content.split('\n', 2)
            if len(lines) >= 2:
                updated_content = lines[0] + '\n' + lines[1] + new_entry + '\n'.join(lines[2:])
            else:
                updated_content = existing_content + new_entry
        else:
            updated_content = f"# {target_directory.capitalize()} Directory Changelog\n\nThis changelog documents changes made to files in the '{target_directory}' directory only.\n" + new_entry + existing_content
    else:
        # Create new changelog
        updated_content = f"# {target_directory.capitalize()} Directory Changelog\n\nThis changelog documents changes made to files in the '{target_directory}' directory only.\n" + new_entry
    
    with open(changelog_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"Updated {changelog_path} with latest changes.")

def main():
    print(f"Starting {target_directory} directory documentation and release generation...")
    
    # Ensure target directory exists
    if not os.path.exists(target_directory):
        print(f"Error: '{target_directory}' directory does not exist.")
        return
    
    # README Generation for target directory only
    target_files = list_files_in_target_directory()
    doc_sections = []
    
    for fp in target_files:
        if fp.endswith(('.md', '.txt')):
            continue  # Skip documentation files
        section = f"### {fp}\n\n{summarize_file(fp)}\n"
        doc_sections.append(section)
    
    target_readme = (
        f"# {target_directory.capitalize()} Directory Documentation (Auto-Generated)\n\n"
        f"This README is auto-generated and explains every file in the '{target_directory}' directory in simple language, so anyone can quickly understand the purpose of each file.\n\n"
        "## Table of Contents\n" +
        "".join([f"- [{os.path.basename(fp)}](#{os.path.basename(fp).replace('.', '').replace('/', '').replace('_', '').lower()})\n"
                 for fp in target_files if fp and not fp.endswith(('.md', '.txt'))]) +
        "\n---\n\n"
        + "\n---\n".join(doc_sections)
        + "\n\n*To re-generate this README, run the documentation script.*\n"
        + f"\n*This documentation focuses only on files within the '{target_directory}' directory.*"
    )
    
    target_readme_path = os.path.join(target_directory, "README.md")
    with open(target_readme_path, "w", encoding="utf-8") as f:
        f.write(target_readme)
    print(f"{target_readme_path} updated with explanations for all {target_directory} directory files.")
    
    # Release Note Generation & Teams Notification (target directory only)
    commit_message = get_target_commit_info()
    commit_diff = get_target_commit_diff()

    # Skip release note generation if nothing meaningful
    if not commit_message or "No commits found" in commit_message:
        print(f"No recent commits found for the {target_directory} directory.")
        return

    if not commit_diff or "No diffs found" in commit_diff:
        print("No meaningful changes in commit diff. Skipping release note generation.")
        return

    release_note = generate_release_note(commit_message, commit_diff)
    
    if not release_note or release_note.strip() == "No meaningful changes detected.":
        print("No meaningful changes detected. Skipping changelog update and Teams notification.")
        return  # Skip further steps if no meaningful changes
        
    print(f"\nRelease Note for {target_directory.capitalize()} Directory Changes:\n", release_note)
        
    # Update target directory changelog
    update_target_changelog(commit_message, commit_diff, release_note)
        
    # Send to Teams
    teams_message = f"📱 {target_directory.capitalize()} Directory Update\n\n{release_note}"
    send_to_teams(teams_message)
    
    print(f"\n✅ {target_directory.capitalize()} directory documentation and changelog generation completed!")
    print("📁 Files updated:")
    print(f"   - {target_readme_path}")
    print(f"   - {target_directory}/CHANGELOG.md")
    print(f"\n🎯 This script now operates only on the '{target_directory}' directory as requested.")

if __name__ == "__main__":
    main()
