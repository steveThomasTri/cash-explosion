Number.prototype.format = function(n, x) {
    var re = '\\d(?=(\\d{' + (x || 3) + '})+' + (n > 0 ? '\\.' : '$') + ')';
    return this.toFixed(Math.max(0, ~~n)).replace(new RegExp(re, 'g'), '$&,');
};

// Creating map object
var map = L.map("map", {
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
  
  //function green
  function shadeOfBlue(count){
    //   if (count > 30){
    //       return 90
    //   } else{
    //       return 100 - (count * 3)
    //   } 
    return 180 + (count-1) * 4;
  }
  // Grabbing our GeoJSON data..
  d3.json("static/ohiodataresidence.json", function(data) {
    // Creating a GeoJSON layer with the retrieved data
    L.geoJson(data, {
        style:function(feature){
            return{
                fillColor:"hsl("+shadeOfBlue(feature.properties.count)+",100%,50%)", 
                fillOpacity:0.5,
                color:"white",
                weight:1.5
            }
        },
        onEachFeature: function(feature, layer){
            layer.on({
                mouseover: function(event){
                    layer = event.target;
                    layer.setStyle({
                        fillOpacity:1
                    })
                },
                mouseout: function(event){
                    layer = event.target;
                    layer.setStyle({
                        fillOpacity:0.5
                    })
                },
                click:function(event){
                    map.fitBounds(event.target.getBounds())
                }
            });

            layer.bindPopup("<h4>" + feature.properties.city + "</h4><hr><h5>Winners: "+feature.properties.count+"</h5>")
        }
    }).addTo(map);
  });