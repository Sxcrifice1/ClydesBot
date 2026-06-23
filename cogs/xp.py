import discord
from discord.ext import commands
from datetime import datetime, timezone, timedelta
import random

from config import XP_FILE, load_json, save_json

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith("!"):
            return

        agora = datetime.now(timezone.utc)
        user_id = str(message.author.id)
        xp_data = load_json(XP_FILE)
        
        if user_id not in xp_data:
            xp_data[user_id] = {"xp": 0, "level": 0, "last_xp": ""}
        
        last_xp_str = xp_data[user_id].get("last_xp", "")
        cooldown_ok = True
        if last_xp_str:
            try:
                last_xp_time = datetime.fromisoformat(last_xp_str)
                if (agora - last_xp_time).total_seconds() < 60:
                    cooldown_ok = False
            except:
                pass
        
        if cooldown_ok:
            ganho = random.randint(15, 25)
            xp_data[user_id]["xp"] += ganho
            xp_data[user_id]["last_xp"] = agora.isoformat()
            
            xp_atual = xp_data[user_id]["xp"]
            nivel_atual = xp_data[user_id]["level"]
            xp_proximo = 5 * (nivel_atual ** 2) + 50 * nivel_atual + 100
            
            if xp_atual >= xp_proximo:
                xp_data[user_id]["level"] += 1
                xp_data[user_id]["xp"] -= xp_proximo
                novo_nivel = xp_data[user_id]["level"]
                
                embed_lvl = discord.Embed(
                    title="🎉 Level Up!",
                    description=f"{message.author.mention} subiu para o **Nível {novo_nivel}**!",
                    color=0x00ffaa
                )
                await message.channel.send(embed=embed_lvl, delete_after=10)
                
                cargo_por_nivel = {5: "Ativo", 10: "Veterano", 20: "Lenda"}
                if novo_nivel in cargo_por_nivel:
                    nome_cargo = cargo_por_nivel[novo_nivel]
                    cargo = discord.utils.get(message.guild.roles, name=nome_cargo)
                    if not cargo:
                        try:
                            cargo = await message.guild.create_role(name=nome_cargo, reason=f"XP: Cargo nível {novo_nivel}")
                        except: pass
                    if cargo:
                        try:
                            await message.author.add_roles(cargo)
                        except: pass
            
            save_json(XP_FILE, xp_data)

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        xp_data = load_json(XP_FILE)
        user_id = str(member.id)
        
        if user_id not in xp_data:
            return await ctx.send(f"{member.mention} ainda não tem XP registrado.")
        
        dados = xp_data[user_id]
        nivel = dados["level"]
        xp = dados["xp"]
        xp_proximo = 5 * (nivel ** 2) + 50 * nivel + 100
        
        ranking = sorted(xp_data.items(), key=lambda x: (x[1].get("level", 0), x[1].get("xp", 0)), reverse=True)
        posicao = next((i + 1 for i, (uid, _) in enumerate(ranking) if uid == user_id), "?")
        
        barra_tam = 20
        preenchido = int((xp / xp_proximo) * barra_tam) if xp_proximo > 0 else 0
        barra = "█" * preenchido + "░" * (barra_tam - preenchido)
        
        embed = discord.Embed(title=f"📊 Rank de {member.name}", color=0x00ffaa)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.add_field(name="Nível", value=f"**{nivel}**", inline=True)
        embed.add_field(name="Posição", value=f"**#{posicao}**", inline=True)
        embed.add_field(name="Progresso", value=f"`{barra}` {xp}/{xp_proximo} XP", inline=False)
        
        cargo_por_nivel = {5: "Ativo", 10: "Veterano", 20: "Lenda"}
        proximo_cargo = None
        for nv, nome in sorted(cargo_por_nivel.items()):
            if nivel < nv:
                proximo_cargo = f"{nome} (Nível {nv})"
                break
        if proximo_cargo:
            embed.add_field(name="Próximo Cargo", value=proximo_cargo, inline=False)
        else:
            embed.add_field(name="Status", value="🏆 Nível máximo de cargos atingido!", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def leaderboard(self, ctx):
        xp_data = load_json(XP_FILE)
        if not xp_data:
            return await ctx.send("📊 Ninguém tem XP ainda.")
        
        ranking = sorted(xp_data.items(), key=lambda x: (x[1].get("level", 0), x[1].get("xp", 0)), reverse=True)[:10]
        
        medalhas = ["🥇", "🥈", "🥉"] + ["🏅"] * 7
        linhas = []
        for i, (uid, dados) in enumerate(ranking):
            membro = ctx.guild.get_member(int(uid))
            nome = membro.name if membro else f"ID: {uid}"
            linhas.append(f"{medalhas[i]} **{nome}** — Nível {dados.get('level', 0)} ({dados.get('xp', 0)} XP)")
        
        embed = discord.Embed(
            title="🏆 Top 10 — Leaderboard",
            description="\n".join(linhas),
            color=0xf1c40f
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(XP(bot))
