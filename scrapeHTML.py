from bs4 import BeautifulSoup
import requests
import random
import time
import sqlite3
from fake_useragent import UserAgent

location_id = 279 # check the locations.txt for metro station id
ua = UserAgent(platforms="desktop")
all_Info = {location_id: []}

file_name = f"location_{location_id}_ids"

with open(f"{file_name}.txt", "r") as f:
    ids = f.read().splitlines()
    
connection = sqlite3.connect("rent_data.db")
cursor = connection.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS rentals(
        rent_id INTEGER PRIMARY KEY,
        link TEXT,
        latitude REAL,
        longitude REAL,
        price INTEGER,
        rooms INTEGER,
        floor TEXT,
        building_type TEXT,
        checked INTEGER,
        favourite INETEGR
    )           
""")

cursor.execute("""
    SELECT rent_id FROM rentals 
    WHERE latitude IS NOT NULL AND price IS NOT NULL AND building_type IS NOT NULL
""")
existing_ids = set(str(row[0]) for row in cursor.fetchall())

connection.close()

fresh_ids = [ID for ID in ids if ID not in existing_ids]
print(f"📊 Total IDs: {len(ids)} | Already scraped: {len(existing_ids)} | Fresh targets: {len(fresh_ids)}")

processed_count = 0
for ID in fresh_ids:
    try:
        item_headers = {
            "User-Agent": ua.random,
            "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
            "Referer": "https://bina.az/",
        }
        
        print(f"🕵️ [{processed_count + 1}/{len(fresh_ids)}] Fetching item details for ID: {ID}...")
        
        apartment_data = requests.get(f"https://bina.az/items/{ID}", headers=item_headers, timeout=10)
        if apartment_data.status_code != 200:
            print(f"⚠️ Listing {ID} unavailable (Status: {apartment_data.status_code}). Skipping.")
            continue
        
        soup = BeautifulSoup(apartment_data.text, "html.parser")

        map_element = soup.find(id="item_map")
        price_element = soup.find(class_="price-val")
        
        needed_Info = {
            "rent_id": int(ID), 
            "latitude": float(map_element["data-lat"]) if map_element and map_element.has_attr("data-lat") else None,
            "longitude": float(map_element["data-lng"]) if map_element and map_element.has_attr("data-lng") else None,
            "price": int(price_element.text.replace(" ", "").strip()) if price_element else None,
            "link": f"https://bina.az/items/{ID}",
            "rooms": None,
            "floor": None,
            "building_type": None,
            "checked":0,
            "favourite":0
        }

        for div in soup.find_all(class_="product-properties__i"):
            label = div.find(class_="product-properties__i-name")
            value = div.find(class_="product-properties__i-value")
            
            if label and value:
                label = label.text.strip()
                value = value.text.strip()
            
                if label == "Otaq sayı":
                    needed_Info["rooms"] = int(value)
                elif label == "Mərtəbə":
                    needed_Info["floor"] = value
                elif label =="Kateqoriya":
                    needed_Info["building_type"] = value
        
        all_Info[location_id].append(needed_Info)
        processed_count += 1
        
        if processed_count % 5 == 0:
            connection = sqlite3.connect("rent_data.db")
            cursor = connection.cursor()
            insert_query = """
            INSERT OR REPLACE INTO rentals(rent_id, link, latitude, longitude, price, rooms, floor, building_type,checked,favourite)
            VALUES(?,?,?,?,?,?,?,?,?,?)
            """
            
            for apartment in all_Info[location_id]:
                values = (
                    apartment.get("rent_id"),
                    apartment.get("link"),
                    apartment.get("latitude"),
                    apartment.get("longitude"),
                    apartment.get("price"),
                    apartment.get("rooms"),
                    apartment.get("floor"),
                    apartment.get("building_type"),
                    apartment.get("checked"),
                    apartment.get("favourite")
                )
                cursor.execute(insert_query, values)
                
            connection.commit()
            connection.close()
            
            all_Info[location_id] = []
            print(f"💾 Successfully cached and committed last batch to rent_data.db!")
        
    except Exception as e:
        print(f"❌ Error parsing item {ID}: {e}")            
                
    time.sleep(random.uniform(2, 4))   

if all_Info[location_id]:
    connection = sqlite3.connect("rent_data.db")
    cursor = connection.cursor()
    insert_query = """
    INSERT OR REPLACE INTO rentals(rent_id, link, latitude, longitude, price, rooms, floor, building_type,checked,favourite)
    VALUES(?,?,?,?,?,?,?,?,?,?)
    """
    for apartment in all_Info[location_id]:
        values = (
            apartment.get("rent_id"),
            apartment.get("link"),
            apartment.get("latitude"),
            apartment.get("longitude"),
            apartment.get("price"),
            apartment.get("rooms"),
            apartment.get("floor"),
            apartment.get("building_type"),
            apartment.get("checked"),
            apartment.get("favourite")
        )
        cursor.execute(insert_query, values)
        
    connection.commit()
    connection.close()

print(f"\n✨ Done! Processed {processed_count} new properties into your database.")