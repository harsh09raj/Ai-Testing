# Usage Instructions

This repository contains three main documentation scripts that serve different purposes. Each script uses Azure OpenAI to generate documentation, but they target different parts of the repository and produce different outputs.

## Scripts Overview

| Script | Purpose | Target Files | Output Location |
|--------|---------|--------------|----------------|
| `generate_docs_and_release.py` | Complete repo documentation + release notes | All repository files | Root README.md + Teams notification |
| `generate_app_docs.py` | App-specific documentation | Only `app/` directory Python files | `app/README.md` + `app/CHANGELOG.md` |
| `genrate_for_this_repo.py` | Non-app documentation | All files EXCEPT `app/` directory | Root README.md |

## Web Application Workflow (Node.js + Python + Frontend)

The repository now includes a web application workflow that provides a user-friendly interface for generating release notes through a browser interface.

### Architecture Overview

The webapp consists of three components working together:
- **Python FastAPI Service**: Backend API that handles release note generation
- **Node.js Server**: Middleware server that serves the frontend and forwards API requests
- **Frontend Interface**: HTML/CSS/JS interface for user interaction

### Setup and Usage

#### 1. Start the Python FastAPI Service

```bash
# Navigate to the python_api directory
cd python_api

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI service
python3 main.py
```

The Python service will start on `http://localhost:8000` and provide the API endpoint:
- `POST /api/generate-release-notes` - Generates release notes from repository URL

#### 2. Start the Node.js Server

```bash
# From the repository root
npm install

# Start the Node.js server
node server.js
```

The Node.js server will start on `http://localhost:3000` (or the port specified in `PORT` environment variable).

#### 3. Access the Frontend

Open your web browser and navigate to:
```
http://localhost:3000
```

The frontend interface will be served from the `frontend/` directory and provides:
- Input field for repository URL
- Generate button to trigger release note generation
- Display area for generated release notes
- Loading states and error handling

#### 4. Workflow Behavior

1. **User Input**: Enter a GitHub repository URL in the frontend interface
2. **Request Flow**: Frontend → Node.js server → Python FastAPI service
3. **Processing**: Python service analyzes the repository and generates release notes using AI
4. **Response Flow**: Python service → Node.js server → Frontend
5. **Display**: Generated release notes are displayed in the frontend interface

### Prerequisites for Web Application

#### Environment Setup

Ensure you have the following installed:
- **Python 3.8+** with pip
- **Node.js 14+** with npm
- **Git** (for repository analysis)

#### Configuration Files

The webapp requires the same Azure OpenAI configuration as the command-line scripts:

```bash
# .env file (in python_api directory)
OPENAI_API_KEY=your-azure-openai-key
OPENAI_API_BASE=https://your-azure-resource.openai.azure.com/
OPENAI_API_VERSION=2024-05-13
OPENAI_DEPLOYMENT_NAME=your-deployment-name
```

### Troubleshooting Web Application

#### Common Issues

- **Port conflicts**: Ensure ports 3000 and 8000 are available
- **CORS errors**: The Node.js server handles CORS for frontend-backend communication
- **API connection issues**: Verify the Python FastAPI service is running on port 8000
- **Missing dependencies**: Run `npm install` and `pip install -r python_api/requirements.txt`

#### Service Status Checks

```bash
# Check if Python FastAPI is running
curl http://localhost:8000/docs

# Check if Node.js server is running
curl http://localhost:3000
```

### Integration with Existing Scripts

The web application workflow complements the existing command-line scripts:
- Use the **webapp** for interactive, on-demand release note generation
- Use **command-line scripts** for automated documentation and batch processing
- Both approaches use the same underlying AI-powered release note generation logic

---

## Prerequisites

### Azure OpenAI Configuration

All scripts require Azure OpenAI credentials in your .env file:

