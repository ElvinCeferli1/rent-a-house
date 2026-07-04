import time
import random
from fake_useragent import UserAgent
import json
import requests
import sqlite3


ua = UserAgent()
item_headers = {
            "User-Agent": ua.random,
            "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
            "Referer": "https://bina.az/",
        }

page = 1
page_size = 50
all_data = []

try:
    while page <19:
        url = f"https://ev10.az/api/v1.0/postings?page_number={page}&media_type=image&sort_by=date_desc&sale_type=LEASE&lease_type=MONTHLY&sponsor_seed=1782230267275&sponsor_skip=0&sponsor_limit=12&search_type=filter&property_type=apartment&page_size={page_size}&location_ids=187&location_ids=186&location_ids=208&location_ids=197"
        response = requests.get(url, headers=item_headers, timeout=10)
        if response.status_code!= 200:
            print(response.status_code)
            break
            
        data = response.json()
        all_data.extend(data["postings"])
            
        print(f"page {page} is succesfully collected" )
        page +=1
        time.sleep(random.uniform(2,4))
        
except Exception as e:
    print("error occured while sending request",e)

with open("ev10.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(all_data, indent=4, ensure_ascii=False))
    
with open("ev10.json", "r", encoding="utf-8") as f:
    file = json.load(f)


conn = sqlite3.connect("rent_ev10.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS rent_ev10(
    rent_id INTEGER PRIMARY KEY,
    link TEXT,
    latitude REAL,
    longitude REAL,
    price INTEGER,
    rooms INTEGER,
    floor TEXT,
    building_type TEXT,
    checked INTEGER,
    favourite INTEGER
    )
    """)

for apartment in file["postings"]:
    values = {
    "rent_id" :apartment["id"],
    "link": f"https://ev10.az/posting/{apartment["id"]}",
    "latitude":apartment["location_lat"],
    "longitude" :apartment["location_lng"],
    "price":apartment["price"],
    "rooms":apartment["rooms"],
    "floor":f'{apartment["floor"]}/{apartment["total_floors"]}',
    "building_type":"Yeni tikili" if apartment["is_new_building"] == True else "Köhnə tikili" ,
    "checked": 0,
    "favourite": 0
}
    infos = (
        values.get("rent_id"),
        values.get("link"),
        values.get("latitude"),
        values.get("longitude"),
        values.get("price"),
        values.get("rooms"),
        values.get("floor"),
        values.get("building_type"),
        values.get("checked"),
        values.get("checked")
    )
    insert_query = ("""
        INSERT OR REPLACE INTO rent_ev10(rent_id,link,latitude,longitude,price,rooms,floor,building_type,checked,favourite)
        VALUES(?,?,?,?,?,?,?,?,?,?)""")

    cursor.execute(insert_query, infos)
    conn.commit()

