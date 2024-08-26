import discord
from discord.ext import commands
import datetime

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(name="serverstats", description="Display server statistics")
    async def server_stats(self, ctx):
        guild = ctx.guild
        total_members = guild.member_count
        online_members = sum(member.status != discord.Status.offline for member in guild.members)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        roles = len(guild.roles)
        emojis = len(guild.emojis)
        boosters = guild.premium_subscription_count

        embed = discord.Embed(
            title=f"{guild.name} Statistics",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(datetime.UTC)
        )
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        
        embed.add_field(name="👥 Total Members", value=total_members, inline=True)
        embed.add_field(name="🟢 Online Members", value=online_members, inline=True)
        embed.add_field(name="💬 Text Channels", value=text_channels, inline=True)
        embed.add_field(name="🔊 Voice Channels", value=voice_channels, inline=True)
        embed.add_field(name="📁 Categories", value=categories, inline=True)
        embed.add_field(name="👑 Roles", value=roles, inline=True)
        embed.add_field(name="😀 Emojis", value=emojis, inline=True)
        embed.add_field(name="🚀 Boosts", value=boosters, inline=True)
        embed.add_field(name="📅 Created On", value=guild.created_at.strftime("%B %d, %Y"), inline=True)

        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)

        await ctx.respond(embed=embed)

    @discord.slash_command(name="membercount", description="Display the current member count")
    async def member_count(self, ctx):
        member_count = ctx.guild.member_count
        embed = discord.Embed(
            title="Member Count",
            description=f"This server has **{member_count}** members.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(datetime.UTC)
        )
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(ServerStats(bot)) 