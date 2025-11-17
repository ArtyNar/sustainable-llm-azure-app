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
    const promptText = document.getElementById('prompt').value;
    
    const res = await fetch('/api/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: promptText
      })
    });
    
    let data;

    try {
      data = await res.json(); // try to parse JSON
    } catch (e) {
      data = { error: "Invalid JSON from server" };
    }

    if (!res.ok) {
      // handle non-200 responses
      document.querySelector('#response').textContent = data.error || "Request failed";
      return;
    }

    document.querySelector('#response').textContent = data.message;

  } catch (err) {
    document.querySelector('#response').textContent = 'Error: ' + err.message;
  }
}