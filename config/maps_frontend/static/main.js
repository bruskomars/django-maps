document.addEventListener("DOMContentLoaded", init);

function init() {
  // Leaflet map initialization
  const map = L.map("map").setView([14.516589, 121.019333], 13);
  L.tileLayer(
    "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}",
    {
      attribution:
        "Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ, USGS, Intermap, iPC, NRCAN, Esri Japan, METI, Esri China (Hong Kong), Esri (Thailand), TomTom, 2012",
    },
  ).addTo(map);

  // fetch data from the backend API
  const fetchGetRequest = async (url, func) => {
    try {
      const response = await fetch(url);
      const data = await response.json();
      func(data);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  // call city search function
  setupCitySearch(map);
}
