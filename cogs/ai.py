import discord
from discord.ext import commands
import aiohttp
import base64
from config import KEYS_FILE, load_json, CANAL_SHOW_EVENTS_ID, MOD_LOG_ID
user_keys = load_json(KEYS_FILE)

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()

    async def send_to_gemini(self, ctx, prompt, attachment=None):
        async def enviar(self, msg):
            if hasattr(ctx, 'send'): await ctx.send(msg)
            else: await ctx.channel.send(msg)

        user_id = str(ctx.author.id)
        if user_id not in user_keys:
            await enviar("⚠️ Cadastre sua API Key do Google primeiro enviando ela aqui.")
            return None
            
        api_key = user_keys[user_id]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        parts = [{"text": prompt}]
        
        if attachment:
            if attachment.size > 5 * 1024 * 1024:
                await enviar("❌ Erro: O arquivo é muito pesado para a IA processar (limite: 5MB). Tente enviar um trecho menor.")
                return None
                
            mime = attachment.content_type
            if not mime:
                await enviar("❌ Não consegui identificar o tipo do arquivo.")
                return None
            try:
                file_bytes = await attachment.read()
                b64_data = base64.b64encode(file_bytes).decode('utf-8')
                parts.append({
                    "inlineData": {
                        "mimeType": mime,
                        "data": b64_data
                    }
                })
            except Exception as e:
                await enviar(f"❌ Erro ao ler arquivo: {e}")
                return None

        payload = {
            "system_instruction": {
                "parts": [{"text": "Você é a IA assistente oficial da comunidade Clydes no Discord. Seja profissional, direto e minimalista."}]
            },
            "contents": [{"parts": parts}]
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['candidates'][0]['content']['parts'][0]['text']
                else:
                    erro_txt = await response.text()
                    print(f"[ERRO GEMINI] {response.status}: {erro_txt}")
                    await enviar(f"❌ Erro na API do Google: {response.status}")
                    return None


    @commands.command()

    @commands.command()

    async def resumo(self, ctx, canal: discord.TextChannel = None, *, periodo=None):
        if ctx.channel.id != MOD_LOG_ID: return
        if not canal: return await ctx.send("⚠️ Use: `!resumo #canal`")
        await ctx.send(f"⏳ Lendo {canal.mention}...")
        mensagens = ""
        try:
            async for msg in canal.history(limit=250):
                if not msg.author.bot: mensagens += f"{msg.author.name}: {msg.content}\n"
        except: return await ctx.send("❌ Sem permissão.")
        if not mensagens: return await ctx.send("Sem mensagens.")
        
        resposta = await send_to_gemini(ctx, f"Faça um resumo direto, em tópicos, das seguintes conversas do canal {canal.name}:\n{mensagens[:15000]}")
        if resposta: await ctx.send(f"📊 **Resumo de {canal.mention}:**\n\n{resposta}")


    @commands.command()

    @commands.command()



async def setup(bot):
    await bot.add_cog(AI(bot))
