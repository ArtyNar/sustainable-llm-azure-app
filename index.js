document.addEventListener('DOMContentLoaded', () => {
  // Auto-fetch on load
  fetchCarbonIntesnityData();
  
  // Send button click handler
  document.querySelector('#send').addEventListener('click', handleSend);

  // Schedule button click handler
  document.querySelector('#schedule').addEventListener('click', handleSchedule);
});

async function fetchCarbonIntesnityData() {
  try {
    const res = await fetch('/api/carbon-intensity');
    const data = await res.json(); 
    document.querySelector('#response2').innerHTML = "Current carbon intensity: <b>" + data.carbonIntensity +" gCO2eq/kWh</b><br>Grid: " + data.zone + " " + data.zone_name;
  } catch (err) {
      document.querySelector('#response2').textContent = 'Error: ' + err.message;
  }
}

async function handleSend() {
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
      document.querySelector('#response').innerHTML = data.error || "Request failed";
      return;
    }

    document.querySelector('#response').innerHTML = data.message;

  } catch (err) {
    document.querySelector('#response').innerHTML = 'Error: ' + err.message;
  }
}

async function handleSchedule() {
  try {
    const promptText = document.getElementById('prompt').value;
    
    const res = await fetch('/api/schedule', {
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
      document.querySelector('#response').innerHTML = data.error || "Request failed";
      return;
    }

    document.querySelector('#response').textContent = data.message;

  } catch (err) {
    document.querySelector('#response').textContent = 'Error: ' + err.message;
  }
}