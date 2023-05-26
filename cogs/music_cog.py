import asyncio
import os
import discord
from discord import Embed
from discord.ext import commands
from collections import deque
from pathlib import Path
from cogs.audio import Cancion


ruta_canciones = Path(os.getenv("RUTA_CANCIONES"))


class MusicCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lista_reproduccion = deque()
        self.reproduciendo = False

    def agregar_a_lista_reproduccion(self, cancion):
        self.lista_reproduccion.append(cancion)

    async def reproducir_siguiente_cancion(self, ctx):
        cliente_voz = ctx.guild.voice_client

        if cliente_voz and not cliente_voz.is_playing():
            if len(self.lista_reproduccion) > 0:
                self.reproduciendo = True

                siguiente_cancion = self.lista_reproduccion.popleft()

                # Reproduce la siguiente canción
                cliente_voz.play(
                    discord.FFmpegPCMAudio(str(siguiente_cancion.ruta)),
                    after=lambda e: asyncio.run_coroutine_threadsafe(
                        self.reproducir_siguiente_cancion(ctx), self.bot.loop
                    ),
                )

                embed = Embed(title=siguiente_cancion.titulo, color=0x00FF00)
                embed.set_author(name="🎶 Reproduciendo")
                embed.set_thumbnail(url=siguiente_cancion.imagen)
                embed.add_field(
                    name="Artista", value=siguiente_cancion.artista, inline=False
                )
                embed.add_field(
                    name="Duración", value=siguiente_cancion.duracion, inline=False
                )
                embed.set_footer(text=f"Pedido por {ctx.author}")
                await ctx.reply(embed=embed)

            else:
                await ctx.reply("No hay más canciones en la lista de reproducción")
                self.reproduciendo = False
        else:
            await ctx.reply("No hay más canciones en la lista de reproducción")

    @commands.hybrid_command(
        name="reproducir",
        with_app_command=True,
        description="Para reproducir una canción",
    )
    async def reproducir_cancion(self, ctx, nombre_cancion: str):
        # Verifica si el usuario está en un canal de voz
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("Debes estar en un canal de voz para usar este comando.")
            return

        # Obtiene el canal de voz y el cliente de voz
        canal_voz = ctx.author.voice.channel
        cliente_voz = ctx.guild.voice_client

        # Si no hay un cliente de voz, se conecta al canal de voz
        if not cliente_voz:
            cliente_voz = await canal_voz.connect()

        # Verifica si ya se está reproduciendo audio
        if cliente_voz.is_playing():
            # Si se está reproduciendo, se agrega la canción a la lista de reproducción
            # y se muestra un mensaje
            cancion_nueva = Cancion.from_nombre_cancion(nombre_cancion, ruta_canciones)

            if cancion_nueva is None:
                await ctx.reply(f"No se encontró la canción: {nombre_cancion}")
                return

            self.lista_reproduccion.append(cancion_nueva)

            embed = Embed(title=cancion_nueva.titulo, color=0x00FF00)
            embed.set_author(name="🎶 Agregado a la lista")
            embed.set_thumbnail(url=cancion_nueva.imagen)
            embed.add_field(name="Artista", value=cancion_nueva.artista, inline=False)
            embed.add_field(name="Duración", value=cancion_nueva.duracion, inline=False)
            embed.set_footer(text=f"Pedido por {ctx.author}")
            await ctx.reply(embed=embed)

            return  # Salir del método para evitar reproducir la canción inmediatamente

        # Crea un objeto Cancion
        cancion = Cancion.from_nombre_cancion(nombre_cancion, ruta_canciones)

        if cancion is None:
            await ctx.reply(
                f"No se pudo obtener la información de la canción: {nombre_cancion}"
            )
            return

        # Reproduce la canción
        self.lista_reproduccion.append(cancion)

        if not self.reproduciendo:
            await self.reproducir_siguiente_cancion(ctx)

        embed = Embed(title=cancion.titulo, color=0x00FF00)
        embed.set_author(name="🎶 Reproduciendo")
        embed.set_thumbnail(url=cancion.imagen)
        embed.add_field(name="Artista", value=cancion.artista, inline=False)
        embed.add_field(name="Duración", value=cancion.duracion, inline=False)
        embed.set_footer(text=f"Pedido por {ctx.author}")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="agregar",
        with_app_command=True,
        description="agrega una cancion a la lista de reproduccion",
    )
    async def agregar(self, ctx, nombre_cancion: str):
        cliente_voz = ctx.guild.voice_client

        cancion_nueva = Cancion.from_nombre_cancion(nombre_cancion, ruta_canciones)
        if cancion_nueva == None:
            await ctx.reply(
                f"No se pudo obtener la información de la canción: {nombre_cancion}"
            )
            return

        await ctx.defer()

        self.lista_reproduccion.append(cancion_nueva)

        print(f"Canción agregada a la lista de reproducción: {cancion_nueva.titulo}")

        print(
            f"Lista de reproducción después de agregar canción: {self.lista_reproduccion}"
        )

        if cliente_voz and not cliente_voz.is_playing():
            await self.reproducir_siguiente_cancion(ctx)

        embed = Embed(title=cancion_nueva.titulo, color=0x00FF00)
        embed.set_author(name="🎶 Agregado a la lista")
        embed.set_thumbnail(url=cancion_nueva.imagen)
        embed.add_field(name="Artista", value=cancion_nueva.artista, inline=False)
        embed.add_field(name="Duración", value=cancion_nueva.duracion, inline=False)
        embed.set_footer(text=f"Agregado por {ctx.author}")
        await ctx.reply(embed=embed)

    @commands.hybrid_command(
        name="pasar",
        with_app_command=True,
        description="Salta a la siguiente canción en la lista de reproducción",
    )
    async def skip_song(self, ctx):
        voice_client = ctx.guild.voice_client

        if voice_client is None or not voice_client.is_playing():
            await ctx.send("No hay ninguna canción reproduciéndose.")
            return

        voice_client.stop()
        await ctx.send("Se ha saltado la canción actual.")

    @commands.hybrid_command(
        name="entra",
        with_app_command=True,
        description="Indica al bot que se una al canal de voz",
    )
    async def join(self, ctx):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.reply("No estás conectado a un canal de voz.")
            return

        voice_channel = self.ctx.user.voice.channel
        voice_client = self.ctx.guild.voice_client

        if voice_client:
            await voice_client.move_to(voice_channel)
            ctx.reply("tamo adentro")
        else:
            voice_client = await voice_channel.connect()
            ctx.reply("tamo adentro")

    @commands.hybrid_command(
        name="pausa", with_app_command=True, description="Este comando pausa la canción"
    )
    async def pause(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await ctx.reply("Canción en pausa.")
        else:
            await ctx.reply("No se está reproduciendo ninguna canción.")

    @commands.hybrid_command(
        name="reanudar", with_app_command=True, description="Reanuda la canción"
    )
    async def resume(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            await ctx.reply("Canción reanudada.")
        else:
            await ctx.reply("No hay canciones en pausa.")

    @commands.hybrid_command(
        name="dejar",
        with_app_command=True,
        description="Para que el bot abandone el canal de voz",
    )
    async def leave(self, ctx):
        voice_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await ctx.reply("Saliendo del canal de voz.")
        else:
            await ctx.reply("No estoy conectado a un canal de voz.")

    @commands.hybrid_command(
        name="lista",
        with_app_command=True,
        description="Muestra la lista de reproducción actual",
    )
    async def mostrar_lista(self, ctx):
        # Verifica si hay canciones en la lista de reproducción
        if not self.lista_reproduccion:
            await ctx.reply("La lista de reproducción está vacía.")
            return

        embed = Embed(title="Lista de Reproducción", color=0x00FF00)
        embed.set_author(name="🎶 Canciones en la lista de reproducción")

        # Recorre la lista de reproducción y agrega cada canción al embed
        for index, cancion in enumerate(self.lista_reproduccion, start=1):
            titulo = cancion.titulo
            artista = cancion.artista
            duracion = cancion.duracion

            embed.add_field(
                name=f"{index}. {titulo}",
                value=f"Artista: {artista} | Duración: {duracion}",
                inline=False,
            )

        await ctx.reply(embed=embed)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user and after.channel is None:
            self.lista_reproduccion.clear()
            if self.bot.voice_clients:
                await self.bot.voice_clients[0].disconnect()

    async def cog_before_invoke(self, ctx):
        await self.bot.wait_until_ready()

        # Verificar si el autor del comando está en un canal de voz
        if ctx.author.voice is None:
            await ctx.reply("Debes estar en un canal de voz para usar este comando.")
            raise commands.CommandError("Autor del comando no está en un canal de voz.")

        # Verificar si el bot ya está en un canal de voz
        if ctx.guild.voice_client is not None:
            # Verificar si el bot y el autor del comando están en el mismo canal de voz
            if ctx.guild.voice_client.channel != ctx.author.voice.channel:
                await ctx.reply("Ya estoy en otro canal de voz.")
                raise commands.CommandError("Bot está en otro canal de voz.")

        # Conectar al canal de voz del autor del comando si no está conectado
        if ctx.guild.voice_client is None:
            await ctx.author.voice.channel.connect()

    async def cog_command_error(self, ctx, error):
        await ctx.reply(str(error))


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
