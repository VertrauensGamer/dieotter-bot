import discord
from discord.ext import commands

class help(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @discord.slash_command()
    async def help(self, ctx):
    
    
        embed = discord.Embed(
            title="Help 1(Currently only Page)",
            description="This Embed gives u information about all the commands of the bot!",
            color=discord.Colour.dark_purple(),
        )
        embed.add_field(name="/hallo", value="/hallo is a test command! Feel free to use it(It just gives u the respond hallo!)",inline=True)
        embed.add_field(name="/help", value="/help is this command you are looking at right now! It gives you information about all commands of this bot!", inline=True)
        embed.add_field(name="/ticket_message [Administrative]", value="/ticket_message creates a Ticket create message", inline=True)
        embed.add_field(name="/close_ticket [Administrative]", value="Closes and automatically archives a ticket into a new category", inline=True)
        embed.set_footer(text="VertrauensGamer", icon_url="https://cdn.discordapp.com/avatars/466537555798654987/3d3a360eb92b3fccd9e4e7ddea831703.webp?size=80")
        embed.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.display_avatar.url}")
        
        await ctx.respond(embed=embed, view = discord.ui.View(discord.ui.Button(label="Github", style=discord.ButtonStyle.url, url="https://github.com/VertrauensGamer")))
        
def setup(bot):
    bot.add_cog(help(bot))