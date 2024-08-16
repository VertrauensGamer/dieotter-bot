import discord
from dotenv import load_dotenv
import os
import logging
from cogs import ticket

logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="latest.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

load_dotenv()

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} ist online!")
    bot.add_view(ticket.OpenTicket())
    activity = discord.Game(name="Die Otter Discord")
    await bot.change_presence(activity=activity)
    
    
@bot.event
async def on_member_join(member):
    member.add_roles(id=1273389944743923713)
    
@bot.slash_command(name="hallo", description="Just a test command")
async def test(ctx):
    await ctx.respond("Hallo!")
    
cogs_list = [
    'help',
    'ticket',
    'giveaway',
    'announcement'
]

for cog in cogs_list:
    bot.load_extension(f'cogs.{cog}')


bot.run(os.getenv("TOKEN"))