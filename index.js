const map = L.map("map", {preferCanvas: true}).setView([40.4093, 49.8671], 12);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


const filterControl = L.control({position : 'topright' })
filterControl.onAdd = function (map) {
    const btn = L.DomUtil.create('button', 'leaflet-bar native-map-btn');

    btn.id = "radius-toggle-btn";
    btn.innerText = "📍 Enable Radius Filter";

    btn.style.backgroundColor = "#2a9d8f";
    btn.style.color = "white";
    btn.style.padding = "8px 12px";
    btn.style.border = "2px solid rgba(0,0,0,0.2)";
    btn.style.borderRadius = "4px";
    btn.style.cursor = "pointer";
    btn.style.fontWeight = "bold";

    L.DomEvent.disableClickPropagation(btn);

    return btn;
};
filterControl.addTo(map);

const btnswitch = document.getElementById("radius-toggle-btn")
btnswitch.addEventListener("click", function(){
    isRadiusSearchEnabled = !isRadiusSearchEnabled

    if (isRadiusSearchEnabled){
        btnswitch.innerText = "Disable Radius Filter"
        btnswitch.style.backgroundColor = "#e76f51"
    }else {
        btnswitch.innerText = "Enable Radius Filter"
        btnswitch.style.backgroundColor = "#2a9d8f"
    }
})

const clearControl = L.control({position : 'topright' })
clearControl.onAdd = function (map) {
    const btn = L.DomUtil.create('button', 'leaflet-bar native-map-btn');

    btn.id = "clear-radius-btn";
    btn.innerText = "Clear Radius Filter";

    btn.style.backgroundColor = "#5e1a93";
    btn.style.color = "white";
    btn.style.padding = "8px 12px";
    btn.style.border = "2px solid rgba(0,0,0,0.2)";
    btn.style.borderRadius = "4px";
    btn.style.cursor = "pointer";
    btn.style.fontWeight = "bold";

    L.DomEvent.disableClickPropagation(btn);

    return btn;
};
clearControl.addTo(map)
const ClearRadius = document.getElementById("clear-radius-btn")
ClearRadius.addEventListener("click", function (){
        if (searchCircle){
            map.removeLayer(searchCircle)
            searchCircle = null
        }
        drawMap(null)
})

const favourites = L.control({position : "topright"})
favourites.onAdd = function (map){
    const btn = L.DomUtil.create("button", "leaflet-bar native-map-btn")
    btn.id = "favourites-btn"
    btn.innerText = "Favourites"
    btn.style.backgroundColor = "#17b745";
    btn.style.color = "white";
    btn.style.padding = "8px 12px";
    btn.style.border = "2px solid rgba(0,0,0,0.2)";
    btn.style.borderRadius = "4px";
    btn.style.cursor = "pointer";
    btn.style.fontWeight = "bold";

    L.DomEvent.disableClickPropagation(btn)
    return btn;
};
favourites.addTo(map)

let favourite_visible = false
const toggleFavourites = document.getElementById("favourites-btn")
toggleFavourites.addEventListener("click",async function(){
    favourite_visible = !favourite_visible
    if (favourite_visible){
        map.removeLayer(rentalsLayer)
        map.removeLayer(checkedLayer)
        await load_favourites()
        map.addLayer(FavLayer);
        toggleFavourites.innerText = "Hamsını Göstər";
        checked_toggle.innerText = "Baxılanları göstər";
    }else{
        map.removeLayer(FavLayer)
        map.removeLayer(checkedLayer)
        map.addLayer(rentalsLayer)
        toggleFavourites.innerText = "Favoriləri göstər";
        checked_toggle.innerText = "Baxılanları göstər";
    }
})

const checked =L.control({position:"topright"})
checked.onAdd = function(map){
    const btn = L.DomUtil.create("button", "leaflet-bar native-map-btn")
    btn.id = "checked-btn"
    btn.innerText = "Baxılanlar"
    btn.style.backgroundColor = "#2379db";
    btn.style.color = "white";
    btn.style.padding = "8px 12px";
    btn.style.border = "2px solid rgba(0,0,0,0.2)";
    btn.style.borderRadius = "4px";
    btn.style.cursor = "pointer";
    btn.style.fontWeight = "bold";

    L.DomEvent.disableClickPropagation(btn)
    return btn;
}
checked.addTo(map)

let checked_visible = false
const checked_toggle = document.getElementById("checked-btn")
checked_toggle.addEventListener("click", async function(){
    checked_visible =! checked_visible
    if (checked_visible){
        map.removeLayer(rentalsLayer)
        map.removeLayer(FavLayer)
        await load_checked_apartments()
        map.addLayer(checkedLayer)
        checked_toggle.innerText = "Hamsını göstər";
        toggleFavourites.innerText = "Favoriləri göstər";
    }
    else{
        map.removeLayer(FavLayer)
        map.removeLayer(checkedLayer)
        map.addLayer(rentalsLayer)
        checked_toggle.innerText = "Baxılanları göstər";
        toggleFavourites.innerText = "Favoriləri göstər";
    }
})

