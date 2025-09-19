document.addEventListener('DOMContentLoaded', () => {
  const button = document.querySelector('#send');
  const responseDiv = document.querySelector('#response');

  button.addEventListener('click', async () => {
    try {
      const res = await fetch('/api/send');
      const data = await res;
      responseDiv.textContent = data;
    } catch (err) {
      responseDiv.textContent = 'Error: ' + err.message;
    }
  });
});
