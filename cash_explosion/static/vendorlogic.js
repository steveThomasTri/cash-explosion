// Creating map object
map = L.map("map", {
    center: [40.4173, -82.9071],
    zoom: 8
});
  
// Adding tile layer
L.tileLayer("https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}", {
    attribution: "Map data &copy; <a href=\"https://www.openstreetmap.org/\">OpenStreetMap</a> contributors, <a href=\"https://creativecommons.org/licenses/by-sa/2.0/\">CC-BY-SA</a>, Imagery © <a href=\"https://www.mapbox.com/\">Mapbox</a>",
    maxZoom: 18,
    id: "mapbox.streets",
    accessToken: API_KEY
}).addTo(map);

d3.json("/api/vendors").then(function(vendors){
    console.log(vendors)

    for(var i=0; i<vendors.length; i++){
        var location = [vendors[i].latitude, vendors[i].longitude]

        L.marker(location, {icon: greenIcon})
            .bindPopup(`<strong>${vendors[i].name}</strong><hr>${vendors[i].address}<hr>${vendors[i].id}`)
            .addTo(map)
    }
})