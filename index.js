document.addEventListener('DOMContentLoaded', () => {
  // Auto-fetch on load
  fetchCarbonIntesnityData();
  fetchPrompts();
  plotChart();

  // Send button click handler
  document.querySelector('#send').addEventListener('click', handleSend);

  // Schedule button click handler
  document.querySelector('#schedule').addEventListener('click', handleSchedule);
});

async function plotChart() {
    try {
      const res = await fetch('/api/carbon-intensity-past');
      const data = await res.json(); 
      console.log("EM past CI:", data.intensities)
    } catch (err) {
      console.error("EM past CI:", data)
    }
  const ctx = document.getElementById('myChart').getContext('2d');
          const myChart = new Chart(ctx, {
              type: 'line',
              data: {
                  labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
                  datasets: [{
                      label: 'Carbon Intensity (gCO2eq/kWh)',
                      data: [6, 10, 3, 5, 2, 3],
                      backgroundColor: [
                          'rgba(255, 206, 86, 0.2)',
                      ],
                      borderColor: [
                          'rgba(255, 206, 86, 1)',
                      ],
                      borderWidth: 1
                  }]
              }
          });
        }

async function fetchCarbonIntesnityData() {
  try {
    const res = await fetch('/api/carbon-intensity');
    const data = await res.json(); 
    console.log("EM current CI:", data)
    document.querySelector('#response2').innerHTML = "Current carbon intensity: <b>" + data.carbonIntensity +" gCO2eq/kWh</b><br>Grid: " + data.zone + " " + data.zone_name;
  } catch (err) {
      document.querySelector('#response2').textContent = 'Error: ' + err.message;
  }
}

async function fetchPrompts() {
  try {
    const res = await fetch('/api/prompts');
    const data = await res.json(); 
    console.log('Raw response:', data);

    const html = data.map(item => 
      `<li class="list-group-item">
        <strong>${item.prompt}</strong><br>
        <small>Status: ${item.status} | Carbon: ${item.carbonIntensity}</small>
      </li>`
    ).join('');
    
    document.querySelector('#response3').innerHTML = html;
  } catch (err) {
    document.querySelector('#response3').textContent = 'Error: ' + err.message;
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