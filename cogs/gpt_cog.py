import discord
import openai
import os
from discord import Embed
from discord.ext import commands


# Configuramos la clave de la API de OpenAI
openai.api_key = os.getenv("APIOPENAI")

class GPTCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(
        name="gpt", with_app_command=True, description="enviar texto a gpt"
    )
    async def responceGPT(self, ctx, mensaje: str):
        # Definimos la pregunta que vamos a hacer a OpenAI
        prompt = mensaje

        await ctx.defer()

        # Creamos una solicitud a OpenAI para completar el prompt
        # Usamos el motor de texto Davinci-003 que es uno de los más avanzados y puede generar textos muy convincentes
        # El parámetro max_tokens limita el tamaño del texto de respuesta
        completion = openai.Completion.create(
            engine="text-davinci-003", prompt=prompt, max_tokens=2048
        )

        # Extraemos el texto de la respuesta
        texto = completion.choices[0].text

        # Convertimos el texto a una cadena de caracteres
        texto = str(texto)
        embed = Embed(title="GPT")
        embed.set_thumbnail(
            url="https://miro.medium.com/v2/resize:fit:640/1*bf37-lAuwi6_Wx5-e5EJ1Q.jpeg"
        )
        embed.add_field(name="Mensaje", value=mensaje, inline=False)
        embed.add_field(name="respuesta", value=texto, inline=False)
        await ctx.reply(embed=embed)
    
    @commands.hybrid_command(
        name="generar_imagen",
        with_app_command=True,
        description="generar imagen con DALL·E"
    )
    async def gpt_image(self, ctx, texto:str):
        await ctx.defer()
        response = openai.Image.create(
            prompt= texto,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
        embed = Embed(title="DALL·E")
        embed.add_field(name="Prompt: ", value=texto, inline=False)
        embed.set_image(url=image_url)
        await ctx.reply(embed=embed)





async def setup(bot):
    await bot.add_cog(GPTCog(bot))
