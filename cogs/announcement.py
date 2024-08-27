import discord
from discord.ext import commands
import datetime

class Announcement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
    
@discord.slash_command()
@commands.has_permissions(administrator=True)
async def announcement(self,
                       ctx: discord.ApplicationContext,
                       title: discord.Option(str, "Title of the announcement"), # type: ignore
                       message: discord.Option(str, "Content of the announcement"), # type: ignore
                       color: discord.Option(str, "Embed color (hex code)", required=False, default="7289DA"), # type: ignore
                       image_url: discord.Option(str, "URL of an image to add", required=False), # type: ignore
                       event_date: discord.Option(str, "Date of the Event", required=False) # type: ignore
                       ):
    """
    This function sends an announcement to the Discord channel where the command was invoked.

    Parameters:
    ctx (discord.ApplicationContext): The context of the command invocation.
    title (discord.Option(str)): The title of the announcement.
    message (discord.Option(str)): The content of the announcement.
    color (discord.Option(str), optional): The color of the embed. Defaults to "7289DA".
    image_url (discord.Option(str), optional): The URL of an image to add to the embed. Defaults to None.
    event_date (discord.Option(str), optional): The date of the event. Defaults to None.

    Returns:
    None
    """
    try:
        color = discord.Color(int(color.strip('#'), 16))
    except ValueError:
        color = discord.Color.dark_purple()

    guild_icon_url = ctx.guild.icon.url if ctx.guild.icon else None
    embed = discord.Embed(
        title=f"📢 {title}",
        description=f"{message}",
        color=color,
        timestamp=datetime.datetime.now(datetime.UTC)
    )
    embed.set_author(name=f"Announcement by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    embed.set_footer(text="VertrauensGamer", icon_url=guild_icon_url)

    if image_url:
        embed.set_image(url=image_url)

    # Add some visual separators
    embed.add_field(name="\u200b", value="─" * 20, inline=False)

    if event_date:
        embed.add_field(name="📅 Event Date", value=f"{event_date}", inline=True)

    # You can add more fields here if needed, for example:
    # embed.add_field(name="📍 Location", value="Discord", inline=True)

    await ctx.respond(embed=embed)
        
def setup(bot):
    bot.add_cog(Announcement(bot))