import time
import random
from fake_useragent import UserAgent
import json
import requests
import sqlite3
from bs4 import BeautifulSoup

ua = UserAgent()
item_headers = {
            "User-Agent": ua.random,
            "Accept-Language": "en-US,en;q=0.9,az;q=0.8",
            "Referer": "https://yeniemlak.az/",
        }


page =1
size =25
all_data = []

try:
    # while page <10:
        url = f"https://yeniemlak.az/elan/axtar?elan_nov=2&emlak=1&menzil_nov=&qiymet=&qiymet2=&mertebe=&mertebe2=&otaq=&otaq2=&sahe_m=&sahe_m2=&sahe_s=&sahe_s2=&seher%5B%5D=7&metro%5B%5D=9&page={page}&size={size}"

        response = requests.get(url, headers=item_headers, timeout=10)
        if response.status_code!= 200:
            print(response.status_code)
            # break
        # print(response.text[:500])
        soup = BeautifulSoup(response.text, "html.parser")
        
        # print(soup.find_all(class_="list"))

        for apartment in soup.find_all(class_="list"):
            id= apartment.find_all("titem")[-1]
            price = apartment.find("price")
            params = soup.find_all(class_="params")
            otaq  = params[0].get_text(strip=True)   
            sahe  = params[1].get_text(strip=True)   
            mertebe = params[2].get_text(strip=True) 
            seher = params[3].get_text(strip=True)   
            rayon = params[4].get_text(strip=True)   
            metro = params[5].get_text(strip=True)   
        with open("yeniemlak_params.txt", "w", encoding="utf-8") as f:
            f.write(f"{id} | {price} | {otaq} | {sahe} | {mertebe} | {seher} | {rayon} | {metro}\n")

            
            
        
        
        # with open("yeniemlak_class_params.txt", "w", encoding="utf-8") as f:
        #     f.writelines(response.text)
            # data_apartments = soup.find_all(class_="params")
            # for tag in data_apartments:
            #     f.writelines(str(tag) +"\n")
        
        
            
        # print(f"page {page} is succesfully collected" )
        page +=1
        time.sleep(random.uniform(2,4))
        
except Exception as e:
    print("error occured while sending request",e)