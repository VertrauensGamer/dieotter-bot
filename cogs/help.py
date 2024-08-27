import discord
from discord.ext import commands
import datetime

class Help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @discord.slash_command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="📚 Bot Commands Guide",
            description="Welcome to the help section! Here's a comprehensive list of all available commands.",
            color=discord.Colour.dark_purple(),
            timestamp=datetime.datetime.now(datetime.UTC)
        )

        # General Commands
        embed.add_field(name="🔹 General Commands", value="Commands available to all users", inline=False)
        embed.add_field(name="/hallo", value="A test command that responds with 'hallo!'", inline=True)
        embed.add_field(name="/help", value="Displays this help message", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Empty field for alignment

        # Administrative Commands
        embed.add_field(name="🔸 Administrative Commands", value="Commands for server administrators", inline=False)
        embed.add_field(name="/ticket_message", value="Creates a ticket creation message", inline=True)
        embed.add_field(name="/close_ticket", value="Closes and archives a ticket", inline=True)
        embed.add_field(name="/giveaway", value="Starts a giveaway (Options: item, duration)", inline=True)
        embed.add_field(name="/announcement", value="Creates an announcement embed", inline=True)
        embed.add_field(name="/kick", value="Kicks a member from the server", inline=True)
        embed.add_field(name="/ban", value="Bans a member from the server", inline=True)
        embed.add_field(name="/mute", value="Mutes a member", inline=True)
        embed.add_field(name="/unmute", value="Unmutes a member", inline=True)

        # Music Commands (Currently Disabled)
        embed.add_field(name="🎵 Music Commands (Currently Disabled)", value="Commands for playing music", inline=False)
        embed.add_field(name="/play [url]", value="Plays music from the given URL", inline=True)
        embed.add_field(name="/stop", value="Stops playing music", inline=True)
        embed.add_field(name="/disconnect", value="disconnects the bot from the channel", inline=True)
        embed.add_field(name="/pause", value="Pauses the Music", inline=True)
        embed.add_field(name="/resume", value="Resumes the music", inline=True)

        # Footer and Author
        guild_icon_url = ctx.guild.icon.url if ctx.guild.icon else None
        embed.set_footer(text="VertrauensGamer", icon_url=guild_icon_url)
        embed.set_author(name=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        # GitHub Button
        github_button = discord.ui.Button(label="GitHub", style=discord.ButtonStyle.url, url="https://github.com/VertrauensGamer")
        view = discord.ui.View()
        view.add_item(github_button)

        await ctx.respond(embed=embed, view=view)
        
def setup(bot):
    bot.add_cog(Help(bot))