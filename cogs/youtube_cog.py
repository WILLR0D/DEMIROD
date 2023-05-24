import discord
import asyncio
from discord.ext import commands
from cogs.audio import LocalAudioSource, Cancion
from cogs.music_cog import MusicCog
from cogs import music_cog


class YoutubeCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="youtube",
        with_app_command=True,
        description="Para buscar y reproducir una canción desde una URL de YouTube",
    )
    async def buscar_cancion(self, ctx, url: str):
        if ctx.author.voice is None:
            await ctx.reply(
                "Debes estar en un canal de voz para utilizar este comando."
            )
            return

        await ctx.defer()

        voice_channel = ctx.author.voice.channel
        voice_client = ctx.guild.voice_client or await voice_channel.connect()

        music_cog = self.bot.get_cog("MusicCog")
        if music_cog is None:
            await ctx.reply("No se encontró el módulo de música.")
            return

        if voice_client.is_playing():
            cancion_nueva = LocalAudioSource.from_url(url)

            if cancion_nueva == None:
                await ctx.reply(f"No se encontró el link: {url}")
                return

            music_cog.agregar_a_lista_reproduccion(cancion_nueva)

            embed = discord.Embed(title=cancion_nueva.titulo)
            embed.set_author(name="🎶 Agregado a la lista")
            embed.add_field(name="Artista", value=cancion_nueva.artista, inline=False)
            embed.add_field(name="Duración", value=cancion_nueva.duracion, inline=False)
            embed.set_thumbnail(url=cancion_nueva.imagen)
            embed.set_footer(text=f"Pedido por {ctx.author}")
            await ctx.reply(embed=embed)

        else:
            cancion = LocalAudioSource.from_url(url)

            embed = discord.Embed(title=cancion.titulo)
            embed.set_author(name="🎶 Reproduciendo")
            embed.add_field(name="Artista", value=cancion.artista, inline=False)
            embed.add_field(name="Duración", value=cancion.duracion, inline=False)
            embed.set_thumbnail(url=cancion.imagen)
            embed.set_footer(text=f"Pedido por {ctx.author}")
            await ctx.reply(embed=embed)

            music_cog.agregar_a_lista_reproduccion(cancion)

            await music_cog.reproducir_siguiente_cancion(ctx)


async def setup(bot):
    await bot.add_cog(YoutubeCog(bot))
