import discord
from discord.ext import commands
import asyncio
from pymongo import MongoClient

class GiveawayButton(discord.ui.View):
    @discord.ui.button(label="Entry Giveaway", style=discord.ButtonStyle.green)
    async def button_callback(self, button, interaction):
        
        client = MongoClient("mongodb://localhost:27017/")
        giveawaydb = client["DiscordBotDB"]
        checkdb = client.list_database_names()
        collection = giveawaydb["GiveawayCollection"]
        checkcol = giveawaydb.list_collection_names()
        
        user = interaction.user
        guild = interaction.guild
        
        if collection.find_one({"user_id": user.id}):
            await interaction.response.send_message("You've already entered the Giveaway!", ephemeral=True)
        else:
            collection.insert_one({"user_id": user.id, "user_name": user.name})
            await interaction.response.send_message("You've entered the Giveaway!", ephemeral=True)
            

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        
    @discord.slash_command()
    async def startgiveaway(
        self,
        ctx: discord.ApplicationContext,
        giveaway_item: discord.Option(str, "The Giveaway Item"),
        time_in_mins: discord.Option(int, "How long in mins"),
    ):
        
        client = MongoClient("mongodb://localhost:27017/")
        giveawaydb = client["GiveawayDB"]
        checkdb = client.list_database_names()
        collection = giveawaydb["GiveawayCollect"]
        checkcol = giveawaydb.list_collection_names()
        
        embed = discord.Embed(
            title=f"Entry to win: **{giveaway_item}**",
            description=f"{time_in_mins} minutes remaining",
            color=discord.Color.dark_purple()
        )
        
        message = await ctx.respond(embed=embed, view=GiveawayButton())
        
        while time_in_mins > 0:
            time_in_mins -= 1
            embed.description = f"{time_in_mins} minutes remaining"
            await message.edit_original_response(embed=embed)
            await asyncio.sleep(60)
        
        
        winner_data = collection.aggregate([{'$sample': {'size': 1}}])
        winner_document = next(winner_data, None)
        if winner_document:
            winner = winner_document.get('user_name', 'N/A')
        else:
            winner = "No Entry"
        
        
        embed.description = "**GIVEAWAY ENDED**"
        embed.color = discord.Color.red()
        await message.edit_original_response(embed=embed)
        await ctx.send(f"{winner} has won the Giveaway!")
        collection.delete_many({})
        
def setup(bot):
    bot.add_cog(Giveaway(bot))
    