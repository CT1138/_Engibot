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

async function fetchAllGuilds() {
  try {
    const response = await fetch('/guilds');
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const guilds = await response.json();

    // Example: log to console or update your UI
    console.log(guilds);

    // For example, render to a div
    const container = document.getElementById('guilds-container');
    container.innerHTML = ''; // clear previous content

    guilds.forEach(guild => {
      const guildDiv = document.createElement('div');
      guildDiv.className = 'guild';

      guildDiv.innerHTML = `
        <h3>${guild.name} (${guild.member_count} members)</h3>
        <p><strong>Description:</strong> ${guild.description || 'N/A'}</p>
        <p><strong>Owner:</strong> ${guild.owner_name}</p>
        <img src="https://cdn.discordapp.com/icons/${guild.id}/${guild.icon}.png" alt="Icon" width="64" height="64" />
      `;

      container.appendChild(guildDiv);
    });
  } catch (error) {
    console.error('Failed to fetch guilds:', error);
  }
}

// Call it once page loads or whenever needed
fetchAllGuilds();


setInterval(fetchStats, 2000);
fetchStats();
