Number.prototype.format = function(n, x) {
    var re = '\\d(?=(\\d{' + (x || 3) + '})+' + (n > 0 ? '\\.' : '$') + ')';
    return this.toFixed(Math.max(0, ~~n)).replace(new RegExp(re, 'g'), '$&,');
};

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
  
  //function green
  function shadeOfGreen(avg){
      return Math.round(-2 * avg / 100 + 375)
  }
  function shadeOfBlue(count){
        if (count > 30){
            return 90
        } else{
            return 100 - (count * 3)
        } 
    }
  // Grabbing our GeoJSON data..
  d3.json("static/ohiodata.json", function(data) {
    // Creating a GeoJSON layer with the retrieved data
    
    L.geoJson(data, {
        style:function(feature){
            return{
                fillColor:"rgb(0,"+shadeOfGreen(feature.properties.avg)+",0)", 
                fillOpacity:0.5,
                color:"white",
                weight:feature.properties.count / 2
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

            layer.bindPopup("<h1>" + feature.properties.city + "</h1><hr><h2>Tickets Bought: "+feature.properties.count+"</h2><h2>Average Game Total: $"+feature.properties.avg.format(0,3)+"</h2>")
        }
    }).addTo(map);
  });

d3.select("#mapchange").on("click", function(){
    d3.select("#map").html("")
    map = null;
    L.map = null;

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

    // Grabbing our GeoJSON data..
    d3.json("static/ohiodataresidence.json", function(data) {
    // Creating a GeoJSON layer with the retrieved data
        L.geoJson(data, {
            style:function(feature){
                return{
                    fillColor:"hsl(245,100%,"+shadeOfBlue(feature.properties.count)+"%)", 
                    fillOpacity:0.5,
                    color:"red",
                    weight:2
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

                layer.bindPopup("<h1>" + feature.properties.city + "</h1><hr><h2>Winners: "+feature.properties.count+"</h2>")
            }
        }).addTo(map);
    })
})