function Haversine(lat_center,lng_center,lat_apartment,lng_apartment){
    const R = 6371 // Earth's radius
    const diffLat = (lat_apartment - lat_center) *Math.PI/180;
    const diffLng = (lng_apartment - lng_center) *Math.PI/180;


    const a = Math.sin(diffLat/2) * Math.sin(diffLat/2) +
            Math.cos(lat_center * Math.PI / 180) * Math.cos(lat_apartment * Math.PI / 180) *
            Math.sin(diffLng/2) * Math.sin(diffLng/2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

let allData =[];
let favMarkers = {}
let checkedMarkers = {}
let searchCircle = null;
const Radius_KM = 2;
let isRadiusSearchEnabled = false;

const rentalsLayer = L.layerGroup().addTo(map)
const FavLayer = L.layerGroup().addTo(map)
const checkedLayer = L.layerGroup().addTo(map)

async function loadRentals(){
    const url = "http://127.0.0.1:8000/api/rentals"
    try{
        const response  =await fetch(url)
        if (!response.ok){
            throw new Error(`Response status: ${response.status}`)
        }

        allData = await response.json()

        drawMap(null)

        map.on('click', function(e) {
        if (!isRadiusSearchEnabled){
            return;
        }
        if (searchCircle){
            map.removeLayer(searchCircle)
        }
        
        searchCircle = L.circle(e.latlng,{
                color: '#2a9d8f',
                fillColor: '#2a9d8f',
                fillOpacity: 0.15,
                radius: Radius_KM * 1000
            }).addTo(map);

        drawMap(e.latlng)
    });

    }catch (error){
        console.log(`error occured`)
    }
}

async function load_favourites() {
    const url = "http://127.0.0.1:8000/api/rentals/favourites"
    try{
        const response = await fetch(url)
        if (!response.ok){
            throw new Error(`Response status: ${response.status}`)
        }
        const allInfo =await response.json()

        FavLayer.clearLayers()
        favMarkers = {};

        allInfo.forEach(function(apartment){
            if(apartment.favourite ==1){
                const marker = L.marker([parseFloat(apartment.latitude),parseFloat(apartment.longitude)])
                    .addTo(FavLayer)
                    .bindPopup(`<b>Tikili:</b> ${apartment.building_type}<br>
                            <b>Qiymət:</b> ${apartment.price} AZN<br>
                            <b>Otaq sayı:</b> ${apartment.rooms}<br>
                            <b>Mərtəbə:</b> ${apartment.floor}<br>
                            <a href="${apartment.link}" target="_blank">Yerindəcə bax</a><br>
                            <button type="button" id="unfav-${apartment.rent_id}"> ☆Favorilərdən Sil </button></br>`)
                favMarkers[apartment.rent_id] = marker;
                marker.on("popupopen", ()=> {
                    document.getElementById(`unfav-${apartment.rent_id}`)
                    .addEventListener("click",(e) =>{
                    e.preventDefault()
                    e.stopPropagation()
                    toggle_favourite(apartment.rent_id, false)
                    })
                })
            }
        })
        
    }catch(error){
        console.log(error)
    }
}

async function load_checked_apartments(){
    const url = "http://127.0.0.1:8000/api/rentals/checked_apartments"
    try{
        const response = await fetch(url)
        if (!response.ok){
            throw new Error(`Response status: ${response.status}`)
        }
        const allInfo =await response.json()

        checkedLayer.clearLayers()
        checkedMarkers = {};

        allInfo.forEach(function(apartment){
            if(apartment.checked ==1){
                const marker = L.marker([parseFloat(apartment.latitude),parseFloat(apartment.longitude)])
                    .addTo(checkedLayer)
                    .bindPopup(`<b>Tikili:</b> ${apartment.building_type}<br>
                            <b>Qiymət:</b> ${apartment.price} AZN<br>
                            <b>Otaq sayı:</b> ${apartment.rooms}<br>
                            <b>Mərtəbə:</b> ${apartment.floor}<br>
                            <a href="${apartment.link}" target="_blank">Yerindəcə bax</a><br>
                            <button type="button" id="uncheck-${apartment.rent_id}"> Baxılanlardan Sil </button></br>`)
                checkedMarkers[apartment.rent_id] = marker;
                marker.on("popupopen", ()=> {
                    document.getElementById(`uncheck-${apartment.rent_id}`)
                    .addEventListener("click",(e) =>{
                    e.preventDefault()
                    e.stopPropagation()
                    check_apartment(apartment.rent_id, false)
                    })
                })
            }
        })
        
    }catch(error){
        console.log(error)
    }
}

function getMarkerColor(rawPrice){
    const price = parseInt(rawPrice)
    if (price <=600){return "#2a9d8f"}
    else if (price<=800 && price >600){return "#f4a261"}
    else{return "#e76f51"}
}

function drawMap(centerPoint){
    rentalsLayer.clearLayers()

    const maxPrice = parseFloat(document.getElementById(id="maxPrice").value) || Infinity;
    const minPrice = parseFloat(document.getElementById(id="minPrice").value) || 0;
    const roomCount = parseFloat(document.getElementById(id="roomCount").value) || null;


    allData.forEach(function(apartment) {
    // console.log(`Checking ID ${apartment.rent_id}: lat=${apartment.latitude} (type: ${typeof apartment.latitude}), lng=${apartment.longitude} (type: ${typeof apartment.longitude})`);

    const lat = parseFloat(apartment.latitude);
    const lng = parseFloat(apartment.longitude);
    const rooms = parseFloat(apartment.rooms)
    const price = parseFloat(apartment.price)
        
    if (isNaN(lat) || isNaN(lng)) {
        console.warn(`⚠️ Skipped invalid coordinates for ID: ${apartment.rent_id}`);
        return; 
    }
    if (apartment.price >maxPrice || apartment.price < minPrice){return}
    if (roomCount && rooms !== roomCount) {return}

    if (centerPoint){
        let lat_center = centerPoint.lat
        let lng_center = centerPoint.lng
    
        const Distance = Haversine(lat_center,lng_center,lat,lng)
        if (Distance > Radius_KM){
        return;
    };
    }
    
    const markerColor = getMarkerColor(apartment.price)

    const marker = L.circleMarker([lat, lng],{
        radius: 8,         
        fillColor: markerColor,
        color: "#ffffff",    
        weight: 2,            
        opacity: 1,
        fillOpacity: 0.9
    });

    const popupContent = document.createElement('div');
    popupContent.innerHTML = `
        <b>Tikili:</b> ${apartment.building_type}<br>
        <b>Qiymət:</b> ${apartment.price} AZN<br>
        <b>Otaq sayı:</b> ${apartment.rooms}<br>
        <b>Mərtəbə:</b> ${apartment.floor}<br>
        <a href="${apartment.link}" target="_blank">Yerindəcə bax</a><br>
        <button type="button" id="check-${apartment.rent_id}">❌ Baxıldı ❌</button><br>
        <button type="button" id="fav-${apartment.rent_id}">⭐ Favori </button><br>
    `;

    popupContent.querySelector(`#check-${apartment.rent_id}`)
        .addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            L.DomEvent.stopPropagation(e);
            check_apartment(apartment.rent_id);
        });
    popupContent.querySelector(`#fav-${apartment.rent_id}`)
        .addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            L.DomEvent.stopPropagation(e);
            toggle_favourite(apartment.rent_id);
        });
    

    marker.bindPopup(popupContent).addTo(rentalsLayer);
    });

}

async function check_apartment(rent_id, makeChecking = true){
    rent_id = parseInt(rent_id)
    const endpoint = makeChecking ? "checked" : "unchecked"
    try{
        const response = await fetch(`http://127.0.0.1:8000/api/rentals/${rent_id}/${endpoint}`,
            {method:"POST"})  
    if (response.ok){
        allData= allData.filter(item => item.rent_id !== rent_id)

        if (checked_visible && checkedMarkers[rent_id]){
                    checkedLayer.removeLayer(checkedMarkers[rent_id]);
                    delete checkedMarkers[rent_id];
                    }else if(!checked_visible){
                        redrawWithCurrentCircle()}
        }else {
            console.error(`Backend API error: ${response.status}`);
        }
    }catch (error){
        console.error(error)
    }
}

async function toggle_favourite(rent_id, makeFavourite = true){
    rent_id = parseInt(rent_id)
    const endpoint = makeFavourite ? "favourite" : "non_favourite";
    try{
        const response = await fetch(`http://127.0.0.1:8000/api/rentals/${rent_id}/${endpoint}`,
            {method:"POST"});
            if (response.ok){
                allData=allData.filter(item=>item.rent_id !==rent_id);

                if (favourite_visible && favMarkers[rent_id]){
                    FavLayer.removeLayer(favMarkers[rent_id]);
                    delete favMarkers[rent_id];
                    }else if(!favourite_visible){
                        redrawWithCurrentCircle()}
            }else{
                console.error(`Backende API error: ${response.status}`)
        }    
    }catch(error){
        console.log(error)
    }
}
loadRentals()

function redrawWithCurrentCircle() {
    const currentCenter = searchCircle ? searchCircle.getLatLng() : null;
    drawMap(currentCenter);}

document.getElementById("maxPrice").addEventListener("input", () =>redrawWithCurrentCircle());
document.getElementById("minPrice").addEventListener("input", () =>redrawWithCurrentCircle());
document.getElementById("roomCount").addEventListener("input", () => redrawWithCurrentCircle());
