function setupAddressSearch(map) {
  const form = document.getElementById("address-search-form");
  let addressResultsLayer = null;

  // Create a message element once, append it under the form
  const messageBox = document.createElement("div");
  messageBox.id = "address-search-message";
  messageBox.style.display = "none";
  form.parentNode.appendChild(messageBox);

  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const formData = new FormData(form);
    const params = new URLSearchParams();

    for (const [key, value] of formData.entries()) {
      if (value.trim() !== "") {
        params.append(key, value.trim());
      }
    }

    fetch(`/api/address-search/?${params.toString()}`)
      .then((response) => {
        if (response.status === 404) {
          throw new Error("NOT_FOUND");
        }
        if (!response.ok) {
          throw new Error("SERVER_ERROR");
        }
        return response.json();
      })
      .then((data) => {
        messageBox.style.display = "none";

        if (addressResultsLayer) {
          map.removeLayer(addressResultsLayer);
        }

        addressResultsLayer = L.geoJSON(data, {
          pointToLayer: function (feature, latlng) {
            return L.marker(latlng);
          },
          onEachFeature: function (feature, layer) {
            const p = feature.properties;

            const addressLine = [p.hn, p.sn].filter(Boolean).join(" ");
            const popupText = [
              addressLine,
              p.subdivision,
              p.barangay,
              p.municipality,
            ]
              .filter(Boolean)
              .join(", ");
            layer.bindPopup(popupText);
          },
        }).addTo(map);

        if (data.features && data.features.length > 0) {
          map.fitBounds(addressResultsLayer.getBounds(), {
            padding: [50, 50],
            maxZoom: 17,
          });
        }
      })
      .catch((err) => {
        if (addressResultsLayer) {
          map.removeLayer(addressResultsLayer);
          addressResultsLayer = null;
        }

        if (err.message === "NOT_FOUND") {
          messageBox.textContent = "No results found for that address.";
        } else {
          messageBox.textContent = "Something went wrong. Please try again.";
        }
        messageBox.style.display = "block";
      });
  });
}
