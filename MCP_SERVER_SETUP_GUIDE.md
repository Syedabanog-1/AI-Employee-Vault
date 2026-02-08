# MCP (Model Context Protocol) Server Setup Guide

## Overview
The AI Employee system uses MCP (Model Context Protocol) servers to extend Claude Code's capabilities. MCP servers provide specialized tools for email, file system operations, calendar management, and web browsing.

## MCP Server Configuration

The MCP servers are configured in `mcp-config.json` at the root of your vault:

```json
{
  "servers": [
    {
      "name": "email",
      "command": "node",
      "args": ["./mcp-servers/email-mcp/index.js"],
      "env": {
        "GMAIL_CREDENTIALS": "./.env",
        "EMAIL_ADDRESS": "${EMAIL_ADDRESS}",
        "EMAIL_APP_PASSWORD": "${EMAIL_APP_PASSWORD}",
        "SMTP_HOST": "${SMTP_HOST}",
        "SMTP_PORT": "${SMTP_PORT}"
      }
    },
    {
      "name": "browser",
      "command": "npx",
      "args": ["@anthropic/browser-mcp"],
      "env": {
        "HEADLESS": "true"
      }
    },
    {
      "name": "filesystem",
      "command": "python",
      "args": ["./mcp-servers/filesystem-mcp/server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    },
    {
      "name": "calendar",
      "command": "python",
      "args": ["./mcp-servers/calendar-mcp/server.py"],
      "env": {
        "PYTHONPATH": "."
      }
    }
  ]
}
```

## Setting Up Each MCP Server

### 1. Email MCP Server

#### Prerequisites:
- Node.js installed
- Email account credentials (preferably app password for Gmail)

#### Setup:
1. Navigate to the email MCP directory:
   ```
   cd mcp-servers/email-mcp
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Configure your email credentials in `.env` file:
   ```
   EMAIL_ADDRESS=your-email@gmail.com
   EMAIL_APP_PASSWORD=your_app_password
   SMTP_HOST=smtp.gmail.com
   SMTP_PORT=587
   ```

#### Configuration Details:
- **EMAIL_ADDRESS**: Your email address
- **EMAIL_APP_PASSWORD**: App-specific password (for Gmail, generate via Google Account settings)
- **SMTP_HOST**: SMTP server (smtp.gmail.com for Gmail)
- **SMTP_PORT**: Port number (587 for TLS)

### 2. Browser MCP Server

The browser MCP server is provided by Anthropic and can be run directly with npx:

#### Prerequisites:
- Node.js installed
- Playwright (will be installed automatically)

#### Usage:
The browser MCP server is automatically launched by Claude Code when needed, using the npx command specified in the config.

### 3. Filesystem MCP Server

#### Prerequisites:
- Python 3.8+
- Required Python packages

#### Setup:
1. Install required packages:
   ```
   pip install -r mcp-servers/requirements-mcp.txt
   ```

2. The server is ready to use once the Python dependencies are installed.

#### Capabilities:
- Read files
- Write files
- List directories
- Create directories

### 4. Calendar MCP Server

#### Prerequisites:
- Python 3.8+
- Required Python packages

#### Setup:
1. Install required packages (same as filesystem server):
   ```
   pip install -r mcp-servers/requirements-mcp.txt
   ```

2. The server is ready to use once the Python dependencies are installed.

#### Capabilities:
- Create calendar events
- List events in date ranges
- Find free time slots

## Connecting MCP Servers to Claude Code

### 1. Claude Code Configuration
MCP servers are automatically connected when Claude Code is launched with the proper configuration. The configuration file (`mcp-config.json`) specifies how to launch each server.

### 2. Environment Setup
Make sure your `.env` file contains all necessary credentials:

```
# Email Configuration
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587

# Development Mode
DEV_MODE=true
DRY_RUN=true
```

### 3. Launching Claude Code with MCP Support
When launching Claude Code, make sure it can find the MCP configuration:

```
claude --mcp-config ./mcp-config.json
```

Or if MCP config is in the standard location, Claude Code will automatically detect it.

## Testing MCP Server Connections

### 1. Manual Testing
You can test individual MCP servers:

For the email server:
```
cd mcp-servers/email-mcp
node index.js
```

For Python servers:
```
cd mcp-servers/filesystem-mcp
python server.py
```

### 2. Claude Code Testing
In Claude Code, you can test MCP capabilities by asking Claude to use specific tools:

- "Read the file Dashboard.md"
- "Send an email to test@example.com with subject 'Test' and body 'Hello'"
- "Create a calendar event for tomorrow at 10am titled 'Team Meeting'"

## Troubleshooting

### Common Issues:

1. **MCP Server Won't Start**
   - Check that all required dependencies are installed
   - Verify the command and args in mcp-config.json are correct
   - Ensure the environment variables are properly set

2. **Permission Errors**
   - Make sure Claude Code has permission to execute the MCP server commands
   - Check file permissions for the MCP server files

3. **Connection Issues**
   - Verify that the MCP servers are launching properly
   - Check Claude Code logs for connection errors
   - Ensure no firewall is blocking the communication

4. **Credential Issues**
   - Double-check all credentials in the .env file
   - For Gmail, ensure you're using an app password, not your regular password
   - Verify that your email provider allows SMTP access

## Security Considerations

1. **Never commit .env files** to version control
2. **Use app passwords** instead of regular passwords for email accounts
3. **Limit permissions** of the email account used by the MCP server
4. **Monitor access logs** for unusual activity
5. **Regularly rotate credentials**

## Advanced Configuration

### Custom MCP Servers
You can create custom MCP servers by following the patterns in the existing servers. Each server needs to:
1. Implement the MCP protocol
2. Register its capabilities
3. Handle tool calls
4. Communicate via stdio

### Environment Variables
The MCP configuration supports environment variable substitution using ${VAR_NAME} syntax. These variables are loaded from your .env file or system environment.

## Next Steps

1. Set up your email credentials in the .env file
2. Install all required dependencies
3. Test each MCP server individually
4. Launch Claude Code and verify MCP integration
5. Begin using the enhanced capabilities in your AI Employee workflows