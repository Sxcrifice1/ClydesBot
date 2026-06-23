import discord
from discord.ext import commands
from datetime import timedelta, datetime
import json

from config import WARNS_FILE, load_json, save_json, MOD_LOG_ID

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warns_data = load_json(WARNS_FILE)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ban(self, ctx, member: discord.Member = None, *, motivo="Sem motivo informado"):
        if not member:
            return await ctx.send("⚠️ Use: `!ban @usuario <motivo>`")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Você não pode banir alguém com cargo igual ou superior ao seu.")
        await member.ban(reason=motivo)
        embed = discord.Embed(title="🔨 Membro Banido", color=0xe74c3c)
        embed.add_field(name="Usuário", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def kick(self, ctx, member: discord.Member = None, *, motivo="Sem motivo informado"):
        if not member:
            return await ctx.send("⚠️ Use: `!kick @usuario <motivo>`")
        if member.top_role >= ctx.author.top_role:
            return await ctx.send("❌ Você não pode expulsar alguém com cargo igual ou superior ao seu.")
        await member.kick(reason=motivo)
        embed = discord.Embed(title="👢 Membro Expulso", color=0xe67e22)
        embed.add_field(name="Usuário", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=True)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx, member: discord.Member = None, tempo: str = None, *, motivo="Sem motivo informado"):
        if not member or not tempo:
            return await ctx.send("⚠️ Use: `!mute @usuario <tempo> <motivo>`\nExemplos de tempo: `10m`, `1h`, `1d`")
        
        unidade = tempo[-1].lower()
        try:
            valor = int(tempo[:-1])
        except ValueError:
            return await ctx.send("⚠️ Formato de tempo inválido. Use: `10m`, `1h`, `1d`")
        
        if unidade == 'm':
            delta = timedelta(minutes=valor)
            tempo_str = f"{valor} minuto(s)"
        elif unidade == 'h':
            delta = timedelta(hours=valor)
            tempo_str = f"{valor} hora(s)"
        elif unidade == 'd':
            delta = timedelta(days=valor)
            tempo_str = f"{valor} dia(s)"
        else:
            return await ctx.send("⚠️ Use `m` (minutos), `h` (horas) ou `d` (dias). Ex: `30m`")
        
        await member.timeout(discord.utils.utcnow() + delta, reason=motivo)
        embed = discord.Embed(title="🔇 Membro Mutado", color=0x95a5a6)
        embed.add_field(name="Usuário", value=f"{member.mention}", inline=True)
        embed.add_field(name="Duração", value=tempo_str, inline=True)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("⚠️ Use: `!unmute @usuario`")
        await member.timeout(None)
        await ctx.send(f"🔊 {member.mention} foi desmutado.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member = None, *, motivo="Sem motivo informado"):
        if not member:
            return await ctx.send("⚠️ Use: `!warn @usuario <motivo>`")
        
        user_id = str(member.id)
        if user_id not in self.warns_data:
            self.warns_data[user_id] = []
        
        self.warns_data[user_id].append({
            "motivo": motivo,
            "moderador": str(ctx.author.id),
            "data": datetime.now().strftime("%d/%m/%Y %H:%M")
        })
        save_json(WARNS_FILE, self.warns_data)
        
        total_warns = len(self.warns_data[user_id])
        
        embed = discord.Embed(title="⚠️ Advertência Aplicada", color=0xf1c40f)
        embed.add_field(name="Usuário", value=f"{member.mention}", inline=True)
        embed.add_field(name="Warns", value=f"**{total_warns}/3**", inline=True)
        embed.add_field(name="Moderador", value=ctx.author.mention, inline=True)
        embed.add_field(name="Motivo", value=motivo, inline=False)
        
        if total_warns >= 3:
            embed.add_field(name="🔨 BAN AUTOMÁTICO", value="O usuário atingiu 3 advertências e foi banido.", inline=False)
            embed.color = 0xe74c3c
            await ctx.send(embed=embed)
            await member.ban(reason=f"Ban automático: 3 warns atingidos. Última warn: {motivo}")
            del self.warns_data[user_id]
            save_json(WARNS_FILE, self.warns_data)
        else:
            await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def warns(self, ctx, member: discord.Member = None):
        if not member:
            return await ctx.send("⚠️ Use: `!warns @usuario`")
        
        user_id = str(member.id)
        user_warns = self.warns_data.get(user_id, [])
        
        if not user_warns:
            return await ctx.send(f"✅ {member.mention} não possui nenhuma advertência.")
        
        embed = discord.Embed(title=f"📋 Warns de {member.name}", color=0xf1c40f)
        for i, w in enumerate(user_warns, 1):
            embed.add_field(
                name=f"Warn #{i} — {w['data']}",
                value=f"**Motivo:** {w['motivo']}\n**Mod:** <@{w['moderador']}>",
                inline=False
            )
        embed.set_footer(text=f"Total: {len(user_warns)}/3")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def clear(self, ctx, quantidade: int = None):
        if not quantidade:
            return await ctx.send("⚠️ Use: `!clear <quantidade>`\nExemplo: `!clear 50`")
        if quantidade > 200:
            return await ctx.send("⚠️ Limite de 200 mensagens por vez.")
        deleted = await ctx.channel.purge(limit=quantidade + 1)
        msg = await ctx.send(f"🗑️ **{len(deleted) - 1}** mensagens apagadas.")
        await msg.delete(delay=3)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx):
        overwrites = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrites.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
        await ctx.send("🔒 **LOCKDOWN ATIVADO** — Este canal foi trancado. Apenas administradores podem falar.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def unlock(self, ctx):
        overwrites = ctx.channel.overwrites_for(ctx.guild.default_role)
        overwrites.send_messages = None
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrites)
        await ctx.send("🔓 **LOCKDOWN DESATIVADO** — Canal liberado novamente.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
