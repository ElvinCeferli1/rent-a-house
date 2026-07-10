import time
import random
import requests
from fake_useragent import UserAgent
import os

ua = UserAgent()

TARGET_LOCATION = 35 # check location.txt for metro station id 
filename = f"location_{TARGET_LOCATION}_ids.txt"
max_apartments = 1245 # check the number of apartments in that metro station from the website 


seen_ids = set()
if os.path.exists(filename):
    with open(filename, "r") as f:
        seen_ids = set(line.strip() for line in f if line.strip())
    collected_count = len(seen_ids)
    print(f"📂 Resuming — {collected_count} IDs already saved.")
else:
    collected_count = 0

has_next_page = True
end_cursor = None  
print(f"cursor: {end_cursor}")

print(f"🚀 Initializing real-time ID harvest for Location: {TARGET_LOCATION}")
print(f"💾 Data will stream directly into storage: {filename}\n")

while has_next_page:
    if collected_count >= max_apartments:
        print(f"🎯 Target reached! Already collected {collected_count}/{max_apartments} items.")
        break
    headers = {
        "User-Agent": ua.random,
        "Content-Type": "application/json",
        "Referer": "https://bina.az/",
    }
    
    payload = {
        "operationName": "SearchItems",
        "variables": {
            "first": 16,            
            "cursor": end_cursor,    
            "filter": {
                "cityId": "1",
                "categoryId": "1",
                "leased": True,
                "locationId": int(TARGET_LOCATION)
            },
            "sort": "PRICE_ASC" 
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "55232d32b6adb3055bc3e1f0a5627adb2812a29c4d93d29eaa46df1da5b4170d"  #error varsa,bunu dəyişməyi yoxla, filtrlədikdən sonra website-da network=>payload=>extensions-da tapa bilərsən(decode elə)
            }
        }
    }
    
    try:
        response = requests.post("https://bina.az/graphql", json=payload, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ Server paused stream. Code: {response.status_code}")
            break
            
        res_json = response.json()
        edges = res_json["data"]["itemsConnection"]["edges"]
        page_info = res_json["data"]["itemsConnection"]["pageInfo"]
        
        if not edges:
            print("🏁 No more items returned by server.")
            break

        with open(filename, "a") as f:
            for edge in edges:
                item_id = edge["node"]["id"]

                if item_id in seen_ids:
                    continue
                
                if collected_count>= max_apartments:
                    break
                
                item_id = edge["node"]["id"]
                f.write(f"{item_id}\n")
                seen_ids.add(item_id)
                collected_count += 1
            
        print(f"📥 Streamed batch of {len(edges)} items to file. Total saved: {collected_count}")

        has_next_page = page_info.get("hasNextPage", False)
        end_cursor = page_info.get("endCursor", None)
        # print(f"➡️ next cursor: {end_cursor} | hasNextPage: {has_next_page}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {type(e).__name__}: {e}")
        break
    except (KeyError, ValueError) as e:
        print(f"❌ Response parsing error: {type(e).__name__}: {e}")
        print(f"Status: {response.status_code}, Body: {response.text[:500]}")
        break
        
    time.sleep(random.uniform(3.2,5))

print(f"\n✨ Extraction complete! Look inside your project folder for '{filename}'")