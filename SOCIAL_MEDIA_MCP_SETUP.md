# Social Media MCP Server Setup Guide

## Overview
This guide explains how to set up and configure the social media MCP servers for WhatsApp, Facebook, LinkedIn, Instagram, and Twitter.

## Prerequisites
- Python 3.8+
- The MCP server dependencies installed:
  ```bash
  pip install -r mcp-servers/requirements-mcp.txt
  ```

## Platform-Specific Configuration

### 1. WhatsApp Business API

#### Prerequisites:
- Meta Developer Account
- WhatsApp Business Account
- Phone Number registered with WhatsApp Business
- Access Token from Meta Apps Dashboard

#### Setup:
1. Obtain your WhatsApp Business API credentials from the Meta Developers Dashboard
2. Add the following to your `.env` file:
   ```
   WHATSAPP_ACCESS_TOKEN=your_meta_access_token
   WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id
   WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id
   ```

#### Capabilities:
- Send text messages to contacts
- Send media files (images, videos, documents)
- Send messages to WhatsApp groups
- Retrieve contact list

### 2. Facebook API

#### Prerequisites:
- Facebook Developer Account
- Facebook Page with admin access
- App created in Facebook Developers Dashboard

#### Setup:
1. Create a Facebook App and Page in the Facebook Developers Dashboard
2. Add the following to your `.env` file:
   ```
   FACEBOOK_ACCESS_TOKEN=your_facebook_access_token
   FACEBOOK_PAGE_ID=your_facebook_page_id
   ```

#### Capabilities:
- Create posts on your timeline
- Create posts on Facebook Pages
- Send private messages
- Retrieve list of Facebook Pages

### 3. LinkedIn API

#### Prerequisites:
- LinkedIn Developer Account
- LinkedIn App registered in LinkedIn Developer Portal
- Proper OAuth 2.0 credentials

#### Setup:
1. Register your app in the LinkedIn Developer Portal
2. Add the following to your `.env` file:
   ```
   LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token
   LINKEDIN_PAGE_ID=your_linkedin_page_id
   ```

#### Capabilities:
- Create posts on your profile
- Create articles on your profile
- Send InMail messages
- Send connection requests
- Retrieve your connections list

### 4. Instagram Business API

#### Prerequisites:
- Instagram Business Account
- Facebook Page connected to Instagram
- Instagram App registered in Facebook Developers Dashboard

#### Setup:
1. Connect your Instagram Business Account to a Facebook Page
2. Register your app in the Facebook Developers Dashboard
3. Add the following to your `.env` file:
   ```
   INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
   INSTAGRAM_ACCOUNT_ID=your_instagram_account_id
   ```

#### Capabilities:
- Create photo posts
- Create stories
- Comment on posts
- Send direct messages
- Retrieve followers list

### 5. Twitter API

#### Prerequisites:
- Twitter Developer Account
- Twitter App registered in Twitter Developer Portal
- API Keys and Tokens

#### Setup:
1. Register your app in the Twitter Developer Portal
2. Add the following to your `.env` file:
   ```
   TWITTER_API_KEY=your_twitter_api_key
   TWITTER_API_SECRET=your_twitter_api_secret
   TWITTER_ACCESS_TOKEN=your_twitter_access_token
   TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
   ```

#### Capabilities:
- Create tweets and threads
- Reply to tweets
- Send direct messages
- Like tweets
- Retrieve followers list

## Environment Variables Reference

Your `.env` file should contain the following variables for social media MCP servers:

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

## Testing the MCP Servers

### 1. Individual Server Testing
You can test each server individually:

For WhatsApp server:
```bash
cd mcp-servers/whatsapp-mcp
python server.py
```

For Facebook server:
```bash
cd mcp-servers/facebook-mcp
python server.py
```

For LinkedIn server:
```bash
cd mcp-servers/linkedin-mcp
python server.py
```

For Instagram server:
```bash
cd mcp-servers/instagram-mcp
python server.py
```

For Twitter server:
```bash
cd mcp-servers/twitter-mcp
python server.py
```

### 2. Claude Code Integration Testing
Once all servers are configured, launch Claude Code with MCP support:

```bash
claude --mcp-config ./mcp-config.json
```

Then test the capabilities by asking Claude to perform social media actions:

- "Send a WhatsApp message to +1234567890 saying 'Hello from AI Employee'"
- "Create a LinkedIn post about our new product launch"
- "Post an Instagram story with our latest product image"
- "Tweet about our company milestone"
- "Send a Facebook message to John Doe about the meeting"

## Troubleshooting

### Common Issues:

1. **API Authentication Errors**
   - Verify all access tokens and credentials are correct
   - Check that tokens have not expired
   - Ensure proper scopes/permissions are granted

2. **Server Won't Start**
   - Check that all required Python dependencies are installed
   - Verify the server files have proper permissions
   - Check the mcp-config.json configuration

3. **Rate Limiting**
   - Each platform has API rate limits
   - Implement retry logic with exponential backoff
   - Monitor API usage in developer dashboards

4. **Permission Issues**
   - Ensure your app has the necessary permissions for each platform
   - Some actions require additional review/approval from platform providers

## Security Considerations

1. **Never commit** your `.env` file to version control
2. **Rotate tokens regularly** to maintain security
3. **Use minimal required permissions** for each API
4. **Monitor API usage** for unusual activity
5. **Secure token storage** in production environments

## Next Steps

1. Obtain API credentials for each platform
2. Update your `.env` file with the credentials
3. Install required dependencies
4. Test each MCP server individually
5. Launch Claude Code with MCP support
6. Begin automating social media tasks through your AI Employee