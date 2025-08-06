#!/usr/bin/env python3

import requests
import json
from datetime import datetime
from requests.auth import HTTPBasicAuth
from config import CONFLUENCE_BASE_URL, EMAIL, API_TOKEN

def fetch_devops_space_pages():
    """Directly fetch pages from the DEVOPS space"""
    
    print("🔍 FETCHING DEVOPS SPACE PAGES DIRECTLY")
    print("=" * 50)
    
    auth = HTTPBasicAuth(EMAIL, API_TOKEN)
    headers = {"Accept": "application/json"}
    
    # Try different approaches to get space content
    space_key = "DEVOPS"
    all_pages = []
    
    # Approach 1: Get space info first
    print("1. Getting space information...")
    space_url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/space/{space_key}"
    
    try:
        response = requests.get(space_url, auth=auth, headers=headers)
        print(f"   Space info: {response.status_code}")
        if response.status_code == 200:
            space_data = response.json()
            print(f"   ✅ Space: {space_data.get('name', 'Unknown')}")
            print(f"   Key: {space_data.get('key', 'Unknown')}")
        else:
            print(f"   ❌ Failed to get space info: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Approach 2: Get all pages from the space
    print(f"\n2. Getting all pages from {space_key} space...")
    
    # Try different pagination approaches
    page_endpoints = [
        f"/wiki/rest/api/space/{space_key}/content",
        f"/wiki/rest/api/space/{space_key}/content/page", 
        f"/wiki/rest/api/content?spaceKey={space_key}&type=page",
        f"/wiki/rest/api/content?spaceKey={space_key}"
    ]
    
    for i, endpoint in enumerate(page_endpoints, 1):
        print(f"\n   Approach {i}: {endpoint}")
        url = f"{CONFLUENCE_BASE_URL}{endpoint}"
        
        params = {
            "limit": 100,
            "expand": "body.storage,version,metadata.labels,space,ancestors"
        }
        
        try:
            response = requests.get(url, auth=auth, headers=headers, params=params)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get("results", [])
                print(f"      ✅ Found {len(pages)} pages!")
                
                for page in pages:
                    title = page.get("title", "")
                    page_id = page.get("id", "")
                    
                    # Check if this looks like a runbook
                    is_runbook = any(keyword in title.lower() for keyword in 
                                   ['runbook', 'run book', 'playbook', 'procedure', 'guide'])
                    
                    page_data = {
                        "id": page_id,
                        "title": title,
                        "type": page.get("type", ""),
                        "status": page.get("status", ""),
                        "is_runbook": is_runbook,
                        "space": page.get("space", {}).get("key", "") if page.get("space") else space_key,
                        "url": f"{CONFLUENCE_BASE_URL}/wiki/spaces/{space_key}/pages/{page_id}",
                        "direct_url": f"{CONFLUENCE_BASE_URL}/wiki{page.get('_links', {}).get('webui', '')}" if page.get('_links') else "",
                        "created": page.get("version", {}).get("when", "") if page.get("version") else "",
                        "content": "",
                        "approach_used": f"endpoint_{i}"
                    }
                    
                    # Get page content if available
                    body = page.get("body", {})
                    if body and "storage" in body:
                        content = body["storage"].get("value", "")
                        page_data["content"] = content
                        page_data["word_count"] = len(content.split()) if content else 0
                    
                    all_pages.append(page_data)
                    
                    status_icon = "📘" if is_runbook else "📄"
                    print(f"         {status_icon} {title}")
                
                # If we found pages, don't try other endpoints
                if pages:
                    break
                    
            else:
                print(f"      ❌ Failed: {response.text[:100]}...")
                
        except Exception as e:
            print(f"      ❌ Error: {e}")
    
    # Approach 3: Try to get specific runbook pages by common names
    print(f"\n3. Searching for common runbook page names...")
    common_runbook_names = [
        "runbook", "runbooks", "Run Book", "Run Books", 
        "Playbook", "Playbooks", "Procedures", "Deployment Guide",
        "Incident Response", "Troubleshooting", "Operations Guide"
    ]
    
    for name in common_runbook_names:
        search_url = f"{CONFLUENCE_BASE_URL}/wiki/rest/api/content"
        params = {
            "spaceKey": space_key,
            "title": name,
            "type": "page",
            "expand": "body.storage,version"
        }
        
        try:
            response = requests.get(search_url, auth=auth, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])
                if results:
                    print(f"   ✅ Found page: '{name}' ({len(results)} results)")
                    for result in results:
                        # Add to our collection if not already there
                        if not any(p["id"] == result.get("id") for p in all_pages):
                            page_data = {
                                "id": result.get("id", ""),
                                "title": result.get("title", ""),
                                "type": result.get("type", ""),
                                "is_runbook": True,
                                "space": space_key,
                                "url": f"{CONFLUENCE_BASE_URL}/wiki/spaces/{space_key}/pages/{result.get('id', '')}",
                                "content": result.get("body", {}).get("storage", {}).get("value", "") if result.get("body") else "",
                                "approach_used": "name_search"
                            }
                            all_pages.append(page_data)
        except:
            pass
    
    # Save results
    if all_pages:
        # Remove duplicates
        unique_pages = []
        seen_ids = set()
        for page in all_pages:
            if page["id"] not in seen_ids:
                unique_pages.append(page)
                seen_ids.add(page["id"])
        
        output_data = {
            "metadata": {
                "fetched_at": datetime.now().isoformat(),
                "space_key": space_key,
                "space_url": f"{CONFLUENCE_BASE_URL}/wiki/spaces/{space_key}/pages/",
                "total_pages": len(unique_pages),
                "runbook_pages": len([p for p in unique_pages if p.get("is_runbook", False)])
            },
            "pages": unique_pages
        }
        
        filename = f"devops_space_pages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ SUCCESS! Saved {len(unique_pages)} pages to {filename}")
        
        # Summary
        runbook_pages = [p for p in unique_pages if p.get("is_runbook", False)]
        regular_pages = [p for p in unique_pages if not p.get("is_runbook", False)]
        
        print(f"\n📋 SUMMARY:")
        print(f"   📘 Runbook pages: {len(runbook_pages)}")
        print(f"   📄 Other pages: {len(regular_pages)}")
        print(f"   🔗 Space URL: {CONFLUENCE_BASE_URL}/wiki/spaces/{space_key}/pages/")
        
        print(f"\n📘 RUNBOOK PAGES FOUND:")
        for page in runbook_pages:
            word_count = page.get("word_count", 0)
            print(f"   • {page['title']} ({word_count} words)")
            print(f"     URL: {page['url']}")
        
        if regular_pages:
            print(f"\n📄 OTHER PAGES (might contain runbooks):")
            for page in regular_pages[:10]:  # Show first 10
                print(f"   • {page['title']}")
        
    else:
        print(f"\n❌ No pages found in {space_key} space")
        print("This might indicate:")
        print("1. The space key is incorrect")
        print("2. You don't have permission to access the space content")
        print("3. The space is empty")

if __name__ == "__main__":
    fetch_devops_space_pages() 