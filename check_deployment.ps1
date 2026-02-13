Write-Host "Checking Railway Deployment Status for AI Employee Vault" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green

Write-Host "`nStep 1: Logging in to Railway (this will open browser)" -ForegroundColor Yellow
Write-Host "Please follow the prompts in your browser to log in"
Start-Process -FilePath "railway" -ArgumentList "login"

Write-Host "`nStep 2: Checking if project is linked" -ForegroundColor Yellow
try {
    $status = & railway status
    Write-Host $status
} catch {
    Write-Host "Project not linked. Run 'railway link' to link to an existing project" -ForegroundColor Red
}

Write-Host "`nStep 3: To see your deployment URL:" -ForegroundColor Yellow
Write-Host "railway domain"

Write-Host "`nStep 4: To deploy your application:" -ForegroundColor Yellow
Write-Host "railway up"

Write-Host "`nStep 5: To see all your projects:" -ForegroundColor Yellow
Write-Host "railway list"

Write-Host ""
Write-Host "Note: Your application supports multiple phases:" -ForegroundColor Cyan
Write-Host "- Bronze Phase: Basic filesystem watcher" -ForegroundColor Cyan
Write-Host "- Silver Phase: Enhanced watchers + MCP servers" -ForegroundColor Cyan
Write-Host "- Gold Phase: Full integration + accounting" -ForegroundColor Cyan
Write-Host "- Platinum Phase: 24/7 Cloud + Local agents" -ForegroundColor Cyan
Write-Host ""
Write-Host "The Platinum Phase is configured in your railway.toml file" -ForegroundColor Cyan
Write-Host "with AGENT_TYPE=cloud for 24/7 operation." -ForegroundColor Cyan

Write-Host "`nPress any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")