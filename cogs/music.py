import discord
from discord.ext import commands
import yt_dlp as youtube_dl

youtube_dl.utils.bug_reports_message = lambda: ""

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        
    @discord.slash_command()
    async def play(self, ctx: discord.ApplicationContext, url: discord.Option(str, "Enter URL to play")): # type: ignore
        voice_channel = ctx.author.voice.channel
        if not voice_channel: 
            await ctx.respond("You need to be in a Voice Channel to play music", ephemeral=True)
            return
        
        voice_client = await voice_channel.connect()
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            try: 
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                await ctx.respond(f"An error occurred: {str(e)}")
                return
            ur12 = info['formats'][0]['url']
            voice_client.play(discord.FFmpegPCMAudio(ur12))
            
        await ctx.respond(f"Now playing: {info["title"]}")
        

    @discord.slash_command()
    async def stop(self, ctx: discord.ApplicationContext):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await ctx.respond("Music stopped.")
        if voice_client:
            await voice_client.disconnect()
            
def setup(bot):
    bot.add_cog(music(bot))