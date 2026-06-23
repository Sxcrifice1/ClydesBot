import discord
from discord.ext import commands
from datetime import datetime, timezone

from config import MOD_LOG_ID, CANAL_BEM_VINDO_ID, CANAL_SELF_ROLES_ID, CANAL_BOOSTS_ID, COMMUNITY_CATEGORY_ID, STARBOARD_THRESHOLD

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.join_timestamps = []

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        canal_log = self.bot.get_channel(MOD_LOG_ID)
        if not canal_log: return
        embed = discord.Embed(title="🗑️ Mensagem Deletada", color=0xe74c3c, timestamp=discord.utils.utcnow())
        embed.add_field(name="Autor", value=f"{message.author.mention} ({message.author})", inline=True)
        embed.add_field(name="Canal", value=message.channel.mention, inline=True)
        content = message.content[:1024] if message.content else "*Sem texto (possível embed/arquivo)*"
        embed.add_field(name="Conteúdo", value=content, inline=False)
        if message.attachments:
            embed.add_field(name="Anexos", value="\n".join([a.filename for a in message.attachments]), inline=False)
        await canal_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot: return
        if before.content == after.content: return
        canal_log = self.bot.get_channel(MOD_LOG_ID)
        if not canal_log: return
        embed = discord.Embed(title="✏️ Mensagem Editada", color=0xf39c12, timestamp=discord.utils.utcnow())
        embed.add_field(name="Autor", value=f"{before.author.mention} ({before.author})", inline=True)
        embed.add_field(name="Canal", value=before.channel.mention, inline=True)
        embed.add_field(name="Antes", value=before.content[:1024] or "*vazio*", inline=False)
        embed.add_field(name="Depois", value=after.content[:1024] or "*vazio*", inline=False)
        embed.add_field(name="Link", value=f"[Ir para mensagem]({after.jump_url})", inline=False)
        await canal_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        canal_log = self.bot.get_channel(MOD_LOG_ID)
        if not canal_log: return
        embed = discord.Embed(title="🔨 Membro Banido (Log do Discord)", color=0xe74c3c, timestamp=discord.utils.utcnow())
        embed.add_field(name="Usuário", value=f"{user} ({user.id})", inline=False)
        if user.avatar:
            embed.set_thumbnail(url=user.avatar.url)
        await canal_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        canal_log = self.bot.get_channel(MOD_LOG_ID)
        if not canal_log: return
        embed = discord.Embed(title="👋 Membro Saiu", color=0x95a5a6, timestamp=discord.utils.utcnow())
        embed.add_field(name="Usuário", value=f"{member} ({member.id})", inline=True)
        cargos = [r.name for r in member.roles if r.name != "@everyone"]
        embed.add_field(name="Cargos", value=", ".join(cargos) if cargos else "Nenhum", inline=False)
        await canal_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        agora = datetime.now(timezone.utc)
        self.join_timestamps.append(agora)
        self.join_timestamps = [t for t in self.join_timestamps if (agora - t).total_seconds() <= 10]
        
        if len(self.join_timestamps) >= 5:
            canal_log = self.bot.get_channel(MOD_LOG_ID)
            if canal_log:
                embed = discord.Embed(
                    title="🚨 ALERTA DE RAID DETECTADO",
                    description=f"**{len(self.join_timestamps)} contas** entraram nos últimos 10 segundos!\nConsidere usar `!lockdown` para travar os canais.",
                    color=0xff0000,
                    timestamp=discord.utils.utcnow()
                )
                await canal_log.send(embed=embed)
            self.join_timestamps.clear()
        
        cargo_membro = discord.utils.get(member.guild.roles, name="Membro")
        if not cargo_membro:
            try:
                cargo_membro = await member.guild.create_role(name="Membro", reason="Auto-role setup")
            except:
                pass
        if cargo_membro:
            try:
                await member.add_roles(cargo_membro)
            except:
                pass
        
        canal = self.bot.get_channel(CANAL_BEM_VINDO_ID)
        if canal:
            embed = discord.Embed(title=f"👋 Bem-vindo(a), {member.name}!", description=f"A comunidade Clydes está feliz com sua chegada!\n\nVá em <#{CANAL_SELF_ROLES_ID}> para escolher seus cargos.", color=0x00ffaa)
            if member.avatar: embed.set_thumbnail(url=member.avatar.url)
            await canal.send(content=member.mention, embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.premium_since is None and after.premium_since is not None:
            canal = self.bot.get_channel(CANAL_BOOSTS_ID)
            if canal:
                embed = discord.Embed(title="🚀 Novo Impulso na Clydes!", description=f"Obrigado pelo Boost, {after.mention}!", color=0xff73fa)
                await canal.send(content=after.mention, embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ Você não tem permissão para usar esse comando.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("❌ Membro não encontrado. Verifique a menção.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"⚠️ Argumento faltando: `{error.param.name}`. Use `!help` para ver os comandos.")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Argumento inválido. Verifique o formato do comando.")
        else:
            await ctx.send("❌ Ocorreu um erro inesperado. O administrador foi notificado.")
            canal_log = self.bot.get_channel(MOD_LOG_ID)
            if canal_log:
                embed = discord.Embed(title="⚠️ Erro de Comando", color=0xff0000, timestamp=discord.utils.utcnow())
                embed.add_field(name="Comando", value=ctx.message.content[:1024], inline=False)
                embed.add_field(name="Autor", value=f"{ctx.author} ({ctx.author.id})", inline=True)
                embed.add_field(name="Canal", value=ctx.channel.mention, inline=True)
                embed.add_field(name="Erro", value=str(error)[:1024], inline=False)
                await canal_log.send(embed=embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if str(payload.emoji) != "⭐":
            return
        
        channel = self.bot.get_channel(payload.channel_id)
        if not channel: return
        
        try:
            message = await channel.fetch_message(payload.message_id)
        except:
            return
        
        if message.author.bot: return
        
        reacao = discord.utils.get(message.reactions, emoji="⭐")
        if not reacao or reacao.count < STARBOARD_THRESHOLD:
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if not guild: return
        
        canal_destaques = discord.utils.get(guild.text_channels, name="destaques")
        if not canal_destaques:
            category = discord.utils.get(guild.categories, id=COMMUNITY_CATEGORY_ID)
            canal_destaques = await guild.create_text_channel("destaques", category=category)
        
        async for msg in canal_destaques.history(limit=100):
            if msg.embeds and msg.embeds[0].footer and str(payload.message_id) in (msg.embeds[0].footer.text or ""):
                embed_atualizado = msg.embeds[0].copy()
                embed_atualizado.title = f"⭐ {reacao.count} | #{channel.name}"
                await msg.edit(embed=embed_atualizado)
                return
        
        embed = discord.Embed(
            title=f"⭐ {reacao.count} | #{channel.name}",
            description=message.content[:2048] if message.content else "",
            color=0xf1c40f,
            timestamp=message.created_at
        )
        embed.set_author(name=message.author.name, icon_url=message.author.avatar.url if message.author.avatar else None)
        
        if message.attachments:
            if message.attachments[0].content_type and message.attachments[0].content_type.startswith("image"):
                embed.set_image(url=message.attachments[0].url)
        
        embed.add_field(name="Original", value=f"[Ir para mensagem]({message.jump_url})", inline=False)
        embed.set_footer(text=f"ID: {message.id}")
        
        await canal_destaques.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Events(bot))
