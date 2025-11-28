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
    console.log(res)
    const data = await res.json(); 
    console.log("EM current CI:", data)
    document.querySelector('#EMresponse').innerHTML = "Current carbon intensity: <b>" + data.carbonIntensity +" gCO2eq/kWh</b>";
    document.querySelector('#grid').innerHTML = "Grid: " + data.zone + " " + data.zone_name;
  } catch (err) {
      document.querySelector('#EMresponse').textContent = '<p class="text-danger  m-0 p-0">' + err.message + '</p>'  ;
  }
}

async function fetchPrompts() {
  try {
    const res = await fetch('/api/prompts');

    try {
      data = await res.json(); // try to parse JSON
    } catch (e) {
      data = { error: "Invalid JSON from server" };
    }

    console.log('Elements in store:', data);

    pending = data.filter(obj => obj.status === "pending");

    if (pending.length === 0){
      document.querySelector('#response3').innerHTML = "<li class=\"list-group-item text-center\">Nothing here yet</li>";
    }
    else
    {
      const html = pending.map(item => {
        const badgeClass =  "bg-warning text-dark";
        const ci_c = item.carbonIntensity_C === 0 ? "" : item.carbonIntensity_C;

        return `<li class="list-group-item">
          <strong>${item.timestamp}</strong><br>
            <small>Status: <span class="badge badge-pill ${badgeClass}">${item.status}</span> 
            <br> Model: <span class="badge badge-pill bg-secondary text-light">${item.model}</span> 
            <br> Scheduled for: <span class="badge badge-pill bg-light text-dark">${item.schedule}</span> 
            <br> Carbon Intensity (schedule time) : ${item.carbonIntensity_S} 
            <br><strong>Prompt:</strong><br> ${item.prompt} 
          </small>
        </li>`;
      }).join('');
        
      document.querySelector('#response3').innerHTML = html;
    }

    completed = data.filter(obj => obj.status === "completed");

    if (completed.length === 0){
      document.querySelector('#response4').innerHTML = "<li class=\"list-group-item text-center\">Nothing here yet</li>";
    }
    else
    {
      const html = completed.map((item, index) => {
        const badgeClass = "bg-success";
        const accordionId = `accordionResponse${index}`;
        const collapseId = `collapseOne${index}`;

        return `<li class="list-group-item">
          <strong>${item.timestamp}</strong><br>
            <small>Status: <span class="badge badge-pill ${badgeClass}">${item.status}</span> 
            <br> Model: <span class="badge badge-pill bg-secondary text-light">${item.model}</span> 
            <br> Scheduled for: <span class="badge badge-pill bg-light text-dark">${item.schedule}</span> 
            <br> Completed on: ${item.completedAt} 
            <br> Output tokens : ${item.outTokens} 
            <br> Carbon Intensity (schedule time) : ${item.carbonIntensity_S} 
            <br> Carbon Intensity (execution time) : ${item.carbonIntensity_C} 
            <br><strong>Prompt:</strong><br> ${item.prompt} 

            <div class="accordion mt-2 mb-2" id="${accordionId}">
              <div class="accordion-item">
                <h2 class="accordion-header">
                  <button class="accordion-button collapsed p-2" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                    See Response
                  </button>
                </h2>
                <div id="${collapseId}" class="accordion-collapse collapse" data-bs-parent="#${accordionId}">
                  <div class="accordion-body">
                     ${item.response} 
                  </div>
                </div>
              </div>
            </div>
          </small>
        </li>`;
      }).join('');
        
    document.querySelector('#response4').innerHTML = html;
    }
  } catch (err) {
    document.querySelector('#response3').textContent = 'Error: ' + err.message;
    document.querySelector('#response4').textContent = 'Error: ' + err.message;

  }
}


async function handleSend() {
  try {
    const promptText = document.getElementById('prompt').value;
    const model = document.getElementById('model').value;

    //console.log(model);

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
      document.querySelector('#response').innerHTML = '<p class="text-danger  m-0 p-0">' + data.error + '</p>'  || '<p class="text-danger">Request failed.</p>';
      return;
    }

    document.querySelector('#response').innerHTML = data.message + '\n\n<code class="text-success">Output tokens: ' + data.out_tokens + '</code>';

  } catch (err) {
    document.querySelector('#response').innerHTML = 'Error: ' + err.message;
  }
}

async function handleSchedule() {
  try {
    const promptText = document.getElementById('prompt').value;
    const model = document.getElementById('model').value;
    const schedule = document.getElementById('schedule-choise').value;

    if (schedule === "None"){
      document.querySelector('#response').innerHTML = '<p class="text-danger m-0 p-0">Please select a schedule.</p>';
      return;
    }

    const res = await fetch('/api/schedule', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        prompt: promptText,
        model: model,
        schedule: schedule
      })
    });
    
    console.log(res)
    let data;

    try {
      data = await res.json(); // try to parse JSON
    } catch (e) {
      data = { error: "Invalid JSON from server" };
    }

    if (!res.ok) {
      // handle non-200 responses
      document.querySelector('#response').innerHTML = '<p class="text-danger  m-0 p-0">' + data.error + '</p>' || '<p class="text-danger">Request failed.</p>';
      return;
    }

    document.querySelector('#response').textContent = data.message;
    document.getElementById('prompt').value = '';

    fetchPrompts()
  } catch (err) {
    document.querySelector('#response').textContent = 'Error: ' + err.message;
  }
}