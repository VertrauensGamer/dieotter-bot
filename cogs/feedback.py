import discord
from discord import Option
from discord.ext import commands
from main import get_feedback_collection

class Feedback(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(
        name="submit_feedback",
        description="Reiche Feedback ein und sende es an den Feedback-Kanal"
    )
    async def submit_feedback(
        self, 
        ctx, 
        message: Option(str, "Dein Feedback-Nachricht", required=True) #type: ignore
    ):
        await ctx.defer(ephemeral=True)
        feedback_channel_id = discord.utils.get(ctx.guild.channels, name="feedback").id

        feedback_collection = get_feedback_collection()
        
        new_feedback = {
            "user_id": ctx.author.id,
            "user_name": ctx.author.name,
            "user_avatar": str(ctx.author.avatar.url) if ctx.author.avatar else None,
            "message": message
        }
        
        result = feedback_collection.insert_one(new_feedback)
        new_feedback['_id'] = result.inserted_id

        # Sende Feedback an den Kanal
        channel = self.bot.get_channel(feedback_channel_id)
        if not channel:
            await ctx.followup.send("Fehler: Feedback-Kanal nicht gefunden. Bitte kontaktiere einen Administrator.", ephemeral=True)
            return

        embed = discord.Embed(
            title="📝 Neues Feedback",
            description=new_feedback['message'],
            color=discord.Color.blue()
        )
        embed.set_author(name=new_feedback['user_name'], icon_url=new_feedback.get('user_avatar'))
        embed.set_footer(text=f"Feedback ID: {new_feedback['_id']}")

        await channel.send(embed=embed)

        # Bestätigung an den Benutzer
        confirmation_embed = discord.Embed(
            title="✅ Feedback eingereicht",
            description="Vielen Dank für dein Feedback! Es wurde erfolgreich an unser Team weitergeleitet.",
            color=discord.Color.green()
        )
        await ctx.followup.send(embed=confirmation_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Feedback(bot))
