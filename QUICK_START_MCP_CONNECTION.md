# Quick Start: Connecting MCP Servers to Claude Code

## Step-by-Step Connection Guide

### 1. Install Dependencies
```bash
# Install Node.js dependencies for email server
cd mcp-servers/email-mcp
npm install

# Install Python dependencies for other servers
pip install -r ../requirements-mcp.txt
```

### 2. Configure Credentials
Create/update your `.env` file with your email credentials:
```
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Development settings
DEV_MODE=true
DRY_RUN=false
```

### 3. Verify Configuration
Check that `mcp-config.json` is properly configured:
- Email server path: `./mcp-servers/email-mcp/index.js`
- Filesystem server path: `./mcp-servers/filesystem-mcp/server.py`
- Calendar server path: `./mcp-servers/calendar-mcp/server.py`

### 4. Launch Claude Code with MCP Support
```bash
# Claude Code will automatically detect mcp-config.json if it's in the current directory
claude

# Or explicitly specify the config:
claude --mcp-config ./mcp-config.json
```

### 5. Test MCP Capabilities
Once Claude Code is running, test the MCP integration:

**For Email:**
```
Please send an email to test@example.com with the subject "Test" and body "This is a test from AI Employee".
```

**For Filesystem:**
```
Read the contents of Dashboard.md and summarize the recent activity.
```

**For Calendar:**
```
Create a calendar event for tomorrow at 2pm titled "Follow-up Meeting".
```

## Verification Checklist

- [ ] MCP servers configured in `mcp-config.json`
- [ ] Dependencies installed for all servers
- [ ] Email credentials set in `.env` file
- [ ] Claude Code launched with MCP support
- [ ] MCP tools appearing in Claude Code's tool list
- [ ] Successful test of each MCP capability

## Troubleshooting Quick Fixes

**Issue**: MCP servers not appearing in Claude
- Solution: Verify `mcp-config.json` is in Claude's working directory

**Issue**: Email server failing to start
- Solution: Check email credentials in `.env` file

**Issue**: Python servers not working
- Solution: Ensure Python dependencies are installed

**Issue**: Permission errors
- Solution: Check file permissions for MCP server files

## Ready to Use
Once connected, your AI Employee will be able to:
- Send and receive emails automatically
- Read and write files in your vault
- Manage calendar events
- Browse the web for information
- Perform complex multi-step tasks using these capabilities