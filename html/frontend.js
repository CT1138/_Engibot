async function fetchStats() {
  try {
    const response = await fetch('/stats.json');
    if (!response.ok) throw new Error('Network response was not ok');
    const data = await response.json();

    document.getElementById('cpu').textContent = `${data.cpu}%`;
    document.getElementById('memory').textContent = `${data.memory}%`;
    document.getElementById('guilds').textContent = data.guilds;
    document.getElementById('ip').textContent = data.ip;
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

setInterval(fetchStats, 2000);
fetchStats();
