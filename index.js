document.addEventListener('DOMContentLoaded', () => {
  const button = document.querySelector('#send');
  const responseDiv = document.querySelector('#response');

  button.addEventListener('click', async () => {
    const evtSource = new EventSource('/api/send_llm');
    evtSource.onmessage = (event) => {
        responseDiv.textContent += event.data + "\n";
    };
    evtSource.onerror = (err) => {
        responseDiv.textContent = 'Error: ' + err;
        evtSource.close();
    };
  });
});
