import time
import random
import requests
from fake_useragent import UserAgent

ua = UserAgent()

TARGET_LOCATION = 35 # check location.txt for metro station id
filename = f"location_{TARGET_LOCATION}_ids.txt"
max_apartments = 1185 # check the number of apartments in that metro station from the website


with open(filename, "w") as f:
    pass

collected_count = 0
has_next_page = True
end_cursor = None  

print(f"🚀 Initializing real-time ID harvest for Location: {TARGET_LOCATION}")
print(f"💾 Data will stream directly into storage: {filename}\n")

while has_next_page:
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
            "sort": "BUMPED_AT_DESC"
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "c6e47f86a9781ef4db9fc4ace25401d182e66eb4605c66de5ec0310f04fa9b76"
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
        seen_ids=()

        with open(filename, "a") as f:
            for edge in edges:
                item_id = edge["node"]["id"]

                if item_id in seen_ids:
                    continue
                
                if collected_count>= max_apartments:
                    break
                
                item_id = edge["node"]["id"]
                f.write(f"{item_id}\n")
                collected_count += 1
            
        print(f"📥 Streamed batch of {len(edges)} items to file. Total saved: {collected_count}")
        
        has_next_page = page_info.get("hasNextPage", False)
        end_cursor = page_info.get("endCursor", None)
        
    except Exception as e:
        print(f"❌ Network interruption: {e}")
        break
        
    time.sleep(random.uniform(4.2,6.5))

print(f"\n✨ Extraction complete! Look inside your project folder for '{filename}'")