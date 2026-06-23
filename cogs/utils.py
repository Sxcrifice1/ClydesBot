import discord
from discord.ext import commands

from config import XP_FILE, load_json

class Utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        
        xp_data = load_json(XP_FILE)
        user_xp = xp_data.get(str(member.id), {"xp": 0, "level": 0})
        
        cargos = [r.mention for r in reversed(member.roles) if r.name != "@everyone"]
        cargos_str = " ".join(cargos[:15]) if cargos else "Nenhum"
        
        embed = discord.Embed(title=f"👤 Informações de {member.name}", color=member.color if member.color != discord.Color.default() else 0x2b2d31)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        
        embed.add_field(name="🏷️ Nome", value=f"{member} ({member.id})", inline=False)
        embed.add_field(name="📅 Conta Criada", value=member.created_at.strftime("%d/%m/%Y às %H:%M"), inline=True)
        embed.add_field(name="📥 Entrou no Servidor", value=member.joined_at.strftime("%d/%m/%Y às %H:%M") if member.joined_at else "Desconhecido", inline=True)
        embed.add_field(name="📊 Nível XP", value=f"Nível **{user_xp['level']}** ({user_xp['xp']} XP)", inline=True)
        embed.add_field(name=f"🎭 Cargos ({len(cargos)})", value=cargos_str, inline=False)
        
        if member.premium_since:
            embed.add_field(name="🚀 Booster desde", value=member.premium_since.strftime("%d/%m/%Y"), inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def serverinfo(self, ctx):
        guild = ctx.guild
        
        total_membros = guild.member_count
        online = sum(1 for m in guild.members if m.status != discord.Status.offline)
        canais_texto = len(guild.text_channels)
        canais_voz = len(guild.voice_channels)
        total_cargos = len(guild.roles) - 1
        boosts = guild.premium_subscription_count
        nivel_boost = guild.premium_tier
        
        embed = discord.Embed(title=f"🏠 {guild.name}", color=0x2b2d31)
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(name="👑 Dono", value=guild.owner.mention if guild.owner else "Desconhecido", inline=True)
        embed.add_field(name="📅 Criado em", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
        embed.add_field(name="🆔 ID", value=guild.id, inline=True)
        
        embed.add_field(name="👥 Membros", value=f"**{total_membros}** total\n**{online}** online", inline=True)
        embed.add_field(name="💬 Canais", value=f"**{canais_texto}** texto\n**{canais_voz}** voz", inline=True)
        embed.add_field(name="🎭 Cargos", value=f"**{total_cargos}**", inline=True)
        
        embed.add_field(name="🚀 Boosts", value=f"**{boosts}** boosts (Nível {nivel_boost})", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
        
        embed = discord.Embed(title=f"🖼️ Avatar de {member.name}", color=member.color if member.color != discord.Color.default() else 0x2b2d31)
        embed.set_image(url=avatar_url)
        
        if member.avatar:
            links = f"[PNG]({member.avatar.with_format('png').url}) | [JPG]({member.avatar.with_format('jpg').url}) | [WEBP]({member.avatar.with_format('webp').url})"
            if member.avatar.is_animated():
                links += f" | [GIF]({member.avatar.with_format('gif').url})"
            embed.add_field(name="Download", value=links, inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Utils(bot))
