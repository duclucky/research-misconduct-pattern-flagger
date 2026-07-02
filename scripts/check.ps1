$ErrorActionPreference = "Stop"

Write-Host "Running Check Script..."

# Check format/lint if tool exists (e.g., ruff, flake8) - currently unverified
# Check tests if pytest exists - currently unverified
if (Get-Command pytest -ErrorAction SilentlyContinue) {
    Write-Host "Running pytest..."
    pytest
} else {
    Write-Host "[Skipped] pytest not found. Project might not be fully initialized."
}

Write-Host "Check passed (or skipped due to missing tools)."
