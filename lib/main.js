window.captial_one_recommends = { geojson: null, regions: null, accID: null, debug: false };
var map;
require([
    "esri/map",
    "esri/renderers/HeatmapRenderer",
    "esri/layers/FeatureLayer",
    "extras/ClusterLayer",
    "esri/geometry/Multipoint",
    "esri/dijit/PopupTemplate",
    "esri/request",
    "esri/geometry/Point",
    "esri/geometry/webMercatorUtils",
    "esri/graphic",
    "esri/symbols/SimpleMarkerSymbol",
    "esri/symbols/SimpleFillSymbol",
    "esri/symbols/PictureMarkerSymbol",
    "esri/renderers/ClassBreaksRenderer",
    "dojo/on",
    "dojo/_base/array",
    "dojo/domReady!"
], function(
        Map,
        HeatmapRenderer,
        FeatureLayer,
        ClusterLayer,
        Multipoint,
        PopupTemplate,
        esriRequest,
        Point,
        webMercatorUtils,
        Graphic,
        SimpleMarkerSymbol, SimpleFillSymbol, PictureMarkerSymbol, ClassBreaksRenderer,
        on,
        array
        ) {

    var featureLayer;
    map = new Map("map", {
        basemap: "gray",
        center: [0, 0],
        zoom: 16
    });

    //hide the popup if its outside the map's extent
    map.on("mouse-drag", function(evt) {
        if (map.infoWindow.isShowing) {
            var loc = map.infoWindow.getSelectedFeature().geometry;
            if (!map.extent.contains(loc)) {
                map.infoWindow.hide();
            }
        }
    });

    //create a feature collection for the flickr photos
    var featureCollection = {
        "layerDefinition": null,
        "featureSet": {
            "features": [],
            "geometryType": "esriGeometryPoint"
        }
    };

    featureCollection.layerDefinition = {
        "geometryType": "esriGeometryPoint",
        "objectIdField": "ObjectID",
        "drawingInfo": {
            "renderer": {
                "type": "simple",
                "symbol": {
                    "color": [255,255,255,64],
                    "size": 12,
                    "angle": -30,
                    "xoffset": 0,
                    "yoffset": 0,
                    "type": "esriSMS",
                    "style": "esriSMSCircle",
                    "outline": {
                        "color": [0,0,0,255],
                        "width": 1,
                        "type": "esriSLS",
                        "style": "esriSLSSolid"
                    }
                }
            }
        },
        "fields": [{
            "name": "ObjectID",
            "alias": "ObjectID",
            "type": "esriFieldTypeOID"
        }, {
            "name": "title",
            "alias": "Title",
            "type": "esriFieldTypeString"
        }]
    };

    //define a popup template
    var popupTemplate = new PopupTemplate({
        title: "{title}"
    });

    //create a feature layer based on the feature collection
    featureLayer = new FeatureLayer(featureCollection, {
        id: 'pointsLayer'
    });
    featureLayer.setRenderer(new HeatmapRenderer({
        blurRadius: 12,
        maxPixelIntensity: 45,
        minPixelIntensity: 0
    }));

    selectLayer = new FeatureLayer(featureCollection, {
        id: 'selectLayer'
    });

    map.on("layers-add-result", function(results) {
        captial_one_recommends.layersReady = true;
        syncWaitLayerGeojson();
    });

    //add the feature layer that contains the flickr photos to the map
    map.addLayers([selectLayer, featureLayer]);

    function syncWaitLayerGeojson() {
        if (captial_one_recommends.geojson && captial_one_recommends.layersReady) {
            console.log('Updating features');

            //loop through the items and add to the feature layer
            var features = [];
            captial_one_recommends.geojson.items.forEach(function(item) {
                var geometry = new Point(item)
                  , graphic = new Graphic(geometry);

                features.push(graphic);
            });

            console.log('Features');
            console.log(features);
            featureLayer.applyEdits(features, null, null);
            addClusters(captial_one_recommends.geojson.items);
        } else {
            setTimeout(syncWaitLayerGeojson, 50);
        }
    }

    function addClusters(items) {
        console.log('Clustering');

        var processed = { };
        processed.data = array.map(items, function(item) {
            var latlng = new Point(item)
              , webMercator = webMercatorUtils.geographicToWebMercator(latlng);
            return {
                "x": webMercator.x,
                "y": webMercator.y,
                "lat": latlng.latitude,
                "lng": latlng.longitude,
                "attributes": { }
            };
        });
        clusterLayer = new ClusterLayer({
            "data": processed.data,
            "distance": 200,
            "id": "clusters",
            "labelColor": "#fff",
            "labelOffset": 10,
            "resolution": map.extent.getWidth() / map.width,
            "singleColor": "#888",
            "no_click": true
        });
        var defaultSym = new SimpleMarkerSymbol().setSize(4);
        var renderer = new ClassBreaksRenderer(defaultSym, "clusterCount");

        var picBaseUrl = "http://static.arcgis.com/images/Symbols/Shapes/";
        var blue = new PictureMarkerSymbol(picBaseUrl + "BluePin1LargeB.png", 32, 32).setOffset(0, 15);
        var green = new PictureMarkerSymbol(picBaseUrl + "GreenPin1LargeB.png", 64, 64).setOffset(0, 15);
        var red = new PictureMarkerSymbol(picBaseUrl + "RedPin1LargeB.png", 72, 72).setOffset(0, 15);
        renderer.addBreak(0, 2, blue);
        renderer.addBreak(2, 200, green);
        renderer.addBreak(200, 1001, red);

        clusterLayer.setRenderer(renderer);
        if (!captial_one_recommends.debug) clusterLayer.hide();
        map.addLayer(clusterLayer);

        // Find cluster corners. WARNING: Doesn't work well around 180 longitude and by poles. This shouldn't matter
        var regions = loadRegions(clusterLayer);
        captial_one_recommends.regions = regions;

        // Debug region bounds
        if (captial_one_recommends.debug) debugRegions(regions);

        // Choose a random region to load from yelp
        var region;
        while(!region) region = regions[~~(Math.random() * regions.length)];
        loadYelp(region.sw_latitude, region.sw_longitude, region.ne_latitude, region.ne_longitude);
    }

    function loadRegions(clusterLayer) {
        var regions = [ ];
        console.log('Find cluster corners');
        clusterLayer.graphics.forEach(function (graphic) {
            console.log(graphic);
            var points = (graphic.attributes ? graphic.attributes.points : null)
              , id = graphic.attributes.clusterId;
            if (points && points.length > 1 && !regions[id]) {
                var ne_latitude, ne_longitude, sw_latitude, sw_longitude;
                points.forEach(function(p) {
                    var lat = parseFloat(p.lat), lng = parseFloat(p.lng);
                    if (!ne_latitude) ne_latitude = lat;
                    else if (lat > ne_latitude) ne_latitude = lat;

                    if (!ne_longitude) ne_longitude = lng;
                    else if (lng > ne_longitude) ne_longitude = lng;

                    if (!sw_latitude) sw_latitude = lat;
                    else if (lat < sw_latitude) sw_latitude = lat;

                    if (!sw_longitude) sw_longitude = lng;
                    else if (lng < sw_longitude) sw_longitude = lng;
                });

                // { ne_latitude, ne_longitude, sw_latitude, sw_longitude }
                regions[id] = { 
                    'ne_latitude': ne_latitude, 'ne_longitude': ne_longitude, 
                    'sw_latitude': sw_latitude, 'sw_longitude': sw_longitude 
                };
            }
        });

        return regions;
    }

    function debugRegions(regions) {
        console.log('Regions');
        console.log(regions);
        var features = [];
        regions.forEach(function(item) {
            var ne_graphic = new Graphic(new Point(item.ne_longitude, item.ne_latitude))
              , sw_graphic = new Graphic(new Point(item.sw_longitude, item.sw_latitude));

            features.push(ne_graphic);
            features.push(sw_graphic);
        });
        selectLayer.applyEdits(features, null, null);
    }

    function loadYelp(sw_latitude, sw_longitude, ne_latitude, ne_longitude) {
        $.post(
            '/yelp', 
            {
                'sw_latitude': sw_latitude, 'sw_longitude': sw_longitude, 
                'ne_latitude': ne_latitude, 'ne_longitude': ne_longitude
            },
            function(data) {
                data = JSON.parse(data);
                console.log(data);

                var business = data.businesses[~~(Math.random() * data.businesses.length)]
                  , coord = business.location.coordinate;

                console.log('Got business!');
                var point = new Point(coord.longitude, coord.latitude);
                selectLayer.applyEdits([ new Graphic(point) ], null, null);

                console.log(point);
                map.centerAndZoom(point, 16);
            }
        );
    }
});