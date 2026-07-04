import sqlite3

source_conn = sqlite3.connect("rent_ev10.db")
source_cursor = source_conn.cursor()


target_conn = sqlite3.connect("rent_data.db")
target_cursor = target_conn.cursor()

try:
    print("Reading listings from rent_ev10.db...")
    source_cursor.execute("""
        SELECT rent_id, link, latitude, longitude, price, rooms, floor, building_type, checked, favourite
        FROM rent_ev10
    """)
    rent_ev10_rows = source_cursor.fetchall()
    print(f"Found {len(rent_ev10_rows)} listings to migrate.")

    print("Migrating rows into rent_data.db...")
    insert_query = """
        INSERT OR IGNORE INTO rentals (rent_id, link, latitude, longitude, price, rooms, floor, building_type, checked, favourite)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?)
    """
    
    target_cursor.executemany(insert_query, rent_ev10_rows)
    inserted_count = target_conn.total_changes

    target_conn.commit()
    print(f"🎉 Success! Added {inserted_count} unique rent_ev10 listings directly into your main dashboard.")

except Exception as e:
    print("An error occurred during migration:", e)
    target_conn.rollback()

finally:

    source_conn.close()
    target_conn.close()
