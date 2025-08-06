#!/usr/bin/env python3

import requests
from requests.auth import HTTPBasicAuth
from config import CONFLUENCE_BASE_URL, EMAIL, API_TOKEN

def test_authentication():
    """Test if authentication credentials work"""
    
    # Try to get current user info - this is a simple endpoint to test auth
    url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/user/current"
    headers = {"Accept": "application/json"}
    
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    
    print(f"Testing authentication with:")
    print(f"URL: {url}")
    print(f"Email: {EMAIL}")
    print(f"Token: {API_TOKEN[:10]}...{API_TOKEN[-10:]}")
    
    response = requests.get(url, headers=headers, auth=auth)
    
    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text: {response.text[:500]}")
    
    if response.status_code == 200:
        print("✅ Authentication successful!")
        user_data = response.json()
        print(f"Authenticated as: {user_data.get('displayName', 'Unknown')}")
    else:
        print("❌ Authentication failed!")
        
        # Try alternative endpoints
        print("\nTrying alternative API endpoints...")
        
        # Test 1: Different API version
        alt_url1 = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/user"
        response1 = requests.get(alt_url1, headers=headers, auth=auth)
        print(f"Alt URL 1 ({alt_url1}): {response1.status_code}")
        
        # Test 2: Space endpoint
        alt_url2 = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/space"
        response2 = requests.get(alt_url2, headers=headers, auth=auth)  
        print(f"Alt URL 2 ({alt_url2}): {response2.status_code}")

if __name__ == "__main__":
    test_authentication() 