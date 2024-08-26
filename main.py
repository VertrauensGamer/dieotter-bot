import os
import logging
import discord
from dotenv import load_dotenv
from pymongo import MongoClient
from cogs import ticket

# Load environment variables
load_dotenv()

# Constants
MONGO_URI = "mongodb://localhost:27017/"
DB_NAME = "DiscordBotDB"
GIVEAWAY_COLLECTION = "GiveawayCollection"
ENTRY_COLLECTION = "GiveawayEntry"
TICKET_COLLECTION = "TicketCollection"
COGS_LIST = [
    'help',
    'ticket',
    'giveaway',
    'announcement',
    'oil',
    'moderation',
]

# Set up logging
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

def clear_giveaway_data():
    giveawaycol, entrycol = get_db_collections()
    entrycol.delete_many({})
    giveawaycol.delete_many({})

# Bot setup
bot = discord.Bot(intents=discord.Intents.all())

@bot.event
async def on_ready():
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

def load_cogs():
    for cog in COGS_LIST:
        bot.load_extension(f'cogs.{cog}')

def main():
    setup_logging()
    load_cogs()
    bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    main()