#!/usr/bin/env python3
"""
Test script for Employee Directory API - Search Endpoint
"""
import os
import requests
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8008"
SEARCH_ENDPOINT = f"{BASE_URL}/api/v1/employees/search"

# Default API token
DEFAULT_API_TOKEN = "employee-directory-api-token"

def get_auth_headers(token: str) -> Dict[str, str]:
    """Get authentication headers"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def get_auth_token() -> str:
    """Get authentication token from environment or use default"""
    token = os.environ.get("API_TOKEN", DEFAULT_API_TOKEN)
    print(f"Using {'default' if token == DEFAULT_API_TOKEN else 'custom'} API token for authentication...")
    return token

def make_api_request(
    url: str, 
    token: str, 
    method: str = "GET", 
    data: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Make an API request with authentication"""
    headers = get_auth_headers(token)
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            print(f"Unsupported method: {method}")
            return None
        
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error during API request: {e}")
        return None

def test_search_api() -> None:
    """Test the employee search API"""
    # Get authentication token
    token = get_auth_token()
    
    # Test search with status filter
    print("\n1. Testing search with status filter...")
    status_filter = {
        "status": ["active"],
        "page": 1,
        "page_size": 5
    }
    filtered_results = make_api_request(SEARCH_ENDPOINT, token, "POST", status_filter)
    if filtered_results:
        print(f"Found {filtered_results['total']} active employees")
        print("\nActive employees (first 5):")
        for emp in filtered_results['items']:
            print(f"  - {emp['name']} - {emp.get('status', 'N/A')}")

    # Test search with name filter
    print("\n2. Testing search with name filter...")
    name_filter = {
        "name": "Nguyen",
        "page": 1,
        "page_size": 5
    }
    name_results = make_api_request(SEARCH_ENDPOINT, token, "POST", name_filter)
    if name_results:
        print(f"Found {name_results['total']} employees with 'Nguyen' in their name")
        print("\nMatching employees (first 5):")
        for emp in name_results['items']:
            print(f"  - {emp['name']} - {emp['email']}")

    print("\nSearch API tests completed.")

if __name__ == "__main__":
    test_search_api()
