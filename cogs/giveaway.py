import discord
from discord.ext import commands
import asyncio
import uuid
import datetime
from main import get_db_collections

# UI Components
class GiveawayButton(discord.ui.View):
    def __init__(self, giveaway_id):
        super().__init__()
        self.giveaway_id = giveaway_id

    @discord.ui.button(label="Enter Giveaway🎉", style=discord.ButtonStyle.green)
    async def button_callback(self, button, interaction):
        _, entrycol = get_db_collections()
        user = interaction.user

        if entrycol.find_one({"user_id": user.id, "giveaway_id": self.giveaway_id}):
            await interaction.response.send_message("You've already entered the Giveaway!", ephemeral=True)
        else:
            entrycol.insert_one({"user_id": user.id, "user_name": user.name, "giveaway_id": self.giveaway_id})
            await interaction.response.send_message("You've entered the Giveaway!", ephemeral=True)

# Cog
class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}
        self.giveaway_messages = {}

    @discord.slash_command()
    @commands.has_permissions(administrator=True)
    async def giveaway_create(
        self,
        ctx: discord.ApplicationContext,
        giveaway_item: discord.Option(str, "The Giveaway Item"),
        time_in_mins: discord.Option(int, "How long in mins"),
        num_winners: discord.Option(int, "Number of winners", default=1, min_value=1)
    ):
        giveawaycol, entrycol = get_db_collections()

        giveaway_id = str(uuid.uuid4())
        giveawaycol.insert_one({"giveaway_id": giveaway_id, "item": giveaway_item, "num_winners": num_winners})
        self.active_giveaways[giveaway_id] = True

        end_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=int(time_in_mins))

        embed = self.create_giveaway_embed(ctx, giveaway_item, time_in_mins, end_time, num_winners)

        interaction = await ctx.respond(embed=embed, view=GiveawayButton(giveaway_id))
        message = await interaction.original_response()
        self.giveaway_messages[giveaway_id] = message

        await self.giveaway_timer(ctx, giveawaycol, entrycol, giveaway_id, giveaway_item, time_in_mins, message, embed)

    @discord.slash_command()
    @commands.has_permissions(administrator=True)
    async def endgiveaway(
        self,
        ctx: discord.ApplicationContext,
        giveaway_item: discord.Option(str, "Input the giveaway Item of the giveaway you want to end")
    ):
        giveawaycol, entrycol = get_db_collections()

        giveaway = giveawaycol.find_one({"item": giveaway_item})
        if giveaway:
            giveaway_id = giveaway["giveaway_id"]
            self.active_giveaways[giveaway_id] = False
            message = self.giveaway_messages.get(giveaway_id)
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

    async def giveaway_timer(self, ctx, giveawaycol, entrycol, giveaway_id, giveaway_item, time_in_mins, message, embed):
        giveaway = giveawaycol.find_one({"giveaway_id": giveaway_id})
        num_winners = giveaway.get("num_winners", 1)
        
        while time_in_mins > 0 and self.active_giveaways.get(giveaway_id):
            time_in_mins -= 1
            embed.set_field_at(0, name="⏳ Time Remaining", value=f"{time_in_mins} minutes", inline=False)
            await message.edit(embed=embed)
            await asyncio.sleep(60)

        if self.active_giveaways.get(giveaway_id):
            await self.end_giveaway(ctx, entrycol, giveawaycol, giveaway_id, giveaway_item, message, embed)

    async def end_giveaway(self, ctx, entrycol, giveawaycol, giveaway_id, giveaway_item, message, embed):
        giveaway = giveawaycol.find_one({"giveaway_id": giveaway_id})
        num_winners = giveaway.get("num_winners", 1)
        winners = await self.select_winner(ctx, entrycol, giveaway_id, num_winners)

        embed = self.create_end_giveaway_embed(giveaway_item, winners)

        if message:
            await message.edit(embed=embed, view=None)

        winners_mention = ", ".join(winners)
        await ctx.respond(f"🎊 Congratulations! {winners_mention} {'has' if len(winners) == 1 else 'have'} won the Giveaway for **{giveaway_item}**!")

        self.cleanup_giveaway(entrycol, giveawaycol, giveaway_id)

    def create_giveaway_embed(self, ctx, giveaway_item, time_in_mins, end_time, num_winners):
        embed = discord.Embed(
            title=f"🎉 Giveaway: **{giveaway_item}**",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="⏳ Duration", value=f"{time_in_mins} minutes", inline=False)
        embed.add_field(name="🏆 Prize", value=giveaway_item, inline=False)
        embed.add_field(name="🎊 Winners", value=f"{num_winners}", inline=False)
        embed.add_field(name="👥 Hosted by", value=ctx.author.mention, inline=False)
        embed.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.display_avatar.url}")
        embed.set_footer(text="VertrauensGamer • 🎉Click the Button to Entry!", icon_url="https://cdn.discordapp.com/avatars/466537555798654987/3d3a360eb92b3fccd9e4e7ddea831703.webp?size=80")
        embed.timestamp = end_time
        return embed

    def create_end_giveaway_embed(self, giveaway_item, winners):
        embed = discord.Embed(
            title=f"🎉 Giveaway Ended: **{giveaway_item}**",
            color=discord.Color.gold()
        )
        winners_text = "\n".join(winners) if isinstance(winners, list) else winners
        embed.add_field(name="🏆 Winner(s)", value=winners_text, inline=False)
        embed.set_footer(text="VertrauensGamer • Giveaway Ended", icon_url="https://cdn.discordapp.com/avatars/466537555798654987/3d3a360eb92b3fccd9e4e7ddea831703.webp?size=80")
        return embed

    async def select_winner(self, ctx, entrycol, giveaway_id, num_winners):
        winner_data = entrycol.aggregate([
            {'$match': {'giveaway_id': giveaway_id}},
            {'$sample': {'size': num_winners}}
        ])
        winners = []
        for winner_document in winner_data:
            winner_id = winner_document.get('user_id')
            winner_user = await ctx.guild.fetch_member(winner_id)
            winners.append(winner_user.mention)
            
        return winners if winners else ["Nobody"]

    def cleanup_giveaway(self, entrycol, giveawaycol, giveaway_id):
        entrycol.delete_many({"giveaway_id": giveaway_id})
        giveawaycol.delete_one({"giveaway_id": giveaway_id})
        self.active_giveaways.pop(giveaway_id, None)
        self.giveaway_messages.pop(giveaway_id, None)

def setup(bot):
    bot.add_cog(Giveaway(bot))