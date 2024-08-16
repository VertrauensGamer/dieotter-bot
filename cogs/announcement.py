import discord
from discord.ext import commands

class announcement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__
    
    @discord.slash_command()
    async def announcement(self,
                           ctx: discord.ApplicationContext,
                           title: discord.Option(str, "Title of the announcement"),
                           message: discord.Option(str, "Content of the announcement"),
                           ):
        embed = discord.Embed(
            title=f"{title}",
            description=f"{message}",
            color=discord.Color.dark_purple()
        )
        embed.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.display_avatar.url}")
        embed.set_footer(text="VertrauensGamer", icon_url="https://cdn.discordapp.com/avatars/466537555798654987/3d3a360eb92b3fccd9e4e7ddea831703.webp?size=80")
        await ctx.respond(embed=embed)
        
def setup(bot):
    bot.add_cog(announcement(bot))
         