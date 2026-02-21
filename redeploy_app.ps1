# AI Employee Vault - Redeployment Script (PowerShell)
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "AI Employee Vault - Redeployment Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Checking current Railway status..." -ForegroundColor Yellow
try {
    $status = & railway status
    Write-Host $status
} catch {
    Write-Host "Project not linked. Please link your project first." -ForegroundColor Red
    Write-Host "Run: railway link" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Step 2: Checking current deployment..." -ForegroundColor Yellow
try {
    $currentDomain = & railway domain 2>$null
    if ($null -eq $currentDomain -or $currentDomain -eq "") {
        Write-Host "No domain found. This may be a new deployment." -ForegroundColor Yellow
    } else {
        Write-Host "Current domain: $currentDomain" -ForegroundColor Cyan
    }
} catch {
    Write-Host "Could not retrieve domain information" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 3: Checking current variables..." -ForegroundColor Yellow
Write-Host "Current variables:" -ForegroundColor Cyan
try {
    & railway vars
} catch {
    Write-Host "Could not retrieve variables" -ForegroundColor Red
}

Write-Host ""
Write-Host "Step 4: Updating deployment configuration..." -ForegroundColor Yellow

# Backup current railway.toml
$backupName = "railway.toml.backup.$(Get-Date -Format 'yyyyMMddHHmmss')"
Copy-Item "railway.toml" $backupName
Write-Host "Backed up current railway.toml to $backupName" -ForegroundColor Green

# Create updated railway.toml
@"
[build]
builder = "dockerfile"
dockerfilePath = "Dockerfile"

[deploy]
healthcheckPath = "/health"
healthcheckTimeout = 60
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3

[variables]
AGENT_TYPE = "cloud"
VAULT_PATH = "/app/vault"
APP_VERSION = "2.0.0-platinum-enhanced"
DEV_MODE = "false"
PORT = "8080"
HEALTH_PORT = "8080"
APP_PHASE = "platinum"
SYNC_ENABLED = "true"
CLAIM_BY_MOVE_ENABLED = "true"
CLOUD_DRAFT_ONLY = "true"
"@ | Out-File -FilePath "railway.toml" -Encoding UTF8

Write-Host "Configuration updated successfully!" -ForegroundColor Green

Write-Host ""
Write-Host "Step 5: Setting additional environment variables..." -ForegroundColor Yellow
& railway vars set APP_VERSION="2.0.0-platinum-enhanced"
& railway vars set APP_PHASE="platinum"
& railway vars set SYNC_ENABLED="true"
& railway vars set CLAIM_BY_MOVE_ENABLED="true"
& railway vars set CLOUD_DRAFT_ONLY="true"
& railway vars set LOCAL_EXECUTION_ONLY="false"

Write-Host ""
Write-Host "Step 6: Starting redeployment..." -ForegroundColor Yellow
Write-Host "This will take a few minutes. Please wait..." -ForegroundColor Cyan
& railway up

Write-Host ""
Write-Host "Step 7: Getting updated deployment information..." -ForegroundColor Yellow
Write-Host ""
Write-Host "New deployment information:" -ForegroundColor Cyan
& railway status
Write-Host ""
Write-Host "Domain information:" -ForegroundColor Cyan
& railway domain

Write-Host ""
Write-Host "Step 8: Verifying deployment health..." -ForegroundColor Yellow
Write-Host "Waiting 30 seconds for deployment to initialize..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

if ($currentDomain) {
    Write-Host "Testing health endpoint: $currentDomain/health" -ForegroundColor Cyan
    try {
        $response = Invoke-WebRequest -Uri "$currentDomain/health" -TimeoutSec 10 -Method GET
        Write-Host "Health check response: $($response.StatusCode) - $($response.Content)" -ForegroundColor Green
    } catch {
        Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Redeployment completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Your AI Employee Vault Platinum Phase is now deployed with:" -ForegroundColor Green
Write-Host "- Enhanced configuration" -ForegroundColor Green
Write-Host "- Cloud Agent mode (24/7 operation)" -ForegroundColor Green
Write-Host "- Vault synchronization enabled" -ForegroundColor Green
Write-Host "- Claim-by-move task management" -ForegroundColor Green
Write-Host "- Draft-only operations on cloud" -ForegroundColor Green

Write-Host ""
Write-Host "To access your application:" -ForegroundColor Cyan
Write-Host "- Main URL: Will be shown in the deployment info above" -ForegroundColor Cyan
Write-Host "- Health check: [URL]/health" -ForegroundColor Cyan
Write-Host "- API docs: [URL]/docs" -ForegroundColor Cyan
Write-Host "- Dashboard: [URL]/" -ForegroundColor Cyan

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")