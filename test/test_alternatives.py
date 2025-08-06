#!/usr/bin/env python3

import requests
from requests.auth import HTTPBasicAuth
from config import CONFLUENCE_BASE_URL, EMAIL, API_TOKEN

def test_alternatives():
    """Test alternative approaches for Confluence authentication"""
    
    print("🔄 TESTING ALTERNATIVE APPROACHES")
    print("=" * 50)
    
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    
    # Test 1: Different base URL structures
    print("1. Testing different base URL structures...")
    base_urls = [
        "https://meesho.atlassian.net",
        "https://meesho.atlassian.net/wiki",
        "https://wiki.meesho.atlassian.net",
        "https://confluence.meesho.com",  # In case they have custom domain
    ]
    
    for base_url in base_urls:
        test_url = f"{base_url}/rest/api/space"
        try:
            response = requests.get(test_url, auth=auth, timeout=5)
            status_emoji = "✅" if response.status_code == 200 else "❌"
            print(f"   {base_url}: {response.status_code} {status_emoji}")
            if response.status_code == 200:
                print(f"   🎉 SUCCESS with {base_url}")
                return base_url
        except requests.exceptions.RequestException as e:
            print(f"   {base_url}: ERROR - {str(e)[:50]}...")
    
    # Test 2: Try different API versions
    print("\n2. Testing different API versions...")
    api_paths = [
        "/rest/api/content",
        "/wiki/rest/api/content", 
        "/rest/api/2/search",  # Jira-style but might work
        "/wiki/api/v2/pages",  # New API version
        "/ac/rest/api/content",  # Atlassian Connect
    ]
    
    for api_path in api_paths:
        test_url = f"{CONFLUENCE_BASE_URL}{api_path}"
        try:
            response = requests.get(test_url, auth=auth, timeout=5)
            status_emoji = "✅" if response.status_code == 200 else "❌"
            print(f"   {api_path}: {response.status_code} {status_emoji}")
        except requests.exceptions.RequestException as e:
            print(f"   {api_path}: ERROR")
    
    # Test 3: Try with additional headers
    print("\n3. Testing with additional headers...")
    headers_variations = [
        {"Accept": "application/json"},
        {"Accept": "application/json", "X-Atlassian-Token": "no-check"},
        {"Accept": "application/json", "Content-Type": "application/json"},
        {"Accept": "application/json", "User-Agent": "ConfluenceBot/1.0"},
    ]
    
    test_url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/space"
    for i, headers in enumerate(headers_variations, 1):
        try:
            response = requests.get(test_url, auth=auth, headers=headers, timeout=5)
            status_emoji = "✅" if response.status_code == 200 else "❌"
            print(f"   Headers set {i}: {response.status_code} {status_emoji}")
            if response.status_code == 200:
                print(f"   🎉 SUCCESS with headers: {headers}")
        except requests.exceptions.RequestException as e:
            print(f"   Headers set {i}: ERROR")
    
    # Test 4: Check if it's actually Confluence Server vs Cloud
    print("\n4. Testing Server vs Cloud detection...")
    server_endpoints = [
        "/rest/api/space",  # Server style
        "/plugins/servlet/restbrowser",  # Server admin
    ]
    
    for endpoint in server_endpoints:
        test_url = f"{CONFLUENCE_BASE_URL}{endpoint}"
        try:
            response = requests.get(test_url, auth=auth, timeout=5)
            print(f"   Server endpoint {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print("   💡 This might be Confluence Server, not Cloud!")
        except:
            pass
    
    # Test 5: Try to access a known page directly
    print("\n5. Testing direct page access...")
    # Try accessing the space directly
    direct_urls = [
        f"{CONFLUENCE_BASE_URL}/wiki/spaces/DEVOPS",
        f"{CONFLUENCE_BASE_URL}/display/DEVOPS",
        f"{CONFLUENCE_BASE_URL}/wiki/display/DEVOPS",
    ]
    
    for url in direct_urls:
        try:
            response = requests.get(url, auth=auth, timeout=5)
            print(f"   Direct access {url.split('/')[-1]}: {response.status_code}")
            if response.status_code == 200:
                print(f"   🎉 Can access space directly!")
        except:
            pass

if __name__ == "__main__":
    test_alternatives() 