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
    data_from_EM = {}
    try {
      const res = await fetch('/api/carbon-intensity-past');
      data_from_EM = await res.json(); 
      console.log("EM past CI:", data_from_EM)
    } catch (err) {
      console.error("EM past CI:", data_from_EM)
    }
    const data = {
            labels: data_from_EM.stamps,
            datasets: [{
                label: 'Carbon Intensity (gCO2eq/kWh)',
                data: data_from_EM.intensities,
                backgroundColor: [
                    'rgba(255, 206, 86, 0.2)',
                ],
                borderColor: [
                    'rgba(255, 206, 86, 1)',
                ],
                borderWidth: 1
            }]
        }
    const chart = {
        type: 'line',
        data: data
    }
    const ctx = document.getElementById('myChart').getContext('2d');
    const myChart = new Chart(ctx, chart);
  }

async function fetchCarbonIntesnityData() {
  try {
    const res = await fetch('/api/carbon-intensity');
    const data = await res.json(); 
    console.log("EM current CI:", data)
    document.querySelector('#EMresponse').innerHTML = "Current carbon intensity: <b>" + data.carbonIntensity +" gCO2eq/kWh</b>";
    document.querySelector('#grid').innerHTML = "Grid: " + data.zone + " " + data.zone_name;
  } catch (err) {
      document.querySelector('#EMresponse').textContent = 'Error: ' + err.message;
  }
}

async function fetchPrompts() {
  try {
    const res = await fetch('/api/prompts');
    const data = await res.json(); 
    console.log('Elements in store:', data);

    const html = data.map(item => 
      `<li class="list-group-item">
        <strong>${item.prompt}</strong><br>
        <small>Status: <span class="badge badge-pill bg-warning text-dark">${item.status}</span> | Carbon: ${item.carbonIntensity}</small>
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
    const model = document.getElementById('model').value;

    console.log(model);

    const res = await fetch('/api/send', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: promptText,
        model: model
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

    document.querySelector('#response').innerHTML = data.message + '\n\n<code>Output tokens: ' + data.out_tokens + '</code>';

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