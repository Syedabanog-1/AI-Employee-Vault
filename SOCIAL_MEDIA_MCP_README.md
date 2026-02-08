# Social Media MCP Servers for AI Employee

This directory contains Model Context Protocol (MCP) servers that enable your AI Employee to interact with various social media platforms.

## Available MCP Servers

### 1. WhatsApp MCP Server
- **Location**: `mcp-servers/whatsapp-mcp/server.py`
- **Capabilities**:
  - Send text messages to contacts
  - Send media files (images, videos, documents)
  - Send messages to WhatsApp groups
  - Retrieve contact list

### 2. Facebook MCP Server
- **Location**: `mcp-servers/facebook-mcp/server.py`
- **Capabilities**:
  - Create posts on your timeline
  - Create posts on Facebook Pages
  - Send private messages
  - Retrieve list of Facebook Pages

### 3. LinkedIn MCP Server
- **Location**: `mcp-servers/linkedin-mcp/server.py`
- **Capabilities**:
  - Create posts on your profile
  - Create articles on your profile
  - Send InMail messages
  - Send connection requests
  - Retrieve your connections list

### 4. Instagram MCP Server
- **Location**: `mcp-servers/instagram-mcp/server.py`
- **Capabilities**:
  - Create photo posts
  - Create stories
  - Comment on posts
  - Send direct messages
  - Retrieve followers list

### 5. Twitter MCP Server
- **Location**: `mcp-servers/twitter-mcp/server.py`
- **Capabilities**:
  - Create tweets and threads
  - Reply to tweets
  - Send direct messages
  - Like tweets
  - Retrieve followers list

## Configuration

### Environment Variables
Add the following to your `.env` file:

```
# WhatsApp Business API
WHATSAPP_ACCESS_TOKEN=your_meta_access_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id

# Facebook API
FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
FACEBOOK_PAGE_ID=your_facebook_page_id

# LinkedIn API
LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
LINKEDIN_PAGE_ID=your_linkedin_page_id

# Instagram Business API
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
INSTAGRAM_ACCOUNT_ID=your_instagram_account_id

# Twitter API
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
```

### MCP Configuration
The servers are already configured in `mcp-config.json`:

```json
{
  "servers": [
    // ... other servers ...
    {
      "name": "whatsapp",
      "command": "python",
      "args": ["./mcp-servers/whatsapp-mcp/server.py"],
      "env": {
        "PYTHONPATH": ".",
        "WHATSAPP_ACCESS_TOKEN": "${WHATSAPP_ACCESS_TOKEN}",
        "WHATSAPP_PHONE_NUMBER_ID": "${WHATSAPP_PHONE_NUMBER_ID}",
        "WHATSAPP_BUSINESS_ACCOUNT_ID": "${WHATSAPP_BUSINESS_ACCOUNT_ID}"
      }
    },
    {
      "name": "facebook",
      "command": "python",
      "args": ["./mcp-servers/facebook-mcp/server.py"],
      "env": {
        "PYTHONPATH": ".",
        "FACEBOOK_ACCESS_TOKEN": "${FACEBOOK_ACCESS_TOKEN}",
        "FACEBOOK_PAGE_ID": "${FACEBOOK_PAGE_ID}"
      }
    },
    {
      "name": "linkedin",
      "command": "python",
      "args": ["./mcp-servers/linkedin-mcp/server.py"],
      "env": {
        "PYTHONPATH": ".",
        "LINKEDIN_ACCESS_TOKEN": "${LINKEDIN_ACCESS_TOKEN}",
        "LINKEDIN_PAGE_ID": "${LINKEDIN_PAGE_ID}"
      }
    },
    {
      "name": "instagram",
      "command": "python",
      "args": ["./mcp-servers/instagram-mcp/server.py"],
      "env": {
        "PYTHONPATH": ".",
        "INSTAGRAM_ACCESS_TOKEN": "${INSTAGRAM_ACCESS_TOKEN}",
        "INSTAGRAM_ACCOUNT_ID": "${INSTAGRAM_ACCOUNT_ID}"
      }
    },
    {
      "name": "twitter",
      "command": "python",
      "args": ["./mcp-servers/twitter-mcp/server.py"],
      "env": {
        "PYTHONPATH": ".",
        "TWITTER_API_KEY": "${TWITTER_API_KEY}",
        "TWITTER_API_SECRET": "${TWITTER_API_SECRET}",
        "TWITTER_ACCESS_TOKEN": "${TWITTER_ACCESS_TOKEN}",
        "TWITTER_ACCESS_TOKEN_SECRET": "${TWITTER_ACCESS_TOKEN_SECRET}"
      }
    }
  ]
}
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r mcp-servers/requirements-mcp.txt
   ```

2. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`
   - Fill in your API credentials for each platform

3. **Test the Servers**:
   ```bash
   python test_social_media_mcp.py
   ```

4. **Launch Claude Code with MCP Support**:
   ```bash
   claude --mcp-config ./mcp-config.json
   ```

## Usage Examples

Once configured, you can ask Claude to perform social media actions:

- "Send a WhatsApp message to +1234567890 saying 'Hello from AI Employee'"
- "Create a LinkedIn post about our new product launch"
- "Post an Instagram story with our latest product image"
- "Tweet about our company milestone"
- "Send a Facebook message to John Doe about the meeting"

## Security Considerations

- Never commit your `.env` file to version control
- Rotate API tokens regularly
- Use minimal required permissions for each API
- Monitor API usage for unusual activity

## Troubleshooting

- If servers fail to start, check that all required environment variables are set
- Verify that your API credentials have the necessary permissions
- Check that all required Python dependencies are installed