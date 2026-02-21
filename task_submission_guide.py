"""
Task Submission Helper for AI Employee Vault
Shows correct API usage to avoid 422 validation errors
"""

import requests
import json
from pathlib import Path

def submit_task_example():
    """Show examples of correct task submission"""
    
    print("📝 AI Employee Vault - Task Submission Guide")
    print("=" * 50)
    print()
    
    print("✅ CORRECT API CALL FORMAT:")
    print()
    print("POST /api/inbox")
    print("Content-Type: application/json")
    print()
    print("Request Body:")
    correct_payload = {
        "title": "Example task title",
        "content": "Detailed description of what needs to be done"
    }
    print(json.dumps(correct_payload, indent=2))
    print()
    
    print("❌ COMMON MISTAKES THAT CAUSE 422:")
    print("1. Missing 'title' field (REQUIRED)")
    print("2. Sending plain text instead of JSON")
    print("3. Wrong Content-Type header")
    print("4. Empty or null values")
    print()
    
    print("🔧 TO FIX YOUR CURRENT ISSUE:")
    print("1. In Swagger UI, make sure you're sending JSON in the request body")
    print("2. Ensure the 'title' field is present and not empty")
    print("3. The 'content' field is optional but can be included")
    print()
    
    print("📋 EXAMPLE CURL COMMAND:")
    print("curl -X POST http://your-app-url/api/inbox \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{\"title\": \"My task\", \"content\": \"Task description\"}'")
    print()
    
    print("🌐 ALTERNATIVE: Use the main dashboard interface at http://your-app-url/")
    print("   This provides a form that automatically formats the request correctly")

if __name__ == "__main__":
    submit_task_example()