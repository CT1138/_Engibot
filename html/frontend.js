async function loadGuilds() {
  try {
    const res = await fetch("http://127.0.0.1:8000/guilds");
    if (!res.ok) throw new Error("Network response was not ok");
    console.log("Fetching guilds...");
    const guilds = await res.json();

    document.getElementById("guilds").textContent = guilds.length;

    const guildList = document.getElementById("guild-list");
    guildList.innerHTML = "";

    guilds.forEach(guild => {
      const card = document.createElement("div");
      card.className = "guild-card";

      // Guild icon
      const icon = document.createElement("img");
      icon.src = guild.icon_url || "https://via.placeholder.com/80?text=No+Icon";
      icon.alt = `${guild.name} icon`;
      card.appendChild(icon);

      // Guild name
      const name = document.createElement("div");
      name.className = "guild-name";
      name.textContent = guild.name;
      card.appendChild(name);

      // Member count
      const members = document.createElement("div");
      members.className = "member-count";
      members.textContent = `${guild.member_count} members`;
      card.appendChild(members);

      guildList.appendChild(card);
    });
  } catch (error) {
    console.error("Failed to load guilds:", error);
    document.getElementById("guilds").textContent = "Error";
  }
}

loadGuilds();
setInterval(loadGuilds, 2000);
