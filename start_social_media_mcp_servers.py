#!/usr/bin/env python3
"""
Script to start all social media MCP servers for AI Employee.
"""

import asyncio
import subprocess
import sys
import os
from pathlib import Path


def start_server(server_name, server_path):
    """Start a single MCP server."""
    print(f"Starting {server_name} server...")
    try:
        # Start the server as a subprocess
        process = subprocess.Popen([sys.executable, server_path])
        print(f"{server_name} server started with PID: {process.pid}")
        return process
    except Exception as e:
        print(f"Failed to start {server_name} server: {e}")
        return None


async def main():
    """Start all social media MCP servers."""
    print("Starting Social Media MCP Servers for AI Employee...")
    
    # Define server paths
    base_path = Path(__file__).parent
    servers = {
        "WhatsApp": base_path / "mcp-servers" / "whatsapp-mcp" / "server.py",
        "Facebook": base_path / "mcp-servers" / "facebook-mcp" / "server.py",
        "LinkedIn": base_path / "mcp-servers" / "linkedin-mcp" / "server.py",
        "Instagram": base_path / "mcp-servers" / "instagram-mcp" / "server.py",
        "Twitter": base_path / "mcp-servers" / "twitter-mcp" / "server.py"
    }
    
    processes = []
    
    # Start each server
    for name, path in servers.items():
        if path.exists():
            process = start_server(name, str(path))
            if process:
                processes.append((name, process))
        else:
            print(f"Warning: {name} server file does not exist: {path}")
    
    if not processes:
        print("No servers were started. Exiting.")
        return
    
    print(f"\n{len(processes)} social media MCP servers started successfully!")
    print("Servers are now running in the background.")
    print("\nTo stop the servers, press Ctrl+C")
    
    try:
        # Keep the script running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"{name} server stopped.")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"{name} server forcefully killed.")
            except Exception as e:
                print(f"Error stopping {name} server: {e}")
        
        print("All servers stopped.")


if __name__ == "__main__":
    asyncio.run(main())