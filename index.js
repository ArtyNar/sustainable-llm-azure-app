document.addEventListener('DOMContentLoaded', () => {
  // Auto-fetch on load
  fetchCarbonIntesnityData();
  
  // Button click handler
  document.querySelector('#send').addEventListener('click', handleButtonClick);
});

async function fetchCarbonIntesnityData() {
  try {
    const res = await fetch('/api/carbon-intensity');
    const data = await res.json(); 
    document.querySelector('#response2').innerHTML = "Current carbon intensity: " + data.carbonIntensity + " gCO2eq/kWh <br>Grid: " + data.zone + " " + data.zone_name;
  } catch (err) {
      document.querySelector('#response2').textContent = 'Error: ' + err.message;
  }
}

async function handleButtonClick() {
  try {
    const res = await fetch('/api/send');
    const data = await res.json(); 
    document.querySelector('#response').textContent = data.message;
  } catch (err) {
    document.querySelector('#response').textContent = 'Error: ' + err.message;
  }
}