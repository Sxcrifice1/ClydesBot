import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone, timedelta
import random

from config import SUGESTAO_FILE, load_json, save_json, COMMUNITY_CATEGORY_ID

class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_giveaways = {}

    @commands.command()
    async def sugestao(self, ctx, *, texto: str = None):
        if not texto:
            return await ctx.send("⚠️ Use: `!sugestao <sua sugestão aqui>`")
        
        canal_sugestoes = discord.utils.get(ctx.guild.text_channels, name="sugestões")
        if not canal_sugestoes:
            category = discord.utils.get(ctx.guild.categories, id=COMMUNITY_CATEGORY_ID)
            canal_sugestoes = await ctx.guild.create_text_channel("sugestões", category=category)
        
        counter_data = load_json(SUGESTAO_FILE)
        num = counter_data.get("counter", 0) + 1
        counter_data["counter"] = num
        save_json(SUGESTAO_FILE, counter_data)
        
        embed = discord.Embed(
            title=f"💡 Sugestão #{num:03d}",
            description=texto,
            color=0x3498db,
            timestamp=discord.utils.utcnow()
        )
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url if ctx.author.avatar else None)
        embed.set_footer(text="Reaja para votar!")
        
        msg = await canal_sugestoes.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        await ctx.send(f"✅ Sua sugestão **#{num:03d}** foi enviada para {canal_sugestoes.mention}!")

    @commands.command()
    async def poll(self, ctx, *, conteudo: str = None):
        if not conteudo:
            return await ctx.send("⚠️ Use: `!poll <pergunta>` ou `!poll pergunta | opção1 | opção2 | opção3`")
        
        partes = [p.strip() for p in conteudo.split("|")]
        
        if len(partes) == 1:
            embed = discord.Embed(
                title="📊 Enquete",
                description=partes[0],
                color=0x9b59b6
            )
            embed.set_footer(text=f"Criada por {ctx.author.name}")
            msg = await ctx.send(embed=embed)
            await msg.add_reaction("👍")
            await msg.add_reaction("👎")
        else:
            pergunta = partes[0]
            opcoes = partes[1:10]
            emojis_num = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
            
            desc = "\n\n".join([f"{emojis_num[i]} {opcao}" for i, opcao in enumerate(opcoes)])
            
            embed = discord.Embed(
                title=f"📊 {pergunta}",
                description=desc,
                color=0x9b59b6
            )
            embed.set_footer(text=f"Criada por {ctx.author.name} • Reaja para votar!")
            msg = await ctx.send(embed=embed)
            for i in range(len(opcoes)):
                await msg.add_reaction(emojis_num[i])

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def sorteio(self, ctx, tempo: str = None, *, premio: str = None):
        if not tempo or not premio:
            return await ctx.send("⚠️ Use: `!sorteio <tempo> <prêmio>`\nExemplo: `!sorteio 1h Nitro`")
        
        unidade = tempo[-1].lower()
        try:
            valor = int(tempo[:-1])
        except ValueError:
            return await ctx.send("⚠️ Formato de tempo inválido. Use: `30m`, `1h`, `1d`")
        
        if unidade == 'm':
            segundos = valor * 60
            tempo_str = f"{valor} minuto(s)"
        elif unidade == 'h':
            segundos = valor * 3600
            tempo_str = f"{valor} hora(s)"
        elif unidade == 'd':
            segundos = valor * 86400
            tempo_str = f"{valor} dia(s)"
        else:
            return await ctx.send("⚠️ Use `m`, `h` ou `d`.")
        
        fim = datetime.now(timezone.utc) + timedelta(seconds=segundos)
        
        embed = discord.Embed(
            title="🎉 SORTEIO!",
            description=(
                f"**Prêmio:** {premio}\n"
                f"**Duração:** {tempo_str}\n"
                f"**Criado por:** {ctx.author.mention}\n\n"
                "Reaja com 🎉 para participar!"
            ),
            color=0xff0000,
            timestamp=fim
        )
        embed.set_footer(text="Encerra em")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("🎉")
        
        self.active_giveaways[msg.id] = {"channel_id": ctx.channel.id, "premio": premio}
        
        await asyncio.sleep(segundos)
        
        try:
            msg = await ctx.channel.fetch_message(msg.id)
        except:
            return
        
        reacao = discord.utils.get(msg.reactions, emoji="🎉")
        if reacao:
            users = [u async for u in reacao.users() if not u.bot]
            if users:
                ganhador = random.choice(users)
                embed_win = discord.Embed(
                    title="🎊 Sorteio Encerrado!",
                    description=f"**Prêmio:** {premio}\n**Ganhador:** {ganhador.mention}\n\nParabéns! 🥳",
                    color=0x00ff00
                )
                await ctx.send(embed=embed_win)
            else:
                await ctx.send("😢 Ninguém participou do sorteio.")
        
        if msg.id in self.active_giveaways:
            del self.active_giveaways[msg.id]

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def reroll(self, ctx):
        async for message in ctx.channel.history(limit=50):
            if message.author == self.bot.user and message.embeds:
                embed = message.embeds[0]
                if embed.title and "SORTEIO" in embed.title:
                    reacao = discord.utils.get(message.reactions, emoji="🎉")
                    if reacao:
                        users = [u async for u in reacao.users() if not u.bot]
                        if users:
                            ganhador = random.choice(users)
                            await ctx.send(f"🎊 **Re-roll!** Novo ganhador: {ganhador.mention}! Parabéns! 🥳")
                            return
                    await ctx.send("😢 Ninguém participou do sorteio para re-sortear.")
                    return
        await ctx.send("⚠️ Não encontrei nenhum sorteio recente neste canal.")

async def setup(bot):
    await bot.add_cog(Community(bot))
