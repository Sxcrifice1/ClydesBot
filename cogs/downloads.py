import discord
from discord.ext import commands
import librosa
import numpy as np
import yt_dlp
import os
import io

class Downloads(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info_audio(self, ctx):
        if not ctx.message.attachments:
            return await ctx.send("⚠️ Por favor, envie o arquivo de áudio junto com o comando.")
            
        anexo = ctx.message.attachments[0]
        if not anexo.filename.endswith(('.mp3', '.wav', '.ogg')):
            return await ctx.send("❌ Formato não suportado. Envie MP3, WAV ou OGG.")
            
        msg = await ctx.send("⏳ Analisando áudio (BPM, Tom, Duração)...")
        try:
            audio_bytes = await anexo.read()
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None)
            
            # BPM
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
            
            # Tom (Key)
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
            chroma_vals = np.sum(chroma, axis=1)
            notas = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            nota_idx = np.argmax(chroma_vals)
            tom_detectado = notas[nota_idx]
            
            duracao = librosa.get_duration(y=y, sr=sr)
            minutos = int(duracao // 60)
            segundos = int(duracao % 60)
            
            embed = discord.Embed(title="📊 Análise do Áudio", color=0x00ffaa)
            embed.add_field(name="BPM", value=f"**{int(tempo[0]) if isinstance(tempo, np.ndarray) else int(tempo)}**", inline=True)
            embed.add_field(name="Tom Musical (Key)", value=f"**{tom_detectado}**", inline=True)
            embed.add_field(name="Duração", value=f"{minutos}m {segundos}s", inline=True)
            embed.add_field(name="Sample Rate", value=f"{sr} Hz", inline=True)
            
            await msg.edit(content=None, embed=embed)
        except Exception as e:
            await msg.edit(content=f"❌ Erro ao analisar o áudio: {e}")

    @commands.command()
    async def dl_audio(self, ctx, url: str = None):
        if not url:
            return await ctx.send("⚠️ Informe o link do YouTube.")
            
        msg = await ctx.send("⏳ Baixando áudio...")
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'no_warnings': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'cookiefile': 'cookies.txt',  # Se precisar
        }
        
        try:
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                arquivo = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                
            tamanho = os.path.getsize(arquivo) / (1024 * 1024)
            if tamanho > 25:
                os.remove(arquivo)
                return await msg.edit(content="❌ O arquivo gerado é maior que o limite de 25MB do Discord.")
                
            await ctx.send(file=discord.File(arquivo))
            await msg.delete()
            os.remove(arquivo)
            
        except Exception as e:
            await msg.edit(content=f"❌ Erro ao baixar áudio: {e}")

    @commands.command()
    async def dl_video(self, ctx, url: str = None):
        if not url:
            return await ctx.send("⚠️ Informe o link do YouTube.")
            
        msg = await ctx.send("⏳ Baixando vídeo (pode demorar)...")
        
        ydl_opts = {
            'format': 'best[ext=mp4][filesize<25M]/best[filesize<25M]',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True,
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'cookiefile': 'cookies.txt',
        }
        
        try:
            if not os.path.exists('downloads'):
                os.makedirs('downloads')
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                arquivo = ydl.prepare_filename(info)
                
            await ctx.send(file=discord.File(arquivo))
            await msg.delete()
            os.remove(arquivo)
            
        except Exception as e:
            await msg.edit(content="❌ Erro ao baixar vídeo. Pode ser que o arquivo seja maior que 25MB ou não esteja disponível em MP4.")

async def setup(bot):
    await bot.add_cog(Downloads(bot))
