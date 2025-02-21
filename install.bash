#!/bin/bash

# execute tr -d '\r' under linux to delete carriage returns


# Define Python installer URL for version 3.13.1
PYTHON_INSTALLER_URL="https://www.python.org/ftp/python/3.13.1/python-3.13.1-macos11.pkg"
INSTALLER_PATH="/tmp/python-installer.pkg"
DOCUMENTS_PATH="$HOME/Documents"

# Git installation
# Function to check if Git is installed
function test_git_installed {
    command -v git >/dev/null 2>&1
}

# Check if Git is already installed
if test_git_installed; then
    echo "Git is already installed."
else
    # Define the URL for the Git installer
    GIT_INSTALLER_URL="https://sourceforge.net/projects/git-osx-installer/files/latest/download"
    
    # Define the path where the installer will be downloaded
    INSTALLER_PATH="/tmp/GitInstaller.pkg"
    
    # Download the Git installer
    curl -L -o "$INSTALLER_PATH" "$GIT_INSTALLER_URL"
    
    # Run the installer silently
    sudo installer -pkg "$INSTALLER_PATH" -target /
    
    # Clean up the installer file
    rm "$INSTALLER_PATH"
    
    # Verify the installation
    GIT_VERSION=$(git --version)
    echo "Git has been installed successfully. Version: $GIT_VERSION"
fi

# Go to the documents installation
# Print the path
echo "Current Documents Directory: $DOCUMENTS_PATH"

cd "$DOCUMENTS_PATH" || exit

git clone https://github.com/urno38/cocoAI.git cocoAI

cd cocoAI || exit

# Check if Python is installed
if command -v python3 >/dev/null 2>&1; then
    PYTHON_VERSION=$(python3 --version)
    echo "Python is already installed: $PYTHON_VERSION"
else
    echo "Python not found. Downloading and installing Python 3.13.1..."
    curl -L -o "$INSTALLER_PATH" "$PYTHON_INSTALLER_URL"
    sudo installer -pkg "$INSTALLER_PATH" -target /
    rm "$INSTALLER_PATH"
    
    # Verify Python installation
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 --version)
        echo "Python installed successfully: $PYTHON_VERSION"
    else
        echo "Python installation failed!"
        exit 1
    fi
fi

# Virtual environment installation
# Create a virtual environment
VENV_PATH=".venv"
if [ ! -d "$VENV_PATH" ]; then
    echo "Creating virtual environment at $VENV_PATH"
    python3 -m venv "$VENV_PATH"
    echo "Virtual environment created!"
else
    echo "Virtual environment already exists at $VENV_PATH"
fi

# Activate the virtual environment (for current session)
source "$VENV_PATH/bin/activate"

# Install the requirements
pip install -r requirements.txt

# Set the PYTHONPATH environment variable
NEW_PATH=$DOCUMENTS_PATH/cocoAI

# Check if the new path is already in PYTHONPATH
if [[ ":$PYTHONPATH:" != *":$NEW_PATH:"* ]]; then
    # If not, add it to PYTHONPATH
    export PYTHONPATH=$NEW_PATH
    echo "PYTHONPATH is updated to: $PYTHONPATH"
else
    echo "PYTHONPATH already contains: $NEW_PATH"
    echo "We do not add it"
fi
echo PYTHONPATH $PYTHONPATH

cd $DOCUMENTS_PATH/cocoAI

echo Copy of the input baux 

cp -v ~/COMPTOIRS\ ET\ COMMERCES/COMMERCIAL\ -\ Documents/2\ -\ DOSSIERS\ à\ l\'ETUDE/RALLYE\ PASSY\ \(BOUILLON\ PASSY\)\ -\ 75016\ PARIS\ -\ 34\ Rue\ de\ l\'ANNONCIATION/4.\ LOCAUX\ -\ IMMOBILIER\ \&\ PLANS/Annexe\ 6\ * data/

cp -v ~/COMPTOIRS\ ET\ COMMERCES/COMMERCIAL\ -\ Documents/2\ -\ DOSSIERS\ à\ l\'ETUDE/RALLYE\ PASSY\ \(BOUILLON\ PASSY\)\ -\ 75016\ PARIS\ -\ 34\ Rue\ de\ l\'ANNONCIATION/4.\ LOCAUX\ -\ IMMOBILIER\ \&\ PLANS/Annexe\ 6\ * data/

cp -rv ~/COMPTOIRS\ ET\ COMMERCES/COMMERCIAL\ -\ Documents/100\ -\ DOSSIERS\ ARCHIVES\ -\ A\ CONSULTER/1\ -\ ARCHIVES\ DOSSIERS\ SCANNÉS/1\ -\ DOSSIERS\ SCANNÉS\ -\ BRASSERIES\ \&\ DIVERS/GILBERTE\ -\ 79\ Rue\ de\ SEINE\ -\ 75006\ PARIS data/

cp -rv ~/COMPTOIRS\ ET\ COMMERCES/COMMERCIAL\ -\ Documents/2\ -\ DOSSIERS\ à\ l\'ETUDE/CIAL\ -\ 75001\ PARIS\ -\ rue\ Mondétour\ -\ 16/4.\ LOCAUX\ -\ IMMOBILIER\ \&\ PLANS/CIAL*BAIL*pdf data/



echo install tesseract 
 
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo >> /Users/antoninbertuol/.zprofile
    echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/antoninbertuol/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
brew install tesseract
