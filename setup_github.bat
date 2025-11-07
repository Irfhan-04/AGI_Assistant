@echo off
REM GitHub Setup Script for The AGI Assistant
REM Run this after installing Git

echo ========================================
echo GitHub Setup for The AGI Assistant
echo ========================================
echo.

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git is not installed!
    echo Please install Git from: https://git-scm.com/download/win
    echo Then restart this script.
    pause
    exit /b 1
)

echo Git is installed. Proceeding...
echo.

REM Initialize git repository
echo Step 1: Initializing git repository...
git init
if errorlevel 1 (
    echo ERROR: Failed to initialize git repository
    pause
    exit /b 1
)

echo.
echo Step 2: Checking git configuration...
git config user.name >nul 2>&1
if errorlevel 1 (
    echo Git user name not configured.
    set /p GIT_NAME="Enter your name: "
    git config user.name "%GIT_NAME%"
)

git config user.email >nul 2>&1
if errorlevel 1 (
    echo Git user email not configured.
    set /p GIT_EMAIL="Enter your email: "
    git config user.email "%GIT_EMAIL%"
)

echo.
echo Step 3: Adding files to repository...
git add .
if errorlevel 1 (
    echo ERROR: Failed to add files
    pause
    exit /b 1
)

echo.
echo Step 4: Creating initial commit...
git commit -m "Initial commit: The AGI Assistant - Complete Observe, Understand, Automate pipeline"
if errorlevel 1 (
    echo ERROR: Failed to create commit
    pause
    exit /b 1
)

echo.
echo ========================================
echo Local repository initialized successfully!
echo ========================================
echo.
echo Next steps:
echo 1. Go to https://github.com/new
echo 2. Create a new repository (don't initialize with README)
echo 3. Copy the repository URL
echo 4. Run these commands:
echo.
echo    git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
echo    git branch -M main
echo    git push -u origin main
echo.
echo Or use the commands shown on GitHub after creating the repository.
echo.
pause

