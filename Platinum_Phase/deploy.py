"""
Deployment Script for AI Employee Vault - Platinum Phase
Deploys the Cloud Agent with Swagger UI to Railway
"""

import os
import sys
import subprocess
from pathlib import Path

def deploy_platinum_phase():
    """Deploy the platinum phase cloud agent to Railway."""
    print("🚀 Deploying AI Employee Vault - Platinum Phase (Cloud Agent)")
    print("=" * 60)
    
    # Verify required files exist
    required_files = [
        "Platinum_Phase/cloud_agent/api.py",
        "Platinum_Phase/cloud_agent/start_cloud_agent.py",
        "Platinum_Phase/requirements.txt",
        "Platinum_Phase/Dockerfile.cloud"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Required file missing: {file}")
            return False
    
    print("✅ All required files present")
    
    # Show deployment information
    print("\n📋 Deployment Information:")
    print("- Cloud Agent with 24/7 operation")
    print("- Swagger UI at /docs endpoint")
    print("- ReDoc at /redoc endpoint")
    print("- Draft-only operations (emails, social, Odoo)")
    print("- Claim-by-move task management")
    print("- Secure vault synchronization")
    
    print("\n🌐 Access Points After Deployment:")
    print("  - Main Dashboard: https://<your-railway-app>.up.railway.app/")
    print("  - Swagger UI: https://<your-railway-app>.up.railway.app/docs")
    print("  - ReDoc: https://<your-railway-app>.up.railway.app/redoc")
    print("  - Health Check: https://<your-railway-app>.up.railway.app/health")
    print("  - API Root: https://<your-railway-app>.up.railway.app/api/")
    
    print("\n🔐 Security Notes:")
    print("  - Cloud Agent: Draft-only (no execution permissions)")
    print("  - Local Agent: Execution-only (with credentials)")
    print("  - Credentials never synced to cloud")
    print("  - Claim-by-move prevents duplicate work")
    
    print("\n✅ Deployment ready! Run 'railway up' to deploy.")
    return True

if __name__ == "__main__":
    success = deploy_platinum_phase()
    if not success:
        sys.exit(1)