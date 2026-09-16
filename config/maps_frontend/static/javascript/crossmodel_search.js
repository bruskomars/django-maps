function setupCrossModelSearch(map) {
  const form = document.getElementById("address-search-form");

  let searchResultsLayer = null;

  // Create a message element once, append it under the form
  const messageBox = document.createElement("div");
  messageBox.id = "address-search-message";
  messageBox.style.display = "none";
  form.parentNode.appendChild(messageBox);

  // submit function in form
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    // preparing data from a form so it can be sent in a URL
    const formData = new FormData(form);
    const params = new URLSearchParams();

    // looping through all the form’s fields and building a clean query string
    for (const [key, value] of formData.entries()) {
      if (value.trim() !== "") {
        params.append(key, value.trim());
      }
    }

    // sends your query string to the backend and handles possible errors before parsing the JSON
    fetch(`/api/search/?${params.toString()}`)
      .then((response) => {
        if (response.status === 404) {
          throw new Error("NOT FOUND");
        }
        if (!response.ok) {
          throw new Error("SERVER_ERROR");
        }
        return response.json();
      })

      // success handler after fetch returns JSON
      .then((data) => {
        messageBox.style.display = "none";

        // remove previous layer on the map
        if (searchResultsLayer) {
          map.removeLayer(searchResultsLayer);
          searchResultsLayer = null;
        }

        const landmarkGeojson = data.results && data.results.landmark;

        if (
          !landmarkGeojson ||
          !landmarkGeojson.features ||
          landmarkGeojson.features.length === 0
        ) {
          messageBox.textContent = "No results found for that search.";
          messageBox.style.display = "block";
          return;
        }

        searchResultsLayer = L.geoJSON(landmarkGeojson, {
          pointToLayer: function (feature, latlng) {
            return L.marker(latlng);
          },
          // runs for every feature in your GeoJSON for custom behavior
          onEachFeature: function (feature, layer) {
            // build popup string using feature properties
            const p = feature.properties;

            const popupText = [p.name, p.admin.barangay, p.admin.city]
              // remove falsy values
              .filter(Boolean)
              .join(", ");
            layer.bindPopup(popupText);
          },
        }).addTo(map);

        // zooming the map to search results if any
        map.fitBounds(searchResultsLayer.getBounds(), {
          padding: [50, 50],
          maxZoom: 17,
        });
      })
      // error handleer if the .then blocks throws an error
      .catch((err) => {
        // Cleans up the map by removing any previous search results layer
        if (searchResultsLayer) {
          map.removeLayer(searchResultsLayer);
          searchResultsLayer = null;
        }
        if (err.message === "NOT_FOUND") {
          messageBox.textContent = "No results found for that address.";
        } else {
          messageBox.textContent = "Something went wrong. Please try again.";
        }
        // Makes the message box visible so the user sees the error message.
        messageBox.style.display = "block";
      });
  });
}