```bash
# Azure OpenAI Configuration
OPENAI_API_KEY=your-azure-openai-key
OPENAI_API_BASE=https://your-azure-resource.openai.azure.com/
OPENAI_API_VERSION=model-api-version
OPENAI_DEPLOYMENT_NAME=your-exact-deployment-name

# Optional: For Teams notifications (only needed for generate_docs_and_release.py)
TEAMS_WEBHOOK_URL=https://your-ms-teams.webhook/url
```

**Important Notes:**
• **OPENAI_API_KEY**: Your Azure OpenAI API key (not OpenAI's standard key)
• **OPENAI_API_BASE**: Your Azure OpenAI endpoint URL (must end with /)
• **OPENAI_API_VERSION**: Azure API version (e.g., 2024-05-13)
• **OPENAI_DEPLOYMENT_NAME**: Your exact deployment name in Azure (case-sensitive)

### Installation

```bash
pip install -r requirements.txt
```

## Script 1: generate_docs_and_release.py

### Purpose
This is the main comprehensive script that:
• Documents ALL repository files (including app directory)
• Generates release notes for the latest commit
• Sends notifications to Microsoft Teams
• Updates the root README.md with complete documentation

### When to Use
• After major commits or releases
• When you want complete repository documentation
• When you need release notes and Teams notifications
• For comprehensive project overviews

### Usage
```bash
python generate_docs_and_release.py
```

### Output
• **Root README.md**: Complete documentation of ALL files
• **Teams notification**: Release notes sent to configured webhook
• **Console output**: Detailed progress and summary

### ⚠️ Important Warnings
• **OVERWRITES** the root README.md completely
• Requires Teams webhook URL for notifications
• Processes the entire repository (can be time-consuming for large repos)

## Script 2: generate_app_docs.py

### Purpose
This app-focused script that:
• Documents ONLY Python files in the app/ directory
• Creates app-specific documentation
• Generates a changelog for app modifications
• Does NOT touch the root README.md

### When to Use
• After making changes to the app directory
• When you want app-specific documentation without affecting root docs
• For incremental app development documentation
• When working on app features independently

### Usage
```bash
python generate_app_docs.py
```

### Output
• **app/README.md**: Documentation of all Python files in app/
• **app/CHANGELOG.md**: Changelog of app-related modifications
• **Console output**: Summary of documented app files

### ⚠️ Important Warnings
• **OVERWRITES** app/README.md and app/CHANGELOG.md
• Only processes .py files in the app directory
• Does NOT send Teams notifications
• Ignores files outside the app directory

## Script 3: genrate_for_this_repo.py

### Purpose
This non-app documentation script that:
• Documents ALL files EXCEPT those in the app/ directory
• Focuses on repository structure and configuration files
• Updates root README.md with non-app documentation
• Ideal for documenting project setup and configuration

### When to Use
• After changes to configuration files, scripts, or docs
• When you want to document everything except app code
• For project setup and infrastructure documentation
• When app code is documented separately

### Usage
```bash
python genrate_for_this_repo.py
```

### Output
• **Root README.md**: Documentation of all non-app files
• **Console output**: List of processed files and summary

### ⚠️ Important Warnings
• **OVERWRITES** the root README.md completely
• Specifically EXCLUDES the app/ directory
• Does NOT send Teams notifications
• Good complement to generate_app_docs.py

## Decision Matrix: Which Script to Use?

### Use generate_docs_and_release.py when:
• ✅ You want complete repository documentation
• ✅ You need release notes and Teams notifications
• ✅ You're doing a major release or comprehensive update
• ✅ You want everything documented in one go

### Use generate_app_docs.py when:
• ✅ You only changed app code
• ✅ You want app-specific documentation
• ✅ You don't want to affect root README.md
• ✅ You're working on app features incrementally

### Use genrate_for_this_repo.py when:
• ✅ You changed configuration, scripts, or non-app files
• ✅ You want to document project structure without app code
• ✅ You're using generate_app_docs.py for app documentation
• ✅ You want faster documentation of non-app changes

### Use the Web Application when:
• ✅ You want an interactive interface for generating release notes
• ✅ You need on-demand release note generation for any repository
• ✅ You prefer browser-based tools over command-line scripts
• ✅ You want to share the tool with non-technical team members

## Cross-Script Pitfalls and Warnings

### ⚠️ README.md Override Conflicts
• **generate_docs_and_release.py** and **genrate_for_this_repo.py** both overwrite root README.md
• Running them in sequence will cause the second script to overwrite the first's output
• **Solution**: Choose one script based on your documentation needs, or run them separately and manually merge content

### ⚠️ App Directory Handling
• **generate_docs_and_release.py**: Includes app directory
• **generate_app_docs.py**: Only app directory  
• **genrate_for_this_repo.py**: Excludes app directory
• **Recommendation**: Use generate_app_docs.py + genrate_for_this_repo.py for separate documentation, OR use generate_docs_and_release.py for unified documentation

### ⚠️ Teams Notifications
• Only **generate_docs_and_release.py** sends Teams notifications
• Requires `TEAMS_WEBHOOK_URL` in .env file
• Other scripts will work without this variable

### ⚠️ Performance Considerations
• **generate_docs_and_release.py**: Slowest (processes everything + sends notifications)
• **generate_app_docs.py**: Fastest (only app Python files)
• **genrate_for_this_repo.py**: Medium (all non-app files)
• **Web Application**: Interactive (processes on-demand per request)

## Recommended Workflows

### Workflow 1: Comprehensive Documentation
```bash
# For complete repository documentation with release notes
python generate_docs_and_release.py
```

### Workflow 2: Separate App and Non-App Documentation
```bash
# First: Document app changes
python generate_app_docs.py

# Then: Document non-app changes (this will overwrite root README.md)
python genrate_for_this_repo.py

# Note: You'll have app-specific docs in app/ and general docs in root
```

### Workflow 3: App-Only Updates
```bash
# When only app code changed
python generate_app_docs.py

# Root README.md remains unchanged
```

### Workflow 4: Interactive Web Interface
```bash
# Start both services
cd python_api && python main.py &
node server.js

# Then open http://localhost:3000 in your browser
```

## Troubleshooting

### Azure OpenAI Issues
• Ensure your Azure OpenAI deployment is active and accessible
• Verify the deployment name matches exactly (case-sensitive)
• Check that your API key has the correct permissions
• Confirm your endpoint URL is correct and includes the trailing `/`

### Script-Specific Issues
• **File not found errors**: Ensure you're running scripts from the repository root
• **Permission errors**: Check file write permissions for README.md and app/ directory
• **Teams webhook errors**: Verify `TEAMS_WEBHOOK_URL` is correct (only affects `generate_docs_and_release.py`)

### Web Application Issues
• **Port conflicts**: Ensure ports 3000 (Node.js) and 8000 (Python) are available
• **Service connection errors**: Verify both Python FastAPI and Node.js servers are running
• **Frontend not loading**: Check that the `frontend/` directory exists and contains the required files
• **API request failures**: Verify Python service is accessible at `http://localhost:8000`

### Common Fixes
• **Missing .env file**: Create `.env` file with required Azure OpenAI credentials
• **Import errors**: Run `pip install -r requirements.txt`
• **Node.js dependency errors**: Run `npm install`
• **API rate limits**: Add delays between requests if hitting Azure OpenAI rate limits

## Best Practices

1. **Always backup important README.md content** before running scripts that overwrite it
2. **Test with a small repository first** to understand script behavior
3. **Use version control** to track documentation changes
4. **Choose the right script** based on what files you've modified
5. **Set up proper Azure OpenAI permissions** before running any script
6. **Monitor API usage** to avoid unexpected Azure OpenAI costs
7. **For web application**: Keep both Python and Node.js services running during usage
8. **Security**: Never expose Azure OpenAI credentials in frontend code or public repositories
