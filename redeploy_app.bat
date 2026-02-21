@echo off
echo.
echo ================================================
echo AI Employee Vault - Redeployment Script
echo ================================================
echo.

echo Step 1: Checking current Railway status...
railway status
if %errorlevel% neq 0 (
    echo Project not linked. Please link your project first.
    echo Run: railway link
    pause
    exit /b 1
)

echo.
echo Step 2: Checking current deployment...
for /f "tokens=*" %%i in ('railway domain 2^>nul') do set CURRENT_DOMAIN=%%i
if "%CURRENT_DOMAIN%"=="" (
    echo No domain found. This may be a new deployment.
) else (
    echo Current domain: %CURRENT_DOMAIN%
)

echo.
echo Step 3: Checking current variables...
echo Current variables:
railway vars

echo.
echo Step 4: Updating deployment configuration...
echo Backing up current railway.toml...
copy railway.toml railway.toml.backup.%date:~-4,4%%date:~4,2%%date:~7,2%.%time:~0,2%%time:~3,2%%time:~6,2%

echo.
echo Updating railway.toml with enhanced configuration...
echo [build] > temp_railway.toml
echo builder = "dockerfile" >> temp_railway.toml
echo dockerfilePath = "Dockerfile" >> temp_railway.toml
echo >> temp_railway.toml
echo [deploy] >> temp_railway.toml
echo healthcheckPath = "/health" >> temp_railway.toml
echo healthcheckTimeout = 60 >> temp_railway.toml
echo restartPolicyType = "on_failure" >> temp_railway.toml
echo restartPolicyMaxRetries = 3 >> temp_railway.toml
echo >> temp_railway.toml
echo [variables] >> temp_railway.toml
echo AGENT_TYPE = "cloud" >> temp_railway.toml
echo VAULT_PATH = "/app/vault" >> temp_railway.toml
echo APP_VERSION = "2.0.0-platinum-enhanced" >> temp_railway.toml
echo DEV_MODE = "false" >> temp_railway.toml
echo PORT = "8080" >> temp_railway.toml
echo HEALTH_PORT = "8080" >> temp_railway.toml
echo APP_PHASE = "platinum" >> temp_railway.toml
echo SYNC_ENABLED = "true" >> temp_railway.toml
echo CLAIM_BY_MOVE_ENABLED = "true" >> temp_railway.toml
echo CLOUD_DRAFT_ONLY = "true" >> temp_railway.toml

move temp_railway.toml railway.toml
echo Configuration updated successfully!

echo.
echo Step 5: Setting additional environment variables...
railway vars set APP_VERSION="2.0.0-platinum-enhanced"
railway vars set APP_PHASE="platinum"
railway vars set SYNC_ENABLED="true"
railway vars set CLAIM_BY_MOVE_ENABLED="true"
railway vars set CLOUD_DRAFT_ONLY="true"
railway vars set LOCAL_EXECUTION_ONLY="false"

echo.
echo Step 6: Starting redeployment...
echo This will take a few minutes. Please wait...
railway up

echo.
echo Step 7: Getting updated deployment information...
echo.
echo New deployment information:
railway status
echo.
echo Domain information:
railway domain

echo.
echo Step 8: Verifying deployment health...
echo Waiting 30 seconds for deployment to initialize...
timeout /t 30 /nobreak >nul

echo.
echo Checking health endpoint...
if defined CURRENT_DOMAIN (
    echo Testing: %CURRENT_DOMAIN%/health
    powershell -command "try { (Invoke-WebRequest -Uri '%CURRENT_DOMAIN%/health' -TimeoutSec 10).StatusCode } catch { 'Health check failed' }"
)

echo.
echo ================================================
echo Redeployment completed!
echo ================================================
echo.
echo Your AI Employee Vault Platinum Phase is now deployed with:
echo - Enhanced configuration
echo - Cloud Agent mode (24/7 operation)
echo - Vault synchronization enabled
echo - Claim-by-move task management
echo - Draft-only operations on cloud
echo.
echo To access your application:
echo - Main URL: Will be shown above
echo - Health check: /[URL]/health
echo - API docs: /[URL]/docs
echo - Dashboard: /[URL]/
echo.
echo Press any key to exit...
pause >nul