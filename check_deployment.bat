@echo off
echo Checking Railway Deployment Status for AI Employee Vault
echo ======================================================

echo.
echo Step 1: Logging in to Railway (this will open browser)
echo Please follow the prompts in your browser to log in
railway login

echo.
echo Step 2: Checking if project is linked
railway status

echo.
echo Step 3: If project is not linked, you can link it:
echo railway link

echo.
echo Step 4: To see your deployment URL:
echo railway domain

echo.
echo Step 5: To deploy your application:
echo railway up

echo.
echo Step 6: To see all your projects:
echo railway list

echo.
echo Note: Your application supports multiple phases:
echo - Bronze Phase: Basic filesystem watcher
echo - Silver Phase: Enhanced watchers + MCP servers
echo - Gold Phase: Full integration + accounting
echo - Platinum Phase: 24/7 Cloud + Local agents
echo.
echo The Platinum Phase is configured in your railway.toml file
echo with AGENT_TYPE=cloud for 24/7 operation.
pause