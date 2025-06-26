from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import threading
import discord

HOST="0.0.0.0"
PORT=8000
ACCEPTABLE_ORIGINS=["http://localhost", "http://127.0.0.1", "http://localhost:8000", "http://192.168.68.12"]
class IF_Backend:
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.app = FastAPI(title="IF Backend API")

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=ACCEPTABLE_ORIGINS,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._define_routes()

    def _define_routes(self):
        @self.app.get("/status")
        async def get_status():
            if not self.bot.is_ready():
                return {
                    "online": False,
                    "message": "Bot not ready"
                }

            total_users = len(set(self.bot.users))  # Unique users across guilds
            return {
                "online": True,
                "message": "Bot online and ready"
            }
        
        @self.app.get("/guilds")
        async def get_guilds():
            guild_data = []
            for guild in self.bot.guilds:
                guild_data.append({
                    "id": guild.id,
                    "name": guild.name,
                    "member_count": guild.member_count,
                    "owner_id": guild.owner_id,
                    "icon_url": guild.icon.url if guild.icon else None
                })
            return guild_data

    def run(self):
        uvicorn.run(self.app, host=HOST, port=PORT)

    def start_in_background(self):
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
