import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from cogs.music_cog import MusicCog
from cogs.gpt_cog import GPTCog
from cogs.youtube_cog import YoutubeCog


load_dotenv()
DISCORD_TOKEN = os.getenv("TOKEN")

intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Conectado como {bot.user.name}")
    await bot.change_presence(
        status=discord.Status.online, activity=discord.Game(name="/command")
    )

    await bot.add_cog(MusicCog(bot))
    await bot.add_cog(GPTCog(bot))

    try:
        synce = await bot.tree.sync()
        print(f"Sync {len(synce)} command(s)")
    except Exception as e:
        print(e)


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)
