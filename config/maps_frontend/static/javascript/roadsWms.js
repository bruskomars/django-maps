// roadsWms.js
// Standalone GeoServer WMS overlay for roads — separate from LAYER_CONFIG search flow

const ROADS_WMS_URL = "http://localhost:8080/geoserver/mapsapp/wms";

const roadsWmsLayer = L.tileLayer.wms(ROADS_WMS_URL, {
  layers: "mapsapp:roads",
  format: "image/png",
  transparent: true,
  version: "1.1.1",
  attribution: "GeoServer",
});

function setupRoadsWmsLayer(map) {
  roadsWmsLayer.addTo(map);

  map.on("click", function (e) {
    const size = map.getSize();
    const point = map.latLngToContainerPoint(e.latlng, map.getZoom());

    const params = {
      request: "GetFeatureInfo",
      service: "WMS",
      srs: "EPSG:4326",
      styles: "",
      transparent: true,
      version: "1.1.1",
      format: "image/png",
      bbox: map.getBounds().toBBoxString(),
      height: size.y,
      width: size.x,
      layers: "mapsapp:roads",
      query_layers: "mapsapp:roads",
      info_format: "application/json",
      x: Math.round(point.x),
      y: Math.round(point.y),
    };

    const url =
      ROADS_WMS_URL + L.Util.getParamString(params, ROADS_WMS_URL, true);

    fetch(url)
      .then((res) => res.json())
      .then((data) => {
        if (data.features.length > 0) {
          const props = data.features[0].properties;
          const fullName = [props.pf, props.name, props.name_sf]
            .filter(Boolean)
            .join(" ");
          L.popup()
            .setLatLng(e.latlng)
            .setContent(fullName || "Unnamed road")
            .openOn(map);
        }
      })
      .catch((err) => console.error("GetFeatureInfo error:", err));
  });
}
