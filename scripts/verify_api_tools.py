#!/usr/bin/env python3
"""
Script to verify API tool compatibility with the Claude API.
"""

import requests
import sys
import time
import argparse
import subprocess


def check_api_health():
    """Check if the API is healthy."""
    max_retries = 3
    retry_delay = 2  # seconds
    
    for attempt in range(max_retries):
        try:
            print(f"Checking API health (attempt {attempt+1}/{max_retries})...")
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API is healthy")
                return response.json()
            else:
                print(f"❌ API health check failed with status code {response.status_code}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
        except requests.exceptions.ConnectionError:
            print("❌ API connection failed - server may not be running")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
        except Exception as e:
            print(f"❌ API health check failed with error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    
    print("❌ API health check failed after multiple attempts")
    return None


def check_model_version():
    """Check the model version used by the API."""
    endpoints = ["/config", "/api/config", "/version", "/api/version"]
    
    for endpoint in endpoints:
        try:
            print(f"Checking endpoint {endpoint} for API configuration...")
            response = requests.get(f"http://localhost:8000{endpoint}", timeout=5)
            if response.status_code == 200:
                config = response.json()
                if "model" in config or "api_version" in config:
                    print(f"✅ Model: {config.get('model', 'Unknown')}")
                    print(f"✅ API Version: {config.get('api_version', 'Unknown')}")
                    return config
                else:
                    print(f"Endpoint {endpoint} doesn't contain model information")
            else:
                print(f"Endpoint {endpoint} returned status code {response.status_code}")
        except Exception as e:
            print(f"Error checking {endpoint}: {e}")
    
    print("❌ Failed to get API configuration from any endpoint")
    return None


def test_simple_agent():
    """Test a simple agent call with minimal tools."""
    payload = {
        "agent_name": "info",  # A simple agent that doesn't use tools
        "prompt": "What's the current date?",
    }
    
    try:
        response = requests.post("http://localhost:8000/agents/run", json=payload)
        if response.status_code == 200:
            result = response.json()
            if "error" in result:
                print(f"❌ Agent execution failed: {result['error']}")
                return False
            else:
                print("✅ Simple agent executed successfully")
                return True
        else:
            print(f"❌ Agent execution failed with status code {response.status_code}")
            try:
                print(f"Error details: {response.json()}")
            except Exception:
                print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Agent execution failed with error: {e}")
        return False


def check_remaining_tool_issues():
    """Check for any remaining tool type issues in the codebase."""
    print("\nChecking for remaining tool definition issues...")
    
    # Search for "type": "function" or 'type': 'function' in Python files
    try:
        # Check double quotes syntax
        double_quotes_cmd = 'grep -r --include="*.py" -E \'"type"\\s*:\\s*"function"\' packages/agents/'
        # Check single quotes syntax
        single_quotes_cmd = 'grep -r --include="*.py" -E "\'type\'\\s*:\\s*\'function\'" packages/agents/'
        
        # Run both commands
        double_quotes_result = subprocess.run(double_quotes_cmd, shell=True, capture_output=True, text=True)
        single_quotes_result = subprocess.run(single_quotes_cmd, shell=True, capture_output=True, text=True)
        
        issues_found = False
        
        if double_quotes_result.stdout.strip():
            print("❌ Found files with outdated double-quoted tool definitions:")
            for line in double_quotes_result.stdout.strip().split('\n'):
                if line:  # Skip empty lines
                    print(f"  - {line}")
            issues_found = True
        
        if single_quotes_result.stdout.strip():
            print("❌ Found files with outdated single-quoted tool definitions:")
            for line in single_quotes_result.stdout.strip().split('\n'):
                if line:  # Skip empty lines
                    print(f"  - {line}")
            issues_found = True
        
        if not issues_found:
            print("✅ No outdated tool definitions found")
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Error checking for tool issues: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Verify API tool compatibility")
    parser.add_argument("--skip-api-check", action="store_true", 
                        help="Skip API connection checks and only verify tool definitions")
    args = parser.parse_args()
    
    if args.skip_api_check:
        print("Skipping API connection checks as requested")
    else:
        health_data = check_api_health()
        if not health_data:
            print("Cannot continue with API tests without a healthy API")
            print("To skip API checks, use --skip-api-check")
            sys.exit(1)
        
        config = check_model_version()
        if not config:
            print("Cannot continue with API tests without API configuration")
            print("To skip API checks, use --skip-api-check")
            sys.exit(1)
        
        if not test_simple_agent():
            print("\n❌ API tool compatibility test failed")
            sys.exit(1)
        else:
            print("\n✅ API tool compatibility test passed")
    
    # Always check for tool definition issues
    no_tool_issues = check_remaining_tool_issues()
    if not no_tool_issues:
        print("Run the update_agent_tools.py script to fix tool definitions")
        sys.exit(1)
    
    print("\nAll tests passed!")


if __name__ == "__main__":
    main()
