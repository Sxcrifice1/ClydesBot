import discord
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timezone, timedelta
import random
import os
from aiohttp import web

async def handle(request):
    return web.Response(text="Bot is running!")

async def run_dummy_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get('PORT', 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    print(f'Dummy web server running on port {port}')

from config import TOKEN, CANAL_SHOW_EVENTS_ID, MOD_LOG_ID, KEYS_FILE, load_json
user_keys = load_json(KEYS_FILE)

intents = discord.Intents.default()
intents.members = True 
intents.message_content = True 

class RoleSelect(discord.ui.Select):
    def __init__(self, placeholder, options_list, custom_id):
        options = [discord.SelectOption(label=opt) for opt in options_list]
        super().__init__(placeholder=placeholder, min_values=1, max_values=len(options), options=options, custom_id=custom_id)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        added_roles = []
        await interaction.response.defer(ephemeral=True)
        for value in self.values:
            role = discord.utils.get(guild.roles, name=value)
            if not role:
                role = await guild.create_role(name=value, mentionable=True, reason="Auto setup")
            if role not in member.roles:
                await member.add_roles(role)
                added_roles.append(role.name)
        if added_roles:
            await interaction.followup.send(f"✅ Cargos adicionados: **{', '.join(added_roles)}**", ephemeral=True)
        else:
            await interaction.followup.send("Você já possui esses cargos!", ephemeral=True)

class RolesView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleSelect("🎧 Escolha sua DAW", ["FL Studio", "Ableton Live", "Pro Tools", "Logic Pro", "Studio One", "Reaper", "Cubase"], "select_daws"))
        self.add_item(RoleSelect("🎨 Software de Edição/Design", ["Photoshop", "Premiere Pro", "After Effects", "DaVinci Resolve", "Illustrator", "Sony Vegas"], "select_softwares"))
        self.add_item(RoleSelect("💼 Sua Função/Especialidade", ["Produtor Musical", "Beatmaker", "Cantor/Vocalista", "Editor de Vídeo", "Designer", "Músico"], "select_funcoes"))

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Criar Chat com IA", style=discord.ButtonStyle.primary, custom_id="open_ai_chat", emoji="🤖")
    async def open_chat(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        category = interaction.channel.category
        channel_name = f"ia-{member.name.lower()}"
        existing_channel = discord.utils.get(guild.text_channels, name=channel_name)
        if existing_channel:
            await interaction.response.send_message(f"Você já possui um chat aberto em {existing_channel.mention}!", ephemeral=True)
            return
            
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        position = interaction.channel.position + 1
        channel = await guild.create_text_channel(channel_name, category=category, position=position, overwrites=overwrites)
        
        has_key = str(member.id) in user_keys
        if has_key:
            desc = (
                f"Bem-vindo de volta, {member.mention}! Sua chave de API do Google Gemini já está salva de forma segura.\n\n"
                "Você pode usar `!help` para ver os comandos de IA.\n\n"
                "⏳ **Regra de Inatividade:** Chat fecha automaticamente após 5 minutos sem uso."
            )
        else:
            desc = (
                f"Olá {member.mention}! Este é o seu espaço privado na Clydes.\n\n"
                "Para conversar, você precisa informar a sua própria **Chave de API do Google Gemini**.\n\n"
                "**Como pegar sua chave (100% Grátis):**\n"
                "1. Acesse [Google AI Studio](https://aistudio.google.com/app/apikey) com o seu Google.\n"
                "2. Clique em **Create API Key**.\n"
                "3. Copie o código gerado (começa com `AIza...` ou `AQ.`) e envie aqui no chat.\n\n"
                "A chave será salva e apagada da tela por segurança.\n\n"
                "⏳ **Regra de Inatividade:** Se este chat ficar inativo por 5 minutos, ele será fechado."
            )
        
        embed = discord.Embed(title="🤖 Chat Privado com a IA", description=desc, color=0x00ffaa)
        await channel.send(content=member.mention, embed=embed)
        await interaction.response.send_message(f"Sua sala secreta foi criada: {channel.mention}", ephemeral=True)

class CollabModal(discord.ui.Modal, title='Procurar Collab'):
    cargo = discord.ui.TextInput(label='Qual cargo você procura?', placeholder='Ex: Beatmaker, Cantor...', required=True)
    mensagem = discord.ui.TextInput(label='Descreva o projeto', style=discord.TextStyle.long, placeholder='Estou precisando de um beat...', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        cargo_str = self.cargo.value.strip()
        role = discord.utils.get(interaction.guild.roles, name=cargo_str)
        mencao = role.mention if role else f"**{cargo_str}**"
        
        embed = discord.Embed(title="🤝 Nova Busca por Collab", description=self.mensagem.value, color=0x00ffaa)
        embed.set_author(name=interaction.user.name, icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
        embed.set_footer(text="Mande uma mensagem direta (DM) para o criador se tiver interesse!")
        
        await interaction.channel.send(content=f"🔔 Chamando: {mencao}", embed=embed)
        await interaction.response.send_message("✅ Seu anúncio de collab foi postado!", ephemeral=True)

class CollabView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="🤝 Pedir Collab", style=discord.ButtonStyle.success, custom_id="btn_collab")
    async def btn_collab(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(CollabModal())

class PortfolioModal(discord.ui.Modal, title='Cadastrar Portfólio'):
    especialidade = discord.ui.TextInput(label='Sua Especialidade', placeholder='Ex: Produtor, Editor, Designer...', required=True)
    links = discord.ui.TextInput(label='Seus Links', style=discord.TextStyle.long, placeholder='Ex: Instagram: @seu_insta\nSoundcloud: link', required=True)

    async def on_submit(self, interaction: discord.Interaction):
        canal_mod_log = interaction.client.get_channel(MOD_LOG_ID)
        if canal_mod_log:
            await canal_mod_log.send(f"[PORTFOLIO_DB] | UserID: {interaction.user.id} | {self.links.value}")
            
        embed = discord.Embed(title=f"📁 Portfólio de {interaction.user.name}", description=f"**Especialidade:** {self.especialidade.value}\n\n**Links:**\n{self.links.value}", color=0x9b59b6)
        if interaction.user.avatar: embed.set_thumbnail(url=interaction.user.avatar.url)
        
        await interaction.channel.send(embed=embed)
        await interaction.response.send_message("✅ Seu cartão de portfólio foi publicado na vitrine!", ephemeral=True)

class PortfolioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="📁 Cadastrar / Atualizar Portfólio", style=discord.ButtonStyle.primary, custom_id="btn_portfolio")
    async def btn_portfolio(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PortfolioModal())

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.remove_command('help')
        
    async def setup_hook(self):
        self.loop.create_task(run_dummy_server())
        self.add_view(RolesView())
        self.add_view(TicketView())
        self.add_view(CollabView())
        self.add_view(PortfolioView())
        
        cogs = [
            "cogs.admin",
            "cogs.ai",
            "cogs.community",
            "cogs.downloads",
            "cogs.events",
            "cogs.moderation",
            "cogs.utils",
            "cogs.xp",
            "cogs.voice"
        ]
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Cog loaded: {cog}")
            except Exception as e:
                print(f"Failed to load cog {cog}: {e}")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'Bot conectado e Cogs carregadas!')
    if not cleanup_inactive_tickets.is_running():
        cleanup_inactive_tickets.start()
    if not desafio_semanal.is_running():
        desafio_semanal.start()

@tasks.loop(minutes=1)
async def cleanup_inactive_tickets():
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.name.startswith("ia-"):
                try:
                    if channel.last_message_id:
                        last_message = await channel.fetch_message(channel.last_message_id)
                        last_time = last_message.created_at
                    else:
                        last_time = channel.created_at
                    if datetime.now(timezone.utc) - last_time > timedelta(minutes=5):
                        await channel.delete(reason="Inatividade de 5 minutos")
                except:
                    pass

DESAFIOS = [
    "Crie um beat apenas usando samples de água e moedas.",
    "Faça um logo usando exclusivamente a cor Roxa e tipografia minimalista.",
    "Produza um drop de 30 segundos usando apenas sons de videogame dos anos 90.",
    "Edite um mini-vlog de 15 segundos sobre o seu café da manhã em ritmo frenético.",
    "Crie uma melodia triste, mas usando um BPM de música eletrônica animada (128bpm)."
]

@tasks.loop(hours=1)
async def desafio_semanal():
    agora = datetime.now()
    if agora.weekday() == 4 and agora.hour == 18:
        canal = bot.get_channel(CANAL_SHOW_EVENTS_ID)
        if canal:
            embed = discord.Embed(
                title="🏆 DESAFIO SEMANAL CLYDES",
                description=random.choice(DESAFIOS),
                color=0xff0000
            )
            embed.set_footer(text="Mostrem do que são capazes e postem as artes/músicas aqui no canal!")
            await canal.send(embed=embed)

if __name__ == "__main__":
    bot.run(TOKEN)
