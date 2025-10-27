Write-Host "Starting environment setup for Smart Lab Assistant..." -ForegroundColor Cyan

# Step 1: Stop any running Python processes
Write-Host "Closing any running Python processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Step 2: Remove old virtual environment if it exists
Write-Host "Removing old virtual environment (if any)..." -ForegroundColor Yellow
if (Test-Path ".venv") {
    Remove-Item ".venv" -Recurse -Force
}

# Step 3: Create a new virtual environment
Write-Host "Creating a new virtual environment..." -ForegroundColor Yellow
python -m venv .venv

# Step 4: Activate the new virtual environment
Write-Host "Activating the virtual environment..." -ForegroundColor Yellow
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
.\.venv\Scripts\Activate.ps1

# Step 5: Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Step 6: Install project dependencies
Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
pip install -r requirements.txt

# Step 7: Final message
Write-Host "✅ Environment setup complete!" -ForegroundColor Green
Write-Host "You can now run:  flask run  or  python app.py" -ForegroundColor Cyan
