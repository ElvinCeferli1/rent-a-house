from fastapi import FastAPI 
import sqlite3
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5500", "http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/rentals")
def get_db_connection():
    with sqlite3.connect("rent_data.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM rentals 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND checked IS 0 AND favourite IS 0
        """)
        
        rows = cursor.fetchall()
        listings = [dict(row) for row in rows]
        return listings
    
@app.get("/api/rentals/favourites")
def get_favourite_rentals():
    with sqlite3.connect("rent_data.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM rentals 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND favourite = 1
        """)
        
        rows = cursor.fetchall()
        listings = [dict(row) for row in rows]
        return listings

@app.get("/api/rentals/checked_apartments")
def get_checked_rentals():
    with sqlite3.connect("rent_data.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT * FROM rentals 
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL AND checked = 1
        """)
        
        rows = cursor.fetchall()
        listings = [dict(row) for row in rows]
        return listings

@app.post("/api/rentals/{rent_id}/checked")
def checked(rent_id:int):
    with sqlite3.connect("rent_data.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE rentals SET checked =1 WHERE rent_id=?",(rent_id,)
        )
        conn.commit()
        return {"ok":True}
    
@app.post("/api/rentals/{rent_id}/unchecked")
def uncheck(rent_id:int):
    with sqlite3.connect("rent_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE rentals SET checked = 0 WHERE rent_id=?", (rent_id,)
            )
        conn.commit()
        return {"ok":True}

@app.post("/api/rentals/{rent_id}/favourite")
def favourite(rent_id:int):
    with sqlite3.connect("rent_data.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rentals SET favourite = 1 WHERE rent_id =?""",(rent_id,)
)
        conn.commit()
        return {"ok":True}
    
@app.post("/api/rentals/{rent_id}/non_favourite")
def non_favourite(rent_id:int):
    with sqlite3.connect("rent_data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE rentals SET favourite = 0 WHERE rent_id=?",(rent_id,))
        conn.commit()
        return {"ok":True}