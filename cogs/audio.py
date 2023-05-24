import os
import asyncio
import difflib
import re
import discord
from pytube import YouTube
from mutagen import File
from pydub import AudioSegment
from pathlib import Path
from dotenv import load_dotenv
import uuid
import requests
from bs4 import BeautifulSoup

load_dotenv()
ruta_canciones = Path(os.getenv("RUTA_CANCIONES"))

CARPETA_CACHE = "audio_temp"


class LocalAudioSource(discord.PCMVolumeTransformer):
    def __init__(self, source, data, volumen=0.5):
        super().__init__(source, volumen)
        self.data = data
        self.titulo = data.get("titulo")  # El título del audio
        self.url = ""

    @classmethod
    async def from_file(cls, ruta_archivo, *, loop=None):
        loop = loop or asyncio.get_event_loop()

        # Obtiene la extensión del archivo
        extension = os.path.splitext(ruta_archivo)[1].lower()

        try:
            if extension == ".flac":
                # Si la extensión es .flac, carga el archivo utilizando la biblioteca pydub con el formato adecuado
                cancion = AudioSegment.from_file(ruta_archivo, format="flac")
            elif extension == ".mp3":
                # Si la extensión es .mp3, carga el archivo utilizando la biblioteca pydub con el formato adecuado
                cancion = AudioSegment.from_file(ruta_archivo)
            else:
                raise ValueError(f"Formato de archivo no soportado: {extension}")

            # Obtiene el nombre del archivo sin la extensión y lo convierte en .mp3
            nombre_archivo = (
                f"{os.path.splitext(os.path.basename(ruta_archivo))[0]}.mp3"
            )

            # Ruta del archivo exportado en la carpeta de caché
            ruta_archivo_cache = Path(CARPETA_CACHE) / nombre_archivo

            # Si el archivo no está en la caché, lo exporta
            if not ruta_archivo_cache.is_file():
                os.makedirs(CARPETA_CACHE, exist_ok=True)
                cancion.export(str(ruta_archivo_cache), format="mp3")

            # Crea una instancia de la clase LocalAudioSource con el audio exportado y los datos proporcionados
            return cls(
                discord.FFmpegPCMAudio(source=str(ruta_archivo_cache)),
                data={"titulo": nombre_archivo},
            )

        except Exception:
            raise ValueError(
                f"No se pudo decodificar el archivo de audio: {ruta_archivo}"
            )

    @staticmethod
    def from_url(url):
        youtube_regex = (
            r"(https?://)?(www\.)?"
            r"(youtube|youtu|youtube-nocookie|music.youtube)\.(com|be)/"
            r"(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})"
        )
        match = re.match(youtube_regex, url)
        if match is None:
            return None

        new_url = url.split("list=")[0] if "list=" in url else url.split("t=")[0]
        url_yt = YouTube(new_url)
        audio = url_yt.streams.get_audio_only()
        os.makedirs("audio_temp", exist_ok=True)
        temp_filename = f"{uuid.uuid4()}.mp3"
        output_file = audio.download(
            output_path="audio_temp", filename=temp_filename, timeout=80
        )
        new_file = os.path.join("audio_temp", temp_filename)

        audio_duration = LocalAudioSource.get_audio_duration(new_file)

        return Cancion(
            url_yt.title, url_yt.thumbnail_url, audio_duration, url_yt.author, new_file
        )

    @staticmethod
    def get_audio_duration(file_path):
        audio = AudioSegment.from_file(file_path)
        duration = audio.duration_seconds
        duracionmin = Cancion.convertir_a_minutos(duration)
        return duracionmin


class Cancion:
    def __init__(self, titulo, imagen, duracion, artista, ruta):
        self.titulo = titulo
        self.imagen = imagen
        self.duracion = duracion
        self.artista = artista
        self.ruta = ruta

    def __str__(self):
        return f"{self.titulo} - {self.artista}"

    def __repr__(self) -> str:
        return self.__str__()

    @classmethod
    def from_nombre_cancion(cls, nombre_cancion, ruta_canciones):
        archivos_canciones = list(ruta_canciones.glob("*.flac")) + list(
            ruta_canciones.glob("*.mp3")
        )
        coincidencias = difflib.get_close_matches(
            nombre_cancion, [archivo.stem for archivo in archivos_canciones], n=1
        )

        if not coincidencias:
            return None

        nombre_cancion_similar = coincidencias[0]
        archivo_cancion = next(
            (
                archivo
                for archivo in archivos_canciones
                if archivo.stem == nombre_cancion_similar
            ),
            None,
        )

        if archivo_cancion is None:
            return None

        audio = File(str(archivo_cancion))

        titulo_cancion = nombre_cancion_similar

        artista = None
        if "artist" in audio:
            artista = audio["artist"][0]
        elif "TPE1" in audio:
            artista = audio["TPE1"].text[0]
        elif "TPE2" in audio:
            artista = audio["TPE2"].text[0]
        else:
            artista = "Desconocido"

        imagen = cls.buscar_cover(titulo_cancion, artista)
        duracion_segundos = audio.info.length
        duracion_formateada = cls.convertir_a_minutos(duracion_segundos)

        return cls(
            titulo_cancion, imagen, duracion_formateada, artista, archivo_cancion
        )

    @staticmethod
    def convertir_a_minutos(segundos):
        minutos = int(segundos // 60)
        segundos_restantes = int(segundos % 60)
        return f"{minutos}:{segundos_restantes:02}"

    @staticmethod
    def buscar_cover(cancion, artista):
        search_query = f"{cancion} {artista} album cover"
        url = f"https://www.bing.com/images/search?q={search_query}&qft=+filterui:imagesize-large"

        try:
            response = requests.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")
            images = soup.select("img")

            for image in images:
                if "cover" in image.get("alt", "").lower():
                    cover_url = image.get("src")
                    return cover_url

        except requests.exceptions.RequestException as e:
            print("Error en la solicitud:", str(e))

        return None
