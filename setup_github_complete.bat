@echo off
REM Complete GitHub Setup Script for The AGI Assistant
REM This script will guide you through the entire process

echo ========================================
echo GitHub Setup for The AGI Assistant
echo ========================================
echo.

REM Check if git is installed
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed on your system.
    echo.
    echo Please install Git first:
    echo 1. Download from: https://git-scm.com/download/win
    echo 2. Run the installer with default settings
    echo 3. Restart this script after installation
    echo.
    echo Opening Git download page...
    start https://git-scm.com/download/win
    echo.
    pause
    exit /b 1
)

echo [OK] Git is installed!
git --version
echo.

REM Check if already a git repository
if exist .git (
    echo [INFO] Git repository already initialized.
    echo.
    set /p CONTINUE="Continue with setup? (Y/N): "
    if /i not "%CONTINUE%"=="Y" exit /b 0
) else (
    echo Step 1: Initializing git repository...
    git init
    if errorlevel 1 (
        echo [ERROR] Failed to initialize git repository
        pause
        exit /b 1
    )
    echo [OK] Repository initialized
    echo.
)

REM Configure git user
echo Step 2: Configuring Git...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo Git user name not configured.
    set /p GIT_NAME="Enter your name: "
    git config user.name "%GIT_NAME%"
) else (
    echo Current user name: 
    git config user.name
)

git config user.email >nul 2>&1
if errorlevel 1 (
    echo Git user email not configured.
    set /p GIT_EMAIL="Enter your email: "
    git config user.email "%GIT_EMAIL%"
) else (
    echo Current user email:
    git config user.email
)
echo.

REM Add files
echo Step 3: Adding files to repository...
git add .
if errorlevel 1 (
    echo [ERROR] Failed to add files
    pause
    exit /b 1
)

REM Show what will be committed
echo.
echo Files to be committed:
git status --short
echo.

set /p CONTINUE="Proceed with commit? (Y/N): "
if /i not "%CONTINUE%"=="Y" exit /b 0

REM Create commit
echo.
echo Step 4: Creating initial commit...
git commit -m "Initial commit: The AGI Assistant - Complete Observe, Understand, Automate pipeline"
if errorlevel 1 (
    echo [ERROR] Failed to create commit
    echo This might be because there are no changes to commit.
    pause
    exit /b 1
)

echo.
echo ========================================
echo [SUCCESS] Local repository ready!
echo ========================================
echo.
echo Next steps to push to GitHub:
echo.
echo 1. Go to https://github.com/new
echo 2. Create a new repository:
echo    - Name: The-AGI-Assistant
echo    - Description: A local AI desktop assistant
echo    - Choose Private or Public
echo    - DO NOT initialize with README/gitignore/license
echo 3. After creating, copy the repository URL
echo 4. Run these commands (replace YOUR_USERNAME and REPO_NAME):
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo Or I can help you with the GitHub repository creation.
echo.
set /p OPEN_GITHUB="Open GitHub repository creation page? (Y/N): "
if /i "%OPEN_GITHUB%"=="Y" (
    start https://github.com/new
)

echo.
pause

