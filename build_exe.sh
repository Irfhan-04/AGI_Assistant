#!/bin/bash
# Build script for The AGI Assistant on Linux

set -e  # Exit on error

echo "========================================"
echo "Building The AGI Assistant for Linux"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}⚠️  Warning: Virtual environment not activated${NC}"
    echo "Consider running: source venv/bin/activate"
    echo ""
fi

# Check Python version
echo "🔍 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if Python 3.10+
major=$(echo $python_version | cut -d. -f1)
minor=$(echo $python_version | cut -d. -f2)

if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 10 ]); then
    echo -e "${RED}❌ Python 3.10+ required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python version OK${NC}"
echo ""

# Install/Update PyInstaller
echo "📦 Installing PyInstaller..."
pip3 install pyinstaller --upgrade || {
    echo -e "${RED}❌ Failed to install PyInstaller${NC}"
    exit 1
}
echo ""

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf build dist *.spec
echo -e "${GREEN}✓ Cleaned${NC}"
echo ""

# Build executable
echo "🔨 Building executable..."
pyinstaller \
    --onefile \
    --windowed \
    --name=AGI_Assistant \
    --add-data="src:src" \
    --hidden-import=customtkinter \
    --hidden-import=PIL \
    --hidden-import=mss \
    --hidden-import=sounddevice \
    --hidden-import=numpy \
    --hidden-import=faster_whisper \
    --hidden-import=pytesseract \
    --hidden-import=ollama \
    --hidden-import=playwright \
    --hidden-import=pyautogui \
    --hidden-import=pynput \
    --hidden-import=psutil \
    --collect-all=customtkinter \
    --collect-all=PIL \
    --collect-all=tkinter \
    main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo -e "${GREEN}✅ Build Successful!${NC}"
    echo "========================================"
    echo ""
    echo "📦 Executable: dist/AGI_Assistant"
    
    # Make executable
    chmod +x dist/AGI_Assistant
    
    # Get file size
    size=$(du -h dist/AGI_Assistant | cut -f1)
    echo "📊 Size: $size"
    echo ""
    
    echo "⚠️  IMPORTANT: Before running, ensure:"
    echo "   1. Tesseract OCR installed: sudo apt install tesseract-ocr"
    echo "   2. Ollama installed with phi3.5:mini model"
    echo "   3. Playwright browsers: playwright install chromium"
    echo "   4. X11 tools (Linux): sudo apt install xdotool wmctrl"
    echo ""
    
    # Create installation script
    cat > install_linux_dependencies.sh << 'EOF'
#!/bin/bash
# AGI Assistant - Linux Dependencies Installer

echo "========================================"
echo "AGI Assistant - Dependency Installer"
echo "========================================"
echo ""

# Update package list
echo "Updating package list..."
sudo apt update

# Install Tesseract OCR
echo ""
echo "Installing Tesseract OCR..."
sudo apt install -y tesseract-ocr tesseract-ocr-eng

# Install X11 tools
echo ""
echo "Installing X11 tools (xdotool, wmctrl)..."
sudo apt install -y xdotool wmctrl

# Install Playwright browsers
echo ""
echo "Installing Playwright browsers..."
playwright install chromium

echo ""
echo "========================================"
echo "✅ Dependencies Installed!"
echo "========================================"
echo ""
echo "⚠️  Still need to install Ollama manually:"
echo "   1. Download from: https://ollama.ai/download"
echo "   2. Run: ollama pull phi3.5:mini"
echo ""
EOF
    
    chmod +x install_linux_dependencies.sh
    echo -e "${GREEN}✓ Created install_linux_dependencies.sh${NC}"
    echo ""
    
else
    echo ""
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo "📝 Next steps:"
echo "   1. Test: ./dist/AGI_Assistant"
echo "   2. Install dependencies: ./install_linux_dependencies.sh"
echo "   3. Create AppImage (optional)"
echo ""