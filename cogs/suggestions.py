import discord
from discord.ext import commands
from datetime import datetime as dt
class suggestions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 589714893503070219 and not message.author.bot:
            await message.delete()
            m = await message.channel.send(embed=discord.Embed(title=message.content, timestamp = dt.utcnow(), colour=discord.Colour.green()).set_footer(text=f"Sent by {message.author}"))
            await m.add_reaction("👍")
            await m.add_reaction("👎")

def setup(bot):
    bot.add_cog(suggestions(bot))