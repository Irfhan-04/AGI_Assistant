# GitHub Setup Guide for The AGI Assistant

## Prerequisites

1. **Install Git** (if not already installed):
   - Download from: https://git-scm.com/download/win
   - Install with default settings
   - Restart terminal after installation

2. **Create GitHub Account** (if you don't have one):
   - Go to: https://github.com
   - Sign up for a free account

## Step-by-Step Setup

### Step 1: Initialize Git Repository

Open PowerShell/Terminal in your project directory and run:

```bash
# Initialize git repository
git init

# Configure git (replace with your details)
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

### Step 2: Add All Files

```bash
# Add all files to staging
git add .

# Check what will be committed
git status
```

### Step 3: Create Initial Commit

```bash
# Create initial commit
git commit -m "Initial commit: The AGI Assistant - Complete Observe, Understand, Automate pipeline"
```

### Step 4: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `The-AGI-Assistant` (or your preferred name)
3. Description: "A local AI desktop assistant that observes, learns, and automates repetitive workflows"
4. Choose: **Private** (recommended for hackathon) or **Public**
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click **"Create repository"**

### Step 5: Connect Local Repository to GitHub

After creating the repository on GitHub, you'll see instructions. Run these commands:

```bash
# Add remote repository (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/The-AGI-Assistant.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 6: Verify Upload

1. Go to your GitHub repository page
2. Verify all files are uploaded
3. Check that README.md displays correctly

## Quick Setup Script

Alternatively, you can use the provided `setup_github.bat` script after installing Git.

## Repository Structure

Your repository will include:

```
The-AGI-Assistant/
├── src/                    # Source code
├── data/                   # Data directories (gitignored)
├── logs/                   # Logs (gitignored)
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── README.md              # Documentation
├── .gitignore             # Git ignore rules
├── build_exe.py           # Build script
├── build_exe.bat          # Windows build script
├── HACKATHON_VERIFICATION.md
├── DEMO_VIDEO_SCRIPT.md
├── SUBMISSION_READY.md
└── GITHUB_SETUP.md        # This file
```

## Important Notes

- **.gitignore** is already configured to exclude:
  - `data/` folder (session data)
  - `logs/` folder
  - `venv/` (virtual environment)
  - `__pycache__/` (Python cache)
  - `dist/` and `build/` (build artifacts)
  - `.exe` files

- **Sensitive Data**: Make sure no API keys or secrets are in the code
- **Large Files**: The repository should be relatively small since data/logs are excluded

## Troubleshooting

### If you get "git is not recognized":
- Install Git from https://git-scm.com/download/win
- Restart your terminal
- Verify with: `git --version`

### If push fails with authentication:
- Use GitHub Personal Access Token instead of password
- Generate token: GitHub → Settings → Developer settings → Personal access tokens
- Use token as password when prompted

### If you want to update later:
```bash
git add .
git commit -m "Update: [describe changes]"
git push
```

## Next Steps After Uploading

1. ✅ Add repository description
2. ✅ Add topics/tags: `ai`, `automation`, `desktop-assistant`, `hackathon`, `python`
3. ✅ Pin important repositories (if applicable)
4. ✅ Share repository link in hackathon submission

