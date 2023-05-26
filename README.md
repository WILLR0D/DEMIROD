# DEMIROD

## Descripción

DEMIROD es un bot de Discord multifuncional diseñado para mejorar tu experiencia en los servidores de Discord. Este proyecto alberga el código fuente y la documentación de DEMIROD, el cual cuenta con características como la reproducción de música local en los canales de voz de Discord, así como la capacidad de responder preguntas utilizando el potente modelo de lenguaje ChatGPT.

El bot DEMIROD te permite disfrutar de tus canciones favoritas en Discord. Puedes agregar canciones locales a la lista de reproducción, controlar la reproducción, ajustar el volumen y explorar diferentes opciones de reproducción.

Además, DEMIROD puede responder preguntas utilizando ChatGPT, un modelo de lenguaje de inteligencia artificial. Puedes hacer preguntas en el chat y el bot proporcionará respuestas basadas en su entrenamiento con una amplia gama de datos. También cuenta con la capacidad de generar imágenes utilizando DALL·E, una potente herramienta de creación visual.

## Requisitos previos

* Instala [Python](https://www.python.org/) (versión 3.7 o superior)
* Crea un proyecto en el [Portal de Desarrolladores de Discord](https://discord.com/developers/applications) y obtén un token de bot
* Registra una cuenta en [OpenAI](https://openai.com) y obtén una API key para ChatGPT

## Instalación y configuración

1. Clona este repositorio en tu máquina local.
2. Crea un archivo `.env` en el directorio raíz y configura las variables de entorno necesarias. Incluye el token de tu bot de Discord y la API key de ChatGPT. Puedes seguir el formato del archivo `.env.example` proporcionado.
3. Ejecuta `pip install -r requirements.txt` para instalar las dependencias necesarias.
4. Ejecuta `python demirod.py` para iniciar el bot DEMIROD en tu servidor de Discord.

## Comandos disponibles

* `!agregar <nombre_canción>`: Agrega una canción local a la lista de reproducción.
* `!dejar`: El bot abandona el canal de voz actual.
* `!entra`: Indica al bot que se una al canal de voz.
* `!gpt <Texto>`: Responde lo que envíes utilizando la API de OpenAI.
* `!generar_imagen <texto>`: generar imagen con DALL·E.
* `!lista`: Muestra la lista de reproducción actual.
* `!pasar`: Salta a la siguiente canción en la lista de reproducción.
* `!pausa`: Pausa la canción actual.
* `!reanudar`: Reanuda la canción pausada.
* `!reproducir <nombre_canción>`: Reproduce una canción local.

