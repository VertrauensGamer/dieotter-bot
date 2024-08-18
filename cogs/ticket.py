import discord
from discord.ext import commands
from pymongo import MongoClient


class OpenTicket(discord.ui.View):
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.green, custom_id="OpenTicket")
    async def button_callback(self, button, interaction):
        guild = interaction.guild
        user = interaction.user
        category = discord.utils.find(lambda c: c.name == "tickets", guild.categories)
        member_overwrites = {
                user: discord.PermissionOverwrite(view_channel=True),
                guild.default_role: discord.PermissionOverwrite(view_channel=False)
                }
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        global ticket_id
        client = MongoClient("mongodb://localhost:27017/")
        ticketdb = client["DiscordBotDB"]
        collection = ticketdb["TicketCollection"]
        
        if collection.find_one({"user_id": user.id}):
            await interaction.response.send_message("You already have a open Ticket", ephemeral=True)
            
        else:
            if category:
                max_number = 0
                for channel in guild.channels:
                    if channel.name.startswith("ticket-"):
                        try:
                            number = int(channel.name.split("-")[1])
                            if number > max_number:
                                max_number = number
                        except ValueError:
                            continue
                        
                new_ticket = f"ticket-{max_number + 1}"
                collection.insert_one({"user_id": user.id, "user_name": user.name, "ticket_name": f"{new_ticket}"})
                await guild.create_text_channel(new_ticket, category=category, overwrites=member_overwrites)
                await interaction.response.send_message(f"Created your Ticket! Ticketname: {new_ticket}", ephemeral=True)
            else:
                await guild.create_category(name="tickets", overwrites=overwrites)
                max_number = 0
                for channel in guild.channels:
                    if channel.name.startswith("ticket-"):
                        try:
                            number = int(channel.name.split("-")[1])
                            if number > max_number:
                                max_number = number
                        except ValueError:
                            continue
                        
                new_ticket = f"ticket-{max_number + 1}"
                collection.insert_one({"user_id": user.id, "user_name": user.name, "ticket_name": f"{new_ticket}"})
                await guild.create_text_channel(new_ticket, category=category, overwrites=member_overwrites)
                await interaction.response.send_message(f"Created your Ticket! Ticketname: {new_ticket}", ephemeral=True)
            
class CloseTicket(discord.ui.View):
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red)
    async def button_callback(self, button, interaction: discord.Interaction):
        guild = interaction.guild
        channel = interaction.channel
        category = discord.utils.find(lambda c: c.name == "archived-tickets", guild.categories)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False)
        }
        
        client = MongoClient("mongodb://localhost:27017/")
        ticketdb = client["DiscordBotDB"]
        collection = ticketdb["TicketCollection"]
        

        if category:
            collection.delete_one({"ticket_name": f"{channel.name}"})
            await channel.edit(category=category, overwrites=overwrites)
            await interaction.response.send_message("The Ticket was successfully closed!", ephemeral=True)
        else:
            collection.delete_one({"ticket_name": f"{channel.name}"})
            await guild.create_category(name="archived-tickets", overwrites=overwrites)
            await channel.edit(category=category, overwrites=overwrites)
            await interaction.response.send_message("The Ticket was successfully closed!", ephemeral=True)
        
class ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.slash_command()
    async def ticket_message(self, ctx):
        
        embed = discord.Embed(
            title="Create a Ticket!",
            description="To create a ticket press the button below!",
            color=discord.Colour.dark_purple(),
        )
        
        await ctx.send(embed=embed, view=OpenTicket())
        
    @discord.slash_command()
    async def close_ticket(self, ctx: discord.ApplicationContext):
        
        client = MongoClient("mongodb://localhost:27017/")
        ticketdb = client["DiscordBotDB"]
        collection = ticketdb["TicketCollection"]
        
        if collection.find_one({"ticket_name": f"{ctx.channel}"}):
            embed = discord.Embed(
                    title="Close Ticket",
                    description="Are you really sure u want to close the ticket?",
                    color=discord.Colour.dark_purple(),
                )
            
            await ctx.respond(embed=embed, view=CloseTicket())
        else:
            await ctx.respond("This is not a ticket", ephemeral=True)

def setup(bot):
    bot.add_cog(ticket(bot))