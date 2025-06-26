async function loadGuilds() {
  try {
    const res = await fetch("http://127.0.0.1:8000/guilds");
    if (!res.ok) throw new Error("Network response was not ok");

    const guilds = await res.json();
    const guildsContainer = document.getElementById("guilds");

    // Clear existing guild entries
    guildsContainer.innerHTML = "";

    // Create a guild entry for each guild in the data
    guilds.forEach(guild => {
      const guildElem = document.createElement("span");
      guildElem.className = "guild";

      // Guild icon
      const icon = document.createElement("img");
      icon.className = "guild-icon";
      icon.src = guild.icon_url || "https://via.placeholder.com/75?text=No+Icon";
      icon.alt = `${guild.name} icon`;
      guildElem.appendChild(icon);

      // Guild info container
      const info = document.createElement("div");
      info.className = "guild-info";

      // Guild name
      const name = document.createElement("div");
      name.className = "guild-name";
      name.textContent = guild.name;
      info.appendChild(name);

      // Member count
      const members = document.createElement("div");
      members.className = "guild-attr";
      members.textContent = `Members: ${guild.member_count}`;
      info.appendChild(members);

      // Owner ID
      const owner = document.createElement("div");
      owner.className = "guild-attr";
      owner.textContent = `Owner: ${guild.owner_name} (${guild.owner_id})`;
      info.appendChild(owner);

      guildElem.appendChild(info);
      guildsContainer.appendChild(guildElem);
    });

  } catch (error) {
    console.error("Failed to load guilds:", error);
  }
}

// Initial load and periodic refresh every 2 seconds
loadGuilds();
setInterval(loadGuilds, 2000);
