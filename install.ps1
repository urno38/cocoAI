



#Python installation
# Define Python installer URL for version 3.13.1
$pythonInstallerUrl = "https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe"
$installerPath = "$env:TEMP\python-installer.exe"
$documentsPath = [System.IO.Path]::Combine($HOME, "Documents")

# Git installation 
# Function to check if Git is installed
function Test-GitInstalled {
    $gitPath = Get-Command "git" -ErrorAction SilentlyContinue
    return $null -ne $gitPath
}

# Check if Git is already installed
if (Test-GitInstalled) {
    Write-Output "Git is already installed."
} else {
    # Define the URL for the Git installer
    $gitInstallerUrl = "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe"

    # Define the path where the installer will be downloaded
    $installerPath = "$env:TEMP\GitInstaller.exe"

    # Download the Git installer
    Invoke-WebRequest -Uri $gitInstallerUrl -OutFile $installerPath

    # Run the installer silently
    Start-Process -FilePath $installerPath -ArgumentList "/SILENT" -Wait

    # Clean up the installer file
    Remove-Item -Path $installerPath

    # Verify the installation
    $gitVersion = git --version
    Write-Output "Git has been installed successfully. Version: $gitVersion"
}



# Go to the documents installation
# Print the path
Write-Output "Current Documents Directory: $documentsPath"

Set-Location $documentsPath

git clone https://github.com/urno38/cocoAI.git cocoAI

Set-Location .\cocoAI


# Check if Python is installed
$pythonInstalled = $false
try {
    $pythonVersion = python --version 2>$null
    if ($pythonVersion) {
        $pythonInstalled = $true
        Write-Host "Python is already installed: $pythonVersion" -ForegroundColor Green
    }
} catch {}

# Download and install Python if not found
if (-not $pythonInstalled) {
    Write-Host "Python not found. Downloading and installing Python 3.13.1..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $pythonInstallerUrl -OutFile $installerPath
    Start-Process -FilePath $installerPath -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait -NoNewWindow
    Remove-Item -Path $installerPath -Force
}

# Verify Python installation
try {
    $pythonVersion = python --version
    Write-Host "Python installed successfully: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python installation failed!" -ForegroundColor Red
    exit 1
}

# virtual environment installation
# Create a virtual environment
$venvPath = "$PWD\.venv"
if (!(Test-Path $venvPath)) {
    Write-Host "Creating virtual environment at $venvPath" -ForegroundColor Cyan
    python -m venv $venvPath
    Write-Host "Virtual environment created!" -ForegroundColor Green
} else {
    Write-Host "Virtual environment already exists at $venvPath" -ForegroundColor Yellow
}

# Activate the virtual environment (for current session)
Write-Host "To activate the virtual environment, run:" -ForegroundColor Cyan
Write-Host "`t$venvPath\Scripts\Activate.ps1" -ForegroundColor Yellow


# venv Activation
.venv\Scripts\Activate.ps1

# let us install the requirements
pip install -r requirements.txt


# Set the PYTHONPATH environment variable
# Define the path to add to PYTHONPATH
$newPath = "$documentsPath\cocoAI"

# Check if the new path is already in PYTHONPATH
if ($env:PYTHONPATH -notlike "*$newPath*") {
    # If not, add it to PYTHONPATH
    $env:PYTHONPATH = "$newPath;$env:PYTHONPATH"
    Write-Output "PYTHONPATH is updated to: $env:PYTHONPATH"
} else {
    Write-Output "PYTHONPATH already contains: $newPath"
    Write-Output "we do not add it"
}
