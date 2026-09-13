// Config for each searchable layer: endpoint, query param, style, popup fields
const LAYER_CONFIG = {
  city: {
    url: "/api/city/",
    param: "city",
    style: { color: "black", weight: 2, fillColor: "blue", fillOpacity: 0.3 },
    geometryType: "polygon",
    popupFields: ["city", "barangay", "province"],
  },
  landmark: {
    url: "/api/landmark/",
    param: "name",
    style: {
      radius: 8,
      color: "black",
      weight: 2,
      fillColor: "green",
      fillOpacity: 1,
    },
    geometryType: "point",
    popupFields: ["name"],
  },
  road: {
    url: "/api/road/",
    param: "name",
    style: { color: "red", weight: 3 },
    geometryType: "polyline",
    popupFields: ["name", "name_pf", "name_sf"],
  },
};

function setupLayerSearch(map) {
  var activeLayer; // holds the current search result layer
  const errorElement = document.getElementById("layer-search-error");

  // function to build popup
  const buildPopupHtml = (properties, fields) => {
    return fields
      .map((field) => `<p>${field}: ${properties[field] ?? "N/A"}</p>`)
      .join("");
  };

  const addResultToMap = (geojson, config) => {
    errorElement.textContent = "";
    if (activeLayer) {
      map.removeLayer(activeLayer);
    }

    const geoJsonOptions = {
      onEachFeature: function (feature, layer) {
        layer.bindPopup(buildPopupHtml(feature.properties, config.popupFields));
      },
    };

    if (config.isPolygon) {
      geoJsonOptions.style = config.style;
    } else {
      geoJsonOptions.pointToLayer = function (feature, latlng) {
        return L.circleMarker(latlng, config.style);
      };
    }

    activeLayer = L.geoJSON(geojson, geoJsonOptions).addTo(map);

    if (activeLayer.getLayers().length > 0) {
      map.fitBounds(activeLayer.getBounds(), { maxZoom: 15 });
    }
  };

  const searchLayer = async () => {
    const layerType = document.getElementById("layer-select").value;
    const searchValue = document
      .getElementById("layer-search-input")
      .value.trim();
    const config = LAYER_CONFIG[layerType];

    if (!searchValue) {
      errorElement.textContent = "Please enter a search value";
      return;
    }

    const url = `${config.url}?${config.param}=${encodeURIComponent(searchValue)}`;

    try {
      const response = await fetch(url);

      if (response.status === 404) {
        errorElement.textContent = `${layerType} not found`;
        if (activeLayer) map.removeLayer(activeLayer);
        return;
      }

      if (response.status === 400) {
        errorElement.textContent = "Invalid search request";
        return;
      }

      if (!response.ok) {
        errorElement.textContent = "Something went wrong. Try again.";
        return;
      }

      const data = await response.json();
      addResultToMap(data, config);
    } catch (error) {
      console.error("Error fetching layer:", error.message);
      errorElement.textContent = "Network error. Try again.";
    }
  };

  document
    .getElementById("layer-search-btn")
    .addEventListener("click", searchLayer);
  document
    .getElementById("layer-search-input")
    .addEventListener("keydown", (e) => {
      if (e.key === "Enter") searchLayer();
    });
}
