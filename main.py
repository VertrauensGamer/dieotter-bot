import discord
from dotenv import load_dotenv
import os
import logging
from cogs import ticket
from pymongo import MongoClient

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="latest.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()

bot = discord.Bot()

@bot.event
async def on_ready():
    
    client = MongoClient("mongodb://localhost:27017/")
    db = client["DiscordBotDB"]
    giveawaycol = db["GiveawayCollection"]
    entrycol = db["GiveawayEntry"]
    
    entrycol.delete_many({})
    giveawaycol.delete_many({})
    
    print(f"{bot.user} ist online!")
    bot.add_view(ticket.OpenTicket())
    activity = discord.Game(name="Die Otter Discord")
    await bot.change_presence(activity=activity)
    
cogs_list = [
    'help',
    'ticket',
    'giveaway',
    'announcement',
    'oil',
    'moderation',
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')


bot.run(os.getenv("TOKEN"))