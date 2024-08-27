import discord
from discord.ext import commands
import yt_dlp
import asyncio
import datetime

discord.FFmpegOpusAudio.ffmpeg_executable = 'C:/ffmpeg/bin/ffmpeg.exe'

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.song_queue = {}
        self.FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        self.YDL_OPTIONS = {'format': 'bestaudio/best', 'noplaylist': 'True'}

    def create_embed(self, title, description, color, fields=None, thumbnail=None, footer=None):
        embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.now(datetime.UTC))
        if fields:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        if footer:
            embed.set_footer(text=footer, icon_url=self.bot.user.avatar.url)
        return embed

    @discord.slash_command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            embed = self.create_embed("❌ Fehler", "Du bist in keinem Sprachkanal!", discord.Color.red(), 
                                      footer="Bitte trete einem Sprachkanal bei und versuche es erneut.")
            await ctx.respond(embed=embed)
            return
        
        voice_channel = ctx.author.voice.channel
        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)
        
        embed = self.create_embed("🎵 Verbunden", f"Bot ist dem Kanal **{voice_channel.name}** beigetreten.", discord.Color.green(), 
                                  fields=[("Kanal", voice_channel.name, True), ("Mitglieder", len(voice_channel.members), True)],
                                  footer="Bereit zum Abspielen von Musik!")
        await ctx.respond(embed=embed)

    @discord.slash_command()
    async def disconnect(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            embed = self.create_embed("👋 Auf Wiedersehen", "Bot hat den Sprachkanal verlassen.", discord.Color.blue(), 
                                      footer="Danke fürs Zuhören!")
            await ctx.respond(embed=embed)
        else:
            embed = self.create_embed("❌ Fehler", "Bot ist in keinem Sprachkanal.", discord.Color.red(), 
                                      footer="Verwende !join, um den Bot in einen Kanal zu holen.")
            await ctx.respond(embed=embed)

    @discord.slash_command(name="play", description="Spielt ein YouTube-Video ab")
    async def play(self, ctx, url: discord.Option(str, "Die YouTube-URL des Videos", required=True) #type: ignore
                   ):
        await ctx.defer()

        if not ctx.author.voice:
            await ctx.followup.send("Du musst in einem Sprachkanal sein, um diesen Befehl zu nutzen!")
            return

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        try:
            with yt_dlp.YoutubeDL(self.YDL_OPTIONS) as ydl:
                print(f"Extrahiere Informationen von: {url}")
                info = ydl.extract_info(url, download=False)
                url2 = info['url']
                print(f"Extrahierte URL: {url2}")

            source = await discord.FFmpegOpusAudio.from_probe(url2, **self.FFMPEG_OPTIONS)
            
            ctx.voice_client.stop()
            ctx.voice_client.play(source)
            
            # Erstelle ein Embed
            embed = discord.Embed(title="🎵 Jetzt spielt", description=info['title'], color=discord.Color.green())
            embed.add_field(name="Angefordert von", value=ctx.author.mention, inline=True)
            embed.add_field(name="Dauer", value=self.format_duration(info['duration']), inline=True)
            if 'channel' in info:
                embed.add_field(name="Kanal", value=info['channel'], inline=True)
            if 'view_count' in info:
                embed.add_field(name="Aufrufe", value=f"{info['view_count']:,}", inline=True)
            if 'thumbnail' in info:
                embed.set_thumbnail(url=info['thumbnail'])
            if 'upload_date' in info:
                embed.set_footer(text=f"Veröffentlicht am {info['upload_date']}")
            
            await ctx.followup.send(embed=embed)
            print(f"Wiedergabe von {info['title']} gestartet")
        except Exception as e:
            print(f"Fehler beim Abspielen des YouTube-Videos: {e}")
            error_embed = discord.Embed(title="❌ Fehler", description=f"Es gab einen Fehler beim Abspielen des Videos: {e}", color=discord.Color.red())
            await ctx.followup.send(embed=error_embed)

    def format_duration(self, duration):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @discord.slash_command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            embed = self.create_embed("⏸️ Pausiert", "Die Musikwiedergabe wurde pausiert.", discord.Color.orange(), 
                                      footer="Verwende !resume, um fortzufahren.")
            await ctx.send(embed=embed)
        else:
            embed = self.create_embed("❌ Fehler", "Es wird gerade keine Musik abgespielt.", discord.Color.red(), 
                                      footer="Verwende !play, um Musik abzuspielen.")
            await ctx.send(embed=embed)

    @discord.slash_command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            embed = self.create_embed("▶️ Fortgesetzt", "Die Musikwiedergabe wurde fortgesetzt.", discord.Color.green(), 
                                      footer="Genieße die Musik!")
            await ctx.respond(embed=embed)
        else:
            embed = self.create_embed("❌ Fehler", "Es gibt keine pausierte Musik zum Fortsetzen.", discord.Color.red(), 
                                      footer="Verwende !play, um neue Musik abzuspielen.")
            await ctx.respond(embed=embed)

    @discord.slash_command()
    async def stop(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()
            embed = self.create_embed("⏹️ Gestoppt", "Die Musikwiedergabe wurde gestoppt.", discord.Color.red(), 
                                      footer="Verwende !play, um neue Musik abzuspielen.")
            await ctx.respond(embed=embed)
        else:
            embed = self.create_embed("❌ Fehler", "Es wird gerade keine Musik abgespielt.", discord.Color.red(), 
                                      footer="Verwende !join und !play, um Musik abzuspielen.")
            await ctx.respond(embed=embed)

    def format_duration(self, duration):
        minutes, seconds = divmod(duration, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    @discord.slash_command(name="playurl", description="Spielt Audio von einer direkten URL ab")
    async def playurl(self, ctx, 
                      url: discord.Option(str, "Die direkte URL der Audiodatei", required=True) #type: ignore
                      ):
        await ctx.defer()

        if not ctx.author.voice:
            await ctx.followup.send("Du musst in einem Sprachkanal sein, um diesen Befehl zu nutzen!")
            return

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()
        elif ctx.voice_client.channel != ctx.author.voice.channel:
            await ctx.voice_client.move_to(ctx.author.voice.channel)

        try:
            print(f"Versuche, Audio von URL abzuspielen: {url}")
            source = await discord.FFmpegOpusAudio.from_probe(url, **self.FFMPEG_OPTIONS)
            
            ctx.voice_client.stop()
            ctx.voice_client.play(source)
            
            await ctx.followup.send(f"Spiele jetzt Audio von: {url}")
            print("Audio-Wiedergabe gestartet")
        except Exception as e:
            print(f"Fehler beim Abspielen der Audio: {e}")
            await ctx.followup.send(f"Es gab einen Fehler beim Abspielen der Audio: {e}")

def setup(bot):
    bot.add_cog(Music(bot))