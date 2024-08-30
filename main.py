import datetime
import os
import logging
import time
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from pymongo import MongoClient
from cogs import ticket

# Load environment variables
load_dotenv()

# Constants
START_TIME = time.time()
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "DiscordBotDB"
GIVEAWAY_COLLECTION = "GiveawayCollection"
ENTRY_COLLECTION = "GiveawayEntry"
TICKET_COLLECTION = "TicketCollection"
COGS_LIST = [
    'help', 'ticket', 'giveaway', 'announcement', 'oil',
    'moderation', 'server_stats', 'music', 'feedback',
]

# Bot setup
bot = discord.Bot(intents=discord.Intents.all())

# Logging setup
def setup_logging():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)

# Database functions
def get_db_collections():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[GIVEAWAY_COLLECTION], db[ENTRY_COLLECTION]

def get_ticket_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db[TICKET_COLLECTION]

def get_feedback_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db["FeedbackCollection"]

def get_count_collection():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    return db["CountCollection"]

# Bot status and stats functions
@tasks.loop(seconds=1)
async def update_counts():
    server_count = len(bot.guilds)
    user_count = sum(len(guild.members) for guild in bot.guilds)
    uptime = bot_uptime()
    
    get_count_collection().update_one(
        {"_id": "bot_stats"},
        {"$set": {"server_count": server_count, "user_count": user_count, "bot_uptime": uptime}},
        upsert=True
    )

def update_bot_status(status):
    get_count_collection().update_one({"_id": "bot_stats"}, {"$set": {"status": str(status)}}, upsert=True)

def bot_uptime():
    current_time = time.time()
    difference = int(round(current_time - START_TIME))
    return str(datetime.timedelta(seconds=difference))

def clear_giveaway_data():
    giveawaycol, entrycol = get_db_collections()
    entrycol.delete_many({})
    giveawaycol.delete_many({})

# Bot events
@bot.event
async def on_ready():
    global START_TIME
    START_TIME = time.time()
    update_counts.start()
    update_bot_status("Online")
    clear_giveaway_data()
    print(f"{bot.user} ist online!")
    bot.add_view(ticket.OpenTicket())
    activity = discord.Game(name="Die Otter Discord")
    await bot.change_presence(activity=activity)

@bot.event
async def on_member_join(member: discord.Member):
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        await member.add_roles(role)
        print(f"Assigned {role} to {member.name}")

@bot.event
async def on_disconnect():
    update_bot_status("Offline")
    update_counts.stop()

# Cog loading
def load_cogs():
    for cog in COGS_LIST:
        bot.load_extension(f'cogs.{cog}')

# Main function
def main():
    setup_logging()
    load_cogs()
    bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    main()