import discord
from discord.ext import commands

class oil(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        
    @discord.slash_command()
    async def oilup(self, ctx: discord.ApplicationContext):
        await ctx.respond("Lass mich deinen Astralkörper sanft aber doch bestimmt nach allen Regeln der verführerischen Kunst einölen")
        
def setup(bot):
    bot.add_cog(oil(bot))
        