import discord
from discord import app_commands
from discord.ext import commands
SERVER_ID = 1106924995118108723

class Xxx(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Successfully loaded : PostForum')
        await self.bot.tree.sync(guild=discord.Object(SERVER_ID))
        print("sync")

    @app_commands.command(name = "bottest", description = "テスト")
    @app_commands.guilds(SERVER_ID)
    @app_commands.checks.has_permissions(administrator=True)
    async def bottest(self, interaction: discord.Interaction):
        await interaction.response.send_message("test", ephemeral=True)
            
async def setup(bot: commands.Bot):
    await bot.add_cog(Xxx(bot))