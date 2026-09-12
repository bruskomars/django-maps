// city search functionality
function setupCitySearch(map) {
  var cityGeoJsonLayer; // holds the current searched city layer
  const cityErrorElement = document.getElementById("city-search-error");

  const addCityToMap = (geojson) => {
    cityErrorElement.textContent = ""; // clear previous error message
    if (cityGeoJsonLayer) {
      map.removeLayer(cityGeoJsonLayer); // remove previous city layer
    }
    cityGeoJsonLayer = L.geoJSON(geojson, {
      style: {
        color: "black",
        weight: 2,
        fillColor: "blue",
        fillOpacity: 0.3,
      },
      onEachFeature: function (feature, layer) {
        let city = feature.properties.city;
        let barangay = feature.properties.barangay;
        let province = feature.properties.province;
        layer.bindPopup(`<h4>${city}</h4>
            <p>Barangay: ${barangay}</p>
            <p>Province: ${province}</p>`);
      },
    }).addTo(map);

    if (cityGeoJsonLayer.getLayers().length > 0) {
      map.fitBounds(cityGeoJsonLayer.getBounds(), { maxZoom: 15 });
    }
  };

  const searchCity = async () => {
    const cityName = document.getElementById("city-search-input").value.trim();

    if (!cityName) {
      cityErrorElement.textContent = "Please enter a city name";
      return;
    }

    const url = `/api/city/?city=${encodeURIComponent(cityName)}`;

    try {
      const response = await fetch(url);

      if (response.status === 404) {
        cityErrorElement.textContent = "City not found";
        if (cityGeoJsonLayer) map.removeLayer(cityGeoJsonLayer);
        return;
      }

      if (response.status === 400) {
        cityErrorElement.textContent = "Invalid search request";
        return;
      }

      if (!response.ok) {
        cityErrorElement.textContent = "Something went wrong. Try again.";
        return;
      }

      const data = await response.json();
      addCityToMap(data);
    } catch (error) {
      console.error("Error fetching city", error.message);
      cityErrorElement.textContent = "Network error. Try again.";
    }
  };

  document
    .getElementById("city-search-btn")
    .addEventListener("click", searchCity);
  document
    .getElementById("city-search-input")
    .addEventListener("keydown", (e) => {
      if (e.key === "Enter") searchCity();
    });
}
