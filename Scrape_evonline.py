import requests
from fake_useragent import UserAgent
import json
import sqlite3
import time
import random

# ua = UserAgent()
# item_headers = {
#     "User-Agent": ua.random,
#     "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
#     "Referer": "https://evonline.az/", 
# }

# urls = [
#     "https://evonline.az/map_search_api.php?bounds=40.38126137588519%2C49.80995610355665%2C40.408781383539925%2C49.85870793461134&zoom=14&emlak_novu=M%C9%99nzil&elan_tipi=Kiray%C9%99+verilir&kiraye_novu=Ayl%C4%B1q",
#     "https://evonline.az/map_search_api.php?bounds=40.38305934443676%2C49.80390504001905%2C40.41057861738406%2C49.85265687107374&zoom=14&emlak_novu=M%C9%99nzil&elan_tipi=Kiray%C9%99+verilir&kiraye_novu=Ayl%C4%B1q",
#     "https://evonline.az/map_search_api.php?bounds=40.3841054131479%2C49.803132563822764%2C40.41162425862567%2C49.85188439487745&zoom=14&emlak_novu=M%C9%99nzil&elan_tipi=Kiray%C9%99+verilir&kiraye_novu=Ayl%C4%B1q",
#     "https://evonline.az/map_search_api.php?bounds=40.36443374227096%2C49.77832749485304%2C40.41947626012232%2C49.87583115696241&zoom=13&emlak_novu=M%C9%99nzil&elan_tipi=Kiray%C9%99+verilir&kiraye_novu=Ayl%C4%B1q",
#     "https://evonline.az/map_search_api.php?bounds=40.37710828337788%2C49.82821872376631%2C40.432140444397014%2C49.92572238587569&zoom=13&emlak_novu=M%C9%99nzil&elan_tipi=Kiray%C9%99+verilir&kiraye_novu=Ayl%C4%B1q",
#     "https://evonline.az/map_search_api.php?bounds=40.37697751209568%2C49.77637698792647%2C40.43200977998657%2C49.873880650035844&zoom=13&emlak_novu=M%C9%99nzil&elan_tipi=Kiray%C9%99+verilir&kiraye_novu=Ayl%C4%B1q",
#     "https://evonline.az/map_search_api.php?bounds=40.37648904102385%2C49.80348381500683%2C40.40401099867581%2C49.852235646061516&zoom=14&emlak_novu=M%C9%99nzil&elan_tipi=Kiray%C9%99+verilir&kiraye_novu=Ayl%C4%B1q",
#     "https://evonline.az/map_search_api.php?bounds=40.3713009776904%2C49.805772575751874%2C40.398825054991576%2C49.85452440680656&zoom=14&emlak_novu=M%C9%99nzil&elan_tipi=Kiray%C9%99+verilir&kiraye_novu=Ayl%C4%B1q"
# ]

# all_data_evonline = []
# seen_ids = set()

# try:
#     for idx, url in enumerate(urls, 1):
#         print(f"Fetching bounding box chunk {idx}/{len(urls)}...")
#         response = requests.get(url, headers=item_headers, timeout=10)
        
#         if response.status_code != 200:
#             print(f"⚠️ Skipped box {idx} due to HTTP status: {response.status_code}")
#             continue
            
#         data = response.json()
#         listings = data.get("elanlar", [])
        
#         for apartment in listings:
#             apart_id = apartment.get("id")
#             if apart_id and apart_id not in seen_ids:
#                 seen_ids.add(apart_id)
#                 all_data_evonline.append(apartment)

#         time.sleep(random.uniform(5, 7))
    
# except Exception as e:
#     print("An error occurred during extraction:", e)

# with open("evonline_new.json", "w", encoding="utf-8") as f:
#     json.dump({"elanlar": all_data_evonline}, f, indent=4, ensure_ascii=False)

# print(f"Finished! Gathered {len(all_data_evonline)} unique apartments completely clean.")
    
"""
# with open("evonline_new.json" ,"r", encoding= "utf-8") as f:
#     file = json.load(f)
   
# ids = [apartment["id"] for apartment in file] 
# print(len(ids))

# 1600 dene, amma tekrarlar var, coxdu boyuk ehtimalla
"""
    
    
conn = sqlite3.connect("evonline.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS evonline(
    rent_id INTEGER PRIMARY KEY,
    link TEXT,
    latitude REAL,
    longitude REAL,
    price INTEGER,
    rooms INTEGER,
    floor TEXT,
    building_type TEXT,
    checked INTEGER
    )
    """)

with open("evonline_new.json", "r", encoding="utf-8") as f:
    file = json.load(f)
    
all_info=[]
seen_ids = set() 
    
for apartment in file["elanlar"]:
    
    id = apartment["id"]
    if id is None:
        continue
    id = int(id)
    
    if id in seen_ids:
        continue
    else:
        seen_ids.add(id)
        
        infos = (
        id,
        f"https://evonline.az/view.php?id={id}",
        apartment["latitude"],
        apartment["longitude"],
        apartment["qiymet"],
        apartment["otaq_sayi"],
        f'{apartment["mertebe"]}/{apartment["mertebe_sayi"]}',
        apartment["tikili_novu"],
        0
        )
        all_info.append(infos)
    
insert_query = ("""
            INSERT OR IGNORE INTO evonline(rent_id,link,latitude,longitude,price,rooms,floor,building_type,checked)
            VALUES(?,?,?,?,?,?,?,?,?)""")

cursor.executemany(insert_query, all_info)
conn.commit()
conn.close()