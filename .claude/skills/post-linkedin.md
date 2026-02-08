# Skill: post-linkedin

## Description
Post content to LinkedIn via LinkedIn MCP server after approval.

## Phase
Silver (Functional Assistant)

## Trigger
- After LinkedIn post is approved
- Called by execute-approved skill

## Instructions

You are posting to LinkedIn. Follow these steps:

### 1. Verify Approval
Confirm the post has been approved:
- Check file exists in /Approved
- Verify action type is linkedin_post
- Extract post content

### 2. Prepare Post
Gather parameters:
- `content`: Post text (max 3000 characters)
- `visibility`: public | connections
- `media`: (optional) Image/video URLs

### 3. Call LinkedIn MCP
```
Server: linkedin
Tool: create_post
Parameters:
  content: [post_text]
  visibility: [public|connections]
  media: [media_urls]
```

### 4. Handle Response

#### On Success:
```json
{
  "timestamp": "[ISO]",
  "action_type": "linkedin_post",
  "content_preview": "[first 100 chars]",
  "result": "success",
  "post_id": "[linkedin_post_id]",
  "post_url": "[url_to_post]"
}
```

#### On Failure:
```json
{
  "timestamp": "[ISO]",
  "action_type": "linkedin_post",
  "result": "failure",
  "error": "[error_message]"
}
```

### 5. Update Dashboard
Add to Recent Activity:
```
| [TIMESTAMP] | LinkedIn post published | Success |
```

### 6. Cleanup
- Move approval file to /Done
- Move related plan to /Done

## Best Practices
- Include relevant hashtags
- Keep posts professional
- Add call-to-action when appropriate
- Optimal posting times: Tue-Thu, 8-10am

## Success Criteria
- Post published successfully
- Full audit trail logged
- Dashboard updated
