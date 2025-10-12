document.addEventListener('DOMContentLoaded', () => {
  // Auto-fetch on load
  fetchCarbonIntesnityData();
  
  // Button click handler
  document.querySelector('#send').addEventListener('click', handleButtonClick);
});

async function fetchCarbonIntesnityData() {
  const { text } = await (await fetch('/api/send')).json();
  document.querySelector('#response2').textContent = "Current carbon intensity goes here" + text;
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