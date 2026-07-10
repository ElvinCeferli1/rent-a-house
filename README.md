
# Rent Map — Baku Rental Listings Aggregator

A personal tool for finding apartments to rent within a set radius in Baku. 

### Why I Built This
I made this project because I could not find an existing real estate website that allowed me to search for rental apartments within a specific radius of a target point—in my case, my university. If you don't want to "waste time" searching through every single apartment listing one by one on multiple platforms, you are more than welcome to use it.

> ⚠️ **Note:** This project is built by a coding enthusiast, not a professional developer. Keep in mind that there can be some bugs or mistakes here and there. Feel free to explore, but expect some rough edges!

It aggregates listings from local real-estate sites, stores them in SQLite databases, merges them, serves them through a FastAPI backend, and displays them on an interactive Leaflet map with price, room, and radius filtering.

## Features

- **Interactive map** of rental listings centered on Baku, using OpenStreetMap tiles via Leaflet.js.
- **Radius search**: Click anywhere on the map to see only listings within a set radius of that point (defaults to the 2 km radius around my university).
- **Live Filters**: Filter by min/max price and room count, applied live as you type.
- **Workflow Tracking**: Mark listings as "favourites" (starred) or "checked" (visited or ruled out so they disappear from the main view but stay tracked).
- **Color-coded markers** by price range:
  - 🟢 Green: ≤ 600 AZN
  - 🟠 Orange: 600–800 AZN
  - 🔴 Red: > 800 AZN
- **Multi-source scraping**: Tailored scrapers for `bina.az`, `ev10.az`and `evonline.az`

## Metro Coverage

To keep the data focused and relevant, all scrapers are configured to only scrape listings near these specific Baku metro stations across all websites:
- **Gənclik**
- **28 May**
- **Nizami**
- **8 Noyabr**

## Project Structure


```

rent/
├── main.py                 # FastAPI backend — serves rentals, handles favourite/checked toggles
├── index.html               # Map UI shell
├── index.js                 # Leaflet map logic, filters, UI interactions, API calls
├── id_hunting.py            # Step 1: Harvest bina.az listing IDs via GraphQL API
├── scrapeHTML.py            # Step 2: Scrape bina.az listing pages for details (price, coords, rooms)
├── Scrape_ev10.py            # Scraper for ev10.az listings
├── debug.py                 # Core utility to link and merge external databases into rent_data.db
├── bina.az -locations.txt     # Reference list of bina.az metro/location IDs
├── rent_data.db             # The Main Database — read directly by main.py and the frontend
├── rent_ev10.db             # Source Database — ev10.az data (merged via debug.py)
└── evonline.db              # Source Database — evonline.az data (merged via debug.py)

```

## Database Linking & Pipeline

1. **Scraping**: Individual scraper scripts extract real estate listings and save them to site-specific source databases (e.g., `rent_ev10.db`, `evonline.db`).
2. **Linking to Main Database (`debug.py`)**: Other source databases can and should be linked to the main database (`rent_data.db`) using the `debug.py` file. The merging logic is unified; **only the name/path of the source database needs to be changed** inside `debug.py` to pull in data from a different source.
3. **Serving**: `main.py` reads exclusively from the unified `rent_data.db` to feed the frontend.

## Configuration & Customization

### Changing the Search Radius
The search radius filter defaults to 2 km (the distance needed for my university), but it is easily adjustable. You can change the search radius directly in **`index.js` on line 167**:

```javascript
// Line 167 in index.js
const Radius_KM = 2; // Change this number to your desired radius in kilometers

```

Simply change this value and refresh your map page.

## Setup & Running

### Requirements

* Python 3.10+
* A modern web browser (Frontend is plain HTML/Vanilla JS)

### 1. Install dependencies

```bash
pip install fastapi uvicorn beautifulsoup4 requests fake-useragent

```

### 2. Run the backend

```bash
uvicorn main:app --reload

```

The FastAPI server will start running at `http://127.0.0.1:8000`.

### 3. Open the Map

Open `index.html` using a local server environment (such as VS Code's **Live Server** extension on port 5500). The frontend is configured to communicate with the backend via localhost.

## API Endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/api/rentals` | All unfavourited, unchecked listings with valid coordinates |
| GET | `/api/rentals/favourites` | Listings marked as favourite |
| GET | `/api/rentals/checked_apartments` | Listings marked as checked |
| POST | `/api/rentals/{rent_id}/checked` | Mark a listing as checked |
| POST | `/api/rentals/{rent_id}/unchecked` | Unmark a listing as checked |
| POST | `/api/rentals/{rent_id}/favourite` | Mark a listing as favourite |
| POST | `/api/rentals/{rent_id}/non_favourite` | Unmark a listing as favourite |

```

```
