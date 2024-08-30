import discord
from discord.ext import commands
from pymongo import MongoClient
import datetime
from main import get_ticket_collection

# Utility functions
def find_category(guild, category_name):
    return discord.utils.find(lambda c: c.name == category_name, guild.categories)

def find_role(guild, role_name):
    return discord.utils.find(lambda r: r.name == role_name, guild.roles)

def get_next_ticket_number(guild):
    max_number = 0
    for channel in guild.channels:
        if channel.name.startswith("ticket-"):
            try:
                number = int(channel.name.split("-")[1])
                max_number = max(max_number, number)
            except ValueError:
                continue
    return max_number + 1

# UI Components
class OpenTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green, emoji="🎫", custom_id="OpenTicket")
    async def button_callback(self, button, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user
        collection = get_ticket_collection()
        
        if collection.find_one({"user_id": user.id}):
            await interaction.response.send_message("You already have an open ticket", ephemeral=True)
            return

        category = find_category(guild, "tickets")
        role = find_role(guild, "Admin")
        if not category:
            category = await guild.create_category(name="tickets")

        ticket_number = get_next_ticket_number(guild)
        new_ticket = f"ticket-{ticket_number}"
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True)
        }
        
        await guild.create_text_channel(new_ticket, category=category, overwrites=overwrites)
        collection.insert_one({"user_id": user.id, "user_name": user.name, "ticket_name": new_ticket})
        await interaction.guild.get_channel(discord.utils.get(guild.channels, name=new_ticket).id).send(f"{user.mention} bitte beschreibe dein Problem und ein {role.mention} wird es bearbeiten.")
        await interaction.response.send_message(f"✅ Created your ticket! Channel: {new_ticket}", ephemeral=True)

class CloseTicket(discord.ui.View):
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, emoji="🔒")
    async def button_callback(self, button, interaction: discord.Interaction):
        guild = interaction.guild
        channel = interaction.channel
        collection = get_ticket_collection()

        category_new = find_category(guild, "archived-tickets")
        if not category_new:
            category_new = await guild.create_category(name="archived-tickets")

        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        
        collection.delete_one({"ticket_name": channel.name})
        await channel.edit(category=category_new, overwrites=overwrites)
        await interaction.response.send_message("🔒 The ticket was successfully closed!", ephemeral=True)

# Cog
class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.slash_command()
    @commands.has_permissions(administrator=True)
    async def ticket_message(self, ctx):
        embed = discord.Embed(
            title="🎫 Create a Ticket",
            description="Need assistance? Click the button below to open a new ticket!",
            color=discord.Colour.dark_purple(),
            timestamp=datetime.datetime.now(datetime.UTC)
        )
        guild_icon_url = ctx.guild.icon.url if ctx.guild.icon else None
        embed.set_footer(text="VertrauensGamer", icon_url=guild_icon_url)
        embed.set_author(name="Ticket System", icon_url=guild_icon_url)
        
        await ctx.respond(embed=embed, view=OpenTicket())
        
    @discord.slash_command()
    @commands.has_permissions(administrator=True)
    async def close_ticket(self, ctx: discord.ApplicationContext):
        collection = get_ticket_collection()
        
        if collection.find_one({"ticket_name": ctx.channel.name}):
            embed = discord.Embed(
                title="🔒 Close Ticket",
                description="Are you sure you want to close this ticket?",
                color=discord.Colour.dark_purple(),
                timestamp=datetime.datetime.now(datetime.UTC)
            )
            guild_icon_url = ctx.guild.icon.url if ctx.guild.icon else None
            embed.set_footer(text="VertrauensGamer", icon_url=guild_icon_url)
            embed.set_author(name=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
            await ctx.respond(embed=embed, view=CloseTicket())
        else:
            await ctx.respond("❌ This is not a ticket channel.", ephemeral=True)

def setup(bot):
    bot.add_cog(Ticket(bot))