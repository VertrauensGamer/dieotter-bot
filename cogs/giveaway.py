import discord
from discord.ext import commands
import asyncio
from pymongo import MongoClient
import uuid
import datetime

class GiveawayButton(discord.ui.View):

    def __init__(self, giveaway_id):
        super().__init__()
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="Enter Giveaway🎉", style=discord.ButtonStyle.green)
    async def button_callback(self, button, interaction):
        client = MongoClient("mongodb://localhost:27017/")
        giveawaydb = client["DiscordBotDB"]
        entrycol = giveawaydb["GiveawayEntry"]
        user = interaction.user

        if entrycol.find_one({"user_id": user.id, "giveaway_id": self.giveaway_id}):
            await interaction.response.send_message("You've already entered the Giveaway!", ephemeral=True)
        else:
            entrycol.insert_one({"user_id": user.id, "user_name": user.name, "giveaway_id": self.giveaway_id})
            await interaction.response.send_message("You've entered the Giveaway!", ephemeral=True)

class Giveaway(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}
        self.giveaway_messages = {}  # To store message references
        super().__init__()

    @discord.slash_command()
    @commands.has_permissions(administrator=True)
    async def giveaway_create(
        self,
        ctx: discord.ApplicationContext,
        giveaway_item: discord.Option(str, "The Giveaway Item"), # type: ignore
        time_in_mins: discord.Option(int, "How long in mins") # type: ignore
    ):
        client = MongoClient("mongodb://localhost:27017/")
        giveawaydb = client["DiscordBotDB"]
        giveawaycol = giveawaydb["GiveawayCollection"]
        entrycol = giveawaydb["GiveawayEntry"]

        giveaway_id = str(uuid.uuid4())
        giveawaycol.insert_one({"giveaway_id": giveaway_id, "item": giveaway_item})
        self.active_giveaways[giveaway_id] = True

        end_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=int(time_in_mins))

        embed = discord.Embed(
            title=f"🎉 Giveaway: **{giveaway_item}**",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="⏳ Duration", value=f"{time_in_mins} minutes", inline=False)
        embed.add_field(name="🏆 Prize", value=giveaway_item, inline=False)
        embed.add_field(name="👥 Hosted by", value=ctx.author.mention, inline=False)
        embed.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.display_avatar.url}")
        embed.set_footer(text="VertrauensGamer • 🎉Click the Button to Entry!", icon_url="https://cdn.discordapp.com/avatars/466537555798654987/3d3a360eb92b3fccd9e4e7ddea831703.webp?size=80")
        embed.timestamp = end_time

        interaction = await ctx.respond(embed=embed, view=GiveawayButton(giveaway_id))
        message = await interaction.original_response()
        self.giveaway_messages[giveaway_id] = message

        while time_in_mins > 0 and self.active_giveaways.get(giveaway_id):
            time_in_mins -= 1
            embed.set_field_at(0, name="⏳ Time Remaining", value=f"{time_in_mins} minutes", inline=False)
            await message.edit(embed=embed)
            await asyncio.sleep(60)

        if self.active_giveaways.get(giveaway_id):
            await self.end_giveaway(ctx, entrycol, giveawaycol, giveaway_id, giveaway_item, message, embed)

    @discord.slash_command()
    @commands.has_permissions(administrator=True)
    async def endgiveaway(
        self,
        ctx: discord.ApplicationContext,
        giveaway_item: discord.Option(str, "Input the giveaway Item of the giveaway you want to end") # type: ignore
    ):
        client = MongoClient("mongodb://localhost:27017/")
        giveawaydb = client["DiscordBotDB"]
        giveawaycol = giveawaydb["GiveawayCollection"]
        entrycol = giveawaydb["GiveawayEntry"]

        giveaway = giveawaycol.find_one({"item": giveaway_item})
        if giveaway:
            giveaway_id = giveaway["giveaway_id"]
            self.active_giveaways[giveaway_id] = False
            message = self.giveaway_messages.get(giveaway_id)  # Retrieve the stored message
            embed = discord.Embed(
                title=f"🎉 Giveaway: **{giveaway_item}**",
                description="**GIVEAWAY ENDED**",
                color=discord.Color.gold()
            )
            if message:
                await message.edit(embed=embed)
            await self.end_giveaway(ctx, entrycol, giveawaycol, giveaway_id, giveaway_item, message, embed)
        else:
            await ctx.send("No active giveaway found for the specified item.")

    async def end_giveaway(self, ctx, entrycol, giveawaycol, giveaway_id, giveaway_item, message, embed):
        winner_data = entrycol.aggregate([
            {'$match': {'giveaway_id': giveaway_id}},
            {'$sample': {'size': 1}}
        ])
        winner_document = next(winner_data, None)

        if winner_document:
            winner_id = winner_document.get('user_id')
            winner_user = await ctx.guild.fetch_member(winner_id)
            winner = winner_user.mention
        else:
            winner = "Nobody"

        embed.title = f"🎉 Giveaway Ended: **{giveaway_item}**"
        embed.clear_fields()
        embed.add_field(name="🏆 Winner", value=winner, inline=False)
        embed.color = discord.Color.gold()
        embed.set_footer(text="VertrauensGamer • Giveaway Ended", icon_url="https://cdn.discordapp.com/avatars/466537555798654987/3d3a360eb92b3fccd9e4e7ddea831703.webp?size=80")

        if message:
            await message.edit(embed=embed, view=None)

        await ctx.send(f"🎊 Congratulations! {winner} has won the Giveaway for **{giveaway_item}**!")

        entrycol.delete_many({"giveaway_id": giveaway_id})
        giveawaycol.delete_one({"giveaway_id": giveaway_id})
        self.active_giveaways.pop(giveaway_id, None)
        self.giveaway_messages.pop(giveaway_id, None)

def setup(bot):
    bot.add_cog(Giveaway(bot))