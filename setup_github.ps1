# PowerShell script to setup GitHub - Will work once Git is installed
# This script checks for Git and guides you through the process

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Setup for The AGI Assistant" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if Git is installed
function Test-GitInstalled {
    $gitPaths = @(
        "git",
        "C:\Program Files\Git\cmd\git.exe",
        "C:\Program Files (x86)\Git\cmd\git.exe"
    )
    
    foreach ($path in $gitPaths) {
        try {
            if ($path -eq "git") {
                $null = Get-Command git -ErrorAction Stop
                return $true
            } else {
                if (Test-Path $path) {
                    return $true
                }
            }
        } catch {
            continue
        }
    }
    return $false
}

# Check for Git
if (-not (Test-GitInstalled)) {
    Write-Host "[ERROR] Git is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Git first:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://git-scm.com/download/win" -ForegroundColor White
    Write-Host "2. Install with default settings" -ForegroundColor White
    Write-Host "3. Restart PowerShell and run this script again" -ForegroundColor White
    Write-Host ""
    Write-Host "Opening Git download page..." -ForegroundColor Cyan
    Start-Process "https://git-scm.com/download/win"
    Write-Host ""
    Write-Host "After installing Git, run this script again." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Git is installed, proceed with setup
Write-Host "[OK] Git is installed!" -ForegroundColor Green
$gitVersion = git --version
Write-Host "Version: $gitVersion" -ForegroundColor Gray
Write-Host ""

# Check if already a git repository
if (Test-Path ".git") {
    Write-Host "[INFO] Git repository already initialized." -ForegroundColor Yellow
    $continue = Read-Host "Continue with setup? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 0
    }
} else {
    Write-Host "Step 1: Initializing git repository..." -ForegroundColor Cyan
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to initialize git repository" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    Write-Host "[OK] Repository initialized" -ForegroundColor Green
    Write-Host ""
}

# Configure git user
Write-Host "Step 2: Configuring Git..." -ForegroundColor Cyan
$userName = git config user.name
$userEmail = git config user.email

if (-not $userName) {
    $userName = Read-Host "Enter your name"
    git config user.name $userName
} else {
    Write-Host "Current user name: $userName" -ForegroundColor Gray
}

if (-not $userEmail) {
    $userEmail = Read-Host "Enter your email"
    git config user.email $userEmail
} else {
    Write-Host "Current user email: $userEmail" -ForegroundColor Gray
}
Write-Host ""

# Add files
Write-Host "Step 3: Adding files to repository..." -ForegroundColor Cyan
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to add files" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Show what will be committed
Write-Host ""
Write-Host "Files to be committed:" -ForegroundColor Yellow
git status --short
Write-Host ""

$continue = Read-Host "Proceed with commit? (Y/N)"
if ($continue -ne "Y" -and $continue -ne "y") {
    exit 0
}

# Create commit
Write-Host ""
Write-Host "Step 4: Creating initial commit..." -ForegroundColor Cyan
git commit -m "Initial commit: The AGI Assistant - Complete Observe, Understand, Automate pipeline"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Commit failed. This might be because:" -ForegroundColor Yellow
    Write-Host "  - There are no changes to commit" -ForegroundColor Gray
    Write-Host "  - Files are already committed" -ForegroundColor Gray
    Write-Host ""
    $continue = Read-Host "Continue anyway? (Y/N)"
    if ($continue -ne "Y" -and $continue -ne "y") {
        exit 1
    }
} else {
    Write-Host "[OK] Commit created successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "[SUCCESS] Local repository ready!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps to push to GitHub:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Go to https://github.com/new" -ForegroundColor White
Write-Host "2. Create a new repository:" -ForegroundColor White
Write-Host "   - Name: The-AGI-Assistant" -ForegroundColor Gray
Write-Host "   - Description: A local AI desktop assistant" -ForegroundColor Gray
Write-Host "   - Choose Private or Public" -ForegroundColor Gray
Write-Host "   - DO NOT initialize with README/gitignore/license" -ForegroundColor Yellow
Write-Host "3. After creating, copy the repository URL" -ForegroundColor White
Write-Host "4. Run these commands (replace YOUR_USERNAME and REPO_NAME):" -ForegroundColor White
Write-Host ""
Write-Host "   git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git" -ForegroundColor Yellow
Write-Host "   git branch -M main" -ForegroundColor Yellow
Write-Host "   git push -u origin main" -ForegroundColor Yellow
Write-Host ""
Write-Host "Note: When pushing, use a Personal Access Token as password" -ForegroundColor Yellow
Write-Host "Generate token: GitHub -> Settings -> Developer settings -> Personal access tokens" -ForegroundColor Gray
Write-Host ""

$openGitHub = Read-Host "Open GitHub repository creation page? (Y/N)"
if ($openGitHub -eq "Y" -or $openGitHub -eq "y") {
    Start-Process "https://github.com/new"
}

Write-Host ""
Write-Host "Setup complete! Your code is ready to push to GitHub." -ForegroundColor Green
Read-Host "Press Enter to exit"
