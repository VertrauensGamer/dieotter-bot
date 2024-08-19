import discord
from discord.ext import commands

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @discord.slash_command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = None):
        await member.kick(reason=reason)
        await ctx.respond(f"User {member} has been kicked for {reason}")
        
    @discord.slash_command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = None):
        await member.ban(reason=reason)
        await ctx.respond(f"User{member} has been banned for {reason}")
        
    @discord.slash_command()
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx: discord.ApplicationContext, member: discord.Member, reason: str = None):
        mute_role = discord.utils.get(ctx.guild.roles, name="muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=False, send_messages=False)
                await member.add_roles(mute_role, reason=reason)
                await ctx.respond(f"User {member} has been muted for {reason}")
        else:
            await member.add_roles(mute_role, reason=reason)
            await ctx.respond(f"User {member} has been muted for {reason}")
            
    @discord.slash_command()
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx: discord.ApplicationContext, member: discord.Member):
        mute_role = discord.utils.get(ctx.guild.roles, name="muted")
        await member.remove_roles(mute_role)
        await ctx.respond(f"User {member} has been unmuted.")
        
def setup(bot):
    bot.add_cog(moderation(bot))