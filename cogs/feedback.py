import discord
from discord import Option
from discord.ext import commands
from main import get_feedback_collection
import uuid

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
        message: Option(str, "Deine Feedback-Nachricht", required=True)
    ):
        await ctx.defer(ephemeral=True)
        
        feedback_channel = self.get_feedback_channel(ctx.guild)
        if not feedback_channel:
            await self.send_error_message(ctx)
            return

        feedback_data = self.create_feedback_data(ctx.author, message)
        self.save_feedback_to_database(feedback_data)

        await self.send_feedback_to_channel(feedback_channel, feedback_data)
        await self.send_confirmation_to_user(ctx)

    def get_feedback_channel(self, guild):
        return discord.utils.get(guild.channels, name="feedback")

    async def send_error_message(self, ctx):
        await ctx.followup.send("Fehler: Feedback-Kanal nicht gefunden. Bitte kontaktiere einen Administrator.", ephemeral=True)

    def create_feedback_data(self, author, message):
        return {
            "user_id": author.id,
            "user_name": author.name,
            "message": message,
            "feedbackId": str(uuid.uuid4())
        }

    def save_feedback_to_database(self, feedback_data):
        feedback_collection = get_feedback_collection()
        result = feedback_collection.insert_one(feedback_data)
        feedback_data['_id'] = result.inserted_id

    async def send_feedback_to_channel(self, channel, feedback_data):
        embed = self.create_feedback_embed(feedback_data)
        await channel.send(embed=embed)

    def create_feedback_embed(self, feedback_data):
        embed = discord.Embed(
            title="📝 Neues Feedback",
            description=feedback_data['message'],
            color=discord.Color.blue()
        )
        embed.set_author(name=feedback_data['user_name'], icon_url=feedback_data.get('user_avatar'))
        embed.set_footer(text=f"Feedback ID: {feedback_data['_id']}")
        return embed

    async def send_confirmation_to_user(self, ctx):
        confirmation_embed = discord.Embed(
            title="✅ Feedback eingereicht",
            description="Vielen Dank für dein Feedback! Es wurde erfolgreich an unser Team weitergeleitet.",
            color=discord.Color.green()
        )
        await ctx.followup.send(embed=confirmation_embed, ephemeral=True)

def setup(bot):
    bot.add_cog(Feedback(bot))