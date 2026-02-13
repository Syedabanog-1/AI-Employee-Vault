@echo off
echo.
echo ========================================================================
echo AI Employee Vault - Platinum Phase Deployment Configuration
echo ========================================================================
echo.

echo This script will configure and deploy the Platinum Phase with:
echo - 24/7 Cloud Agent operation
echo - Draft-only capabilities (no execution permissions)
echo - Vault synchronization
echo - Claim-by-move task management
echo - Work-zone specialization
echo.

set /p confirm="Do you want to proceed with Platinum Phase deployment? (y/n): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo Step 1: Ensuring we're in the correct directory...
cd /d "D:\syeda Gulzar Bano\AI_Employee_Vault_"

echo.
echo Step 2: Checking if Railway project is linked...
railway status >nul 2>&1
if %errorlevel% neq 0 (
    echo Project not linked. Attempting to link...
    railway link
    if %errorlevel% neq 0 (
        echo Failed to link project. Please run 'railway link' manually.
        pause
        exit /b 1
    )
)

echo.
echo Step 3: Creating Platinum Phase specific configuration...
echo [build] > railway.toml
echo builder = "dockerfile" >> railway.toml
echo dockerfilePath = "Dockerfile" >> railway.toml
echo >> railway.toml
echo [deploy] >> railway.toml
echo healthcheckPath = "/health" >> railway.toml
echo healthcheckTimeout = 60 >> railway.toml
echo restartPolicyType = "on_failure" >> railway.toml
echo restartPolicyMaxRetries = 3 >> railway.toml
echo >> railway.toml
echo [variables] >> railway.toml
echo AGENT_TYPE = "cloud" >> railway.toml
echo AGENT_ROLE = "cloud-draft" >> railway.toml
echo VAULT_PATH = "/app/vault" >> railway.toml
echo APP_VERSION = "2.0.0-platinum" >> railway.toml
echo APP_PHASE = "platinum" >> railway.toml
echo DEV_MODE = "false" >> railway.toml
echo PORT = "8080" >> railway.toml
echo HEALTH_PORT = "8080" >> railway.toml
echo SYNC_ENABLED = "true" >> railway.toml
echo SYNC_METHOD = "git" >> railway.toml
echo SYNC_INTERVAL = "60" >> railway.toml
echo CLAIM_BY_MOVE_ENABLED = "true" >> railway.toml
echo CLOUD_DRAFT_ONLY = "true" >> railway.toml
echo LOCAL_EXECUTION_ONLY = "false" >> railway.toml
echo SECURITY_AUDIT_ENABLED = "true" >> railway.toml
echo AUDIT_LOG_RETENTION_DAYS = "90" >> railway.toml
echo MAX_WORKERS = "4" >> railway.toml
echo TASK_QUEUE_SIZE = "100" >> railway.toml

echo.
echo Step 4: Setting Platinum Phase specific variables...
railway vars set AGENT_TYPE="cloud"
railway vars set AGENT_ROLE="cloud-draft"
railway vars set APP_VERSION="2.0.0-platinum"
railway vars set APP_PHASE="platinum"
railway vars set SYNC_ENABLED="true"
railway vars set CLAIM_BY_MOVE_ENABLED="true"
railway vars set CLOUD_DRAFT_ONLY="true"
railway vars set SECURITY_AUDIT_ENABLED="true"

echo.
echo Step 5: Validating Dockerfile for Platinum Phase...
if not exist "Dockerfile" (
    echo ERROR: Dockerfile not found!
    pause
    exit /b 1
)

echo Dockerfile found. Contents preview:
type Dockerfile | findstr /i "platinum\|cloud\|agent" || echo No specific platinum keywords found (this is OK)

echo.
echo Step 6: Initiating Platinum Phase deployment...
echo This will build and deploy your 24/7 Cloud Agent.
echo The deployment may take 5-10 minutes depending on build size.
echo.

set /p deploy_confirm="Proceed with deployment? (y/n): "
if /i not "%deploy_confirm%"=="y" (
    echo Deployment cancelled.
    pause
    exit /b 0
)

echo.
echo Starting deployment now...
railway up

echo.
echo Step 7: Retrieving deployment information...
echo.
echo Deployment status:
railway status
echo.
echo Domain information:
railway domain
echo.
echo Active variables:
railway vars

echo.
echo ========================================================================
echo Platinum Phase Deployment Complete!
echo ========================================================================
echo.
echo Your 24/7 Cloud Agent is now running with:
echo - Draft-only operations (safe, no execution permissions)
echo - Continuous monitoring via health checks
echo - Vault synchronization capabilities
echo - Claim-by-move task coordination
echo.
echo Access your Cloud Agent at the URL shown above
echo Health check endpoint: /[URL]/health
echo API documentation: /[URL]/docs
echo.
echo Remember: The Cloud Agent handles drafting only.
echo Execution happens on the Local Agent with proper credentials.
echo.
echo Press any key to exit...
pause >nul