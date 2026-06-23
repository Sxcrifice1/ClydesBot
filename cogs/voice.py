import discord
from discord.ext import commands
import yt_dlp
import aiohttp
import os
import asyncio
from config import load_json

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()

    @commands.command()

    async def generate_tts(text):
        os.makedirs("avisos_cache", exist_ok=True)
        hash_text = hashlib.md5(text.encode('utf-8')).hexdigest()
        filename = f"avisos_cache/{hash_text}.mp3"
        
        if not os.path.exists(filename):
            voice_id = "4Hhnz0dbjgKk6N8yJFP3" # Custom cloned voice ID
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": os.getenv("ELEVENLABS_API_KEY")
            }
            
            data = {
                "text": text,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.75
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        with open(filename, 'wb') as f:
                            f.write(audio_data)
                    else:
                        error_msg = await response.text()
                        raise Exception(f"ElevenLabs HTTP {response.status}: {error_msg}")
            return filename, True
        
        return filename, False


    async def play_announcement(self, vc, mp3_path):
        # Apply radio effect with FFmpeg (EQ cut + Pink Noise static mixed)
        radio_filter = (
            'anoisesrc=d=60:c=pink:r=44100:a=0.015 [noise]; '
            '[0:a] highpass=f=300,lowpass=f=3000,volume=2.0,aformat=sample_fmts=s16:channel_layouts=mono [voice]; '
            '[voice][noise] amix=inputs=2:duration=first'
        )
        source = discord.FFmpegPCMAudio(mp3_path, options=f'-filter_complex "{radio_filter}"')
        
        # Save current mute states and mute everyone
        previous_mutes = {}
        for member in vc.channel.members:
            if not member.bot:
                previous_mutes[member.id] = member.voice.mute
                try:
                    await member.edit(mute=True)
                except discord.Forbidden:
                    pass # Ignora se o bot não tiver permissão de admin
                    
        vc.play(source)
        while vc.is_playing():
            await asyncio.sleep(1)
            
        # Unmute everyone
        for member in vc.channel.members:
            if not member.bot and member.id in previous_mutes:
                if not previous_mutes[member.id]: # Only unmute if they were not muted before
                    try:
                        await member.edit(mute=False)
                    except discord.Forbidden:
                        pass


    @commands.command()

    @commands.command()



async def setup(bot):
    await bot.add_cog(Voice(bot))
