#!/usr/bin/env python3
"""
Test script to verify all social media MCP servers can be imported correctly.
"""

import sys
import os
import importlib.util

def test_server_import(server_name, server_path):
    """Test importing a server module."""
    try:
        spec = importlib.util.spec_from_file_location(server_name, server_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"SUCCESS: Successfully imported {server_name}")
        return True
    except Exception as e:
        print(f"ERROR: Failed to import {server_name}: {str(e)}")
        return False

def main():
    """Test all social media MCP servers."""
    print("Testing Social Media MCP Server Imports...\n")
    
    # Define the server paths
    servers = {
        "WhatsApp": "./mcp-servers/whatsapp-mcp/server.py",
        "Facebook": "./mcp-servers/facebook-mcp/server.py",
        "LinkedIn": "./mcp-servers/linkedin-mcp/server.py",
        "Instagram": "./mcp-servers/instagram-mcp/server.py",
        "Twitter": "./mcp-servers/twitter-mcp/server.py"
    }
    
    results = {}
    
    # Test each server
    for name, path in servers.items():
        abs_path = os.path.abspath(path)
        if os.path.exists(abs_path):
            results[name] = test_server_import(name, abs_path)
        else:
            print(f"ERROR: Server file does not exist: {abs_path}")
            results[name] = False
    
    # Print summary
    print("\n" + "="*50)
    print("SUMMARY:")
    total_servers = len(servers)
    successful_imports = sum(results.values())
    
    print(f"Servers tested: {total_servers}")
    print(f"Successful imports: {successful_imports}")
    print(f"Failed imports: {total_servers - successful_imports}")
    
    if successful_imports == total_servers:
        print("\nSUCCESS: All social media MCP servers imported successfully!")
        print("You can now configure them in your mcp-config.json file.")
    else:
        print("\nERROR: Some servers failed to import. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()