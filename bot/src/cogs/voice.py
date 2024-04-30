import discord
from discord import app_commands
from discord.ext import commands
from lib import voicevox

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
            
async def setup(bot: commands.Bot):
    await bot.add_cog(Voice(bot))