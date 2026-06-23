import discord
from discord.ext import commands
from config import MOD_LOG_ID, ADMIN_CATEGORY_ID, CANAL_BEM_VINDO_ID, CANAL_SELF_ROLES_ID, CANAL_BOOSTS_ID, CANAL_SHOW_EVENTS_ID, COMMUNITY_CATEGORY_ID

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_admin_canais(self, ctx):
        categoria = discord.utils.get(ctx.guild.categories, id=ADMIN_CATEGORY_ID)
        if not categoria:
            return await ctx.send("❌ Categoria de administradores não encontrada.")
            
        guia_channel = ctx.guild.get_channel(1519066501502603455)
        if not guia_channel:
            guia_channel = discord.utils.get(ctx.guild.text_channels, name="guia-de-comandos")
        if not guia_channel:
            guia_channel = await ctx.guild.create_text_channel("guia-de-comandos", category=categoria)
        
        await guia_channel.purge(limit=50)

        # ── EMBED 1: Cabeçalho ──
        header = discord.Embed(
            title="📚 Manual Completo do Bot — Clydes",
            description=(
                "Abaixo está a lista de **todos** os comandos e sistemas do bot.\n"
                "Comandos marcados com 🔒 são restritos a **Administradores**.\n"
                "Comandos marcados com 🔓 podem ser usados por **qualquer membro**."
            ),
            color=0x2b2d31
        )
        await guia_channel.send(embed=header)

        # ── EMBED 2: Sistemas Automáticos ──
        e_auto = discord.Embed(title="🛡️ Sistemas Automáticos (Invisíveis)", color=0xe74c3c)
        e_auto.add_field(
            name="AutoMod de Palavrões",
            value="Detecta xingamentos (inclusive com leetspeak e espaços) → deleta a mensagem → avisa o usuário → aplica timeout de 10 min.",
            inline=False
        )
        e_auto.add_field(
            name="Limpeza de Chats de IA",
            value="Canais `ia-` inativos por mais de 5 minutos são deletados automaticamente.",
            inline=False
        )
        e_auto.add_field(
            name="Desafio Semanal",
            value="Toda sexta-feira às 18h, o bot posta um desafio criativo aleatório no canal de eventos.",
            inline=False
        )
        e_auto.add_field(
            name="Boas-vindas & Boosts",
            value="Envia embeds automáticos quando um membro entra ou dá boost no servidor.",
            inline=False
        )
        await guia_channel.send(embed=e_auto)

        # ── EMBED 3: Comandos de Voz ──
        e_voz = discord.Embed(title="🎙️ Sistema de Voz com IA (ElevenLabs)", color=0x9b59b6)
        e_voz.add_field(
            name="🔒 !aviso_voz <minutos> <texto>",
            value=(
                "O bot gera uma voz clonada com o texto, entra na sua call, "
                "muta todo mundo, fala e depois sai.\n"
                "Se `<minutos>` for `0`, fala uma vez só.\n"
                "Se for maior que `0`, repete o aviso a cada X minutos.\n"
                "**Exemplo:** `!aviso_voz 0 Atenção, o evento começa agora!`\n"
                "**Exemplo com loop:** `!aviso_voz 5 Lembrete: reunião em andamento`\n"
                "📌 *Só funciona no #mod-logs*"
            ),
            inline=False
        )
        e_voz.add_field(
            name="🔒 !aviso_voz <minutos> <link>",
            value=(
                "Igual ao comando acima, mas em vez de gerar voz nova, "
                "usa um MP3 já existente (do #banco-de-vozes).\n"
                "**Custo de tokens: ZERO!**\n"
                "**Exemplo:** `!aviso_voz 0 https://cdn.discordapp.com/.../audio.mp3`"
            ),
            inline=False
        )
        e_voz.add_field(
            name="🔒 !parar_aviso",
            value="Para imediatamente o loop de avisos e desconecta o bot da call.\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        await guia_channel.send(embed=e_voz)

        # ── EMBED 4: Rádio ──
        e_radio = discord.Embed(title="📻 Rádio Lo-fi 24/7", color=0x1abc9c)
        e_radio.add_field(
            name="🔓 !radio",
            value=(
                "Liga a rádio Lo-fi Girl (livestream do YouTube) no canal de voz `lofi-radio`.\n"
                "Se o canal não existir, entra na call onde você está.\n"
                "**Exemplo:** `!radio`"
            ),
            inline=False
        )
        e_radio.add_field(
            name="🔓 !parar_radio",
            value="Desconecta o bot da call e para a rádio.\n**Exemplo:** `!parar_radio`",
            inline=False
        )
        await guia_channel.send(embed=e_radio)

        # ── EMBED 5: Downloads e Análise ──
        e_dl = discord.Embed(title="🎧 Downloads e Análise Musical", color=0x3498db)
        e_dl.add_field(
            name="🔓 !dl_audio <link>",
            value=(
                "Baixa o áudio de um vídeo do YouTube/SoundCloud e envia como MP3.\n"
                "**Exemplo:** `!dl_audio https://www.youtube.com/watch?v=dQw4w9WgXcQ`"
            ),
            inline=False
        )
        e_dl.add_field(
            name="🔓 !dl_video <link>",
            value=(
                "Baixa o vídeo do YouTube e envia como MP4 (limite 25MB).\n"
                "**Exemplo:** `!dl_video https://www.youtube.com/watch?v=dQw4w9WgXcQ`"
            ),
            inline=False
        )
        e_dl.add_field(
            name="🔓 !info_audio",
            value=(
                "Anexe um arquivo de áudio (MP3/WAV/OGG) na mensagem e use este comando.\n"
                "O bot analisa: Duração, Sample Rate, Canais, Bitrate, **BPM** e **Tom Musical**.\n"
                "**Exemplo:** Arraste o arquivo + digite `!info_audio`"
            ),
            inline=False
        )
        await guia_channel.send(embed=e_dl)

        # ── EMBED 6: IA / Chat Privado ──
        e_ia = discord.Embed(title="🤖 Inteligência Artificial (Gemini)", color=0x5865F2)
        e_ia.add_field(
            name="🔓 Conversar com IA",
            value=(
                "Clique no botão do painel de IA para abrir uma sala privada.\n"
                "Na primeira vez, cole sua chave da API do Google Gemini.\n"
                "Depois é só conversar normalmente, sem comandos."
            ),
            inline=False
        )
        e_ia.add_field(
            name="🔓 !help",
            value="Mostra a central de ajuda da IA (só funciona dentro de canais `ia-`).\n**Exemplo:** `!help`",
            inline=False
        )
        e_ia.add_field(
            name="🔓 !nome_beat <vibe>",
            value="A IA gera 5 nomes comerciais para sua track/beat.\n**Exemplo:** `!nome_beat dark trap agressivo`",
            inline=False
        )
        e_ia.add_field(
            name="🔓 !analise_capa",
            value="Anexe uma imagem e a IA faz uma análise técnica de design (cores, tipografia, contraste).\n**Exemplo:** Arraste a imagem + `!analise_capa`",
            inline=False
        )
        e_ia.add_field(
            name="🔓 !ideia",
            value="A IA gera um desafio criativo aleatório para música ou vídeo.\n**Exemplo:** `!ideia`",
            inline=False
        )
        e_ia.add_field(
            name="🔓 !format <título>",
            value="Anexe um arquivo e o bot posta formatado no canal de artes/eventos.\n**Exemplo:** `!format Meu Novo Beat`",
            inline=False
        )
        e_ia.add_field(
            name="🔒 !resumo #canal",
            value="A IA lê as últimas 250 mensagens de um canal e gera um resumo em tópicos.\n**Exemplo:** `!resumo #geral`\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        await guia_channel.send(embed=e_ia)

        # ── EMBED 7: Setup e Admin ──
        e_admin = discord.Embed(title="⚙️ Comandos de Administração", color=0xe67e22)
        e_admin.add_field(
            name="🔒 !setup",
            value="Envia o painel de Self-Roles (DAWs, Softwares, Funções) no canal atual.\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        e_admin.add_field(
            name="🔒 !painel_ia",
            value="Envia o painel com botão para abrir chat privado com a IA.\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        e_admin.add_field(
            name="🔒 !setup_comunidade",
            value="Cria os canais de comunidade (portfolios, collabs, lofi-radio) se não existirem.\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        e_admin.add_field(
            name="🔒 !painel_portfolios",
            value="Envia o painel interativo no canal #portfolios (botão + modal).\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        e_admin.add_field(
            name="🔒 !painel_collabs",
            value="Envia o painel interativo no canal #collabs (botão + modal).\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        e_admin.add_field(
            name="🔒 !criar_cargos",
            value="Cria todos os cargos padrão do servidor (DAWs, Softwares, Funções).\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        e_admin.add_field(
            name="🔒 !travar_canais",
            value="Bloqueia o envio de mensagens nos canais de exibição (boas-vindas, roles, boosts, etc).\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        e_admin.add_field(
            name="🔒 !regras",
            value="Envia o embed de regras no canal de Self-Roles.\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        e_admin.add_field(
            name="🔒 !setup_admin_canais",
            value="Cria/atualiza o canal #guia-de-comandos e #banco-de-vozes na categoria de admins.\n📌 *Só funciona no #mod-logs*",
            inline=False
        )
        await guia_channel.send(embed=e_admin)

        # ── EMBED 8: Moderação (Novo) ──
        e_mod = discord.Embed(title="🛡️ Comandos de Moderação", color=0xe74c3c)
        e_mod.add_field(name="🔒 !ban / !kick", value="Bane ou expulsa um membro.\n**Exemplo:** `!ban @user motivo`", inline=False)
        e_mod.add_field(name="🔒 !warn / !warns", value="Dá advertência ou lista os avisos. (3 Warns = Ban).\n**Exemplo:** `!warn @user motivo`", inline=False)
        e_mod.add_field(name="🔒 !mute / !unmute", value="Muta temporariamente (timeout).\n**Exemplo:** `!mute @user 1h spam`", inline=False)
        e_mod.add_field(name="🔒 !clear <qnt>", value="Apaga até 100 mensagens.\n**Exemplo:** `!clear 10`", inline=False)
        e_mod.add_field(name="🔒 !lockdown / !unlock", value="Tranca ou destranca o canal atual.", inline=False)
        await guia_channel.send(embed=e_mod)

        # ── EMBED 9: XP e Comunidade (Novo) ──
        e_xp = discord.Embed(title="🌟 Engajamento e Comunidade", color=0xf1c40f)
        e_xp.add_field(name="🔓 !rank / !leaderboard", value="Vê seu nível de XP atual ou o top 10 do servidor.", inline=False)
        e_xp.add_field(name="🔓 !sugestao <texto>", value="Cria uma sugestão no canal de sugestões.", inline=False)
        e_xp.add_field(name="🔓 !poll <perg | op1 | op2>", value="Cria uma enquete com reações numeradas.", inline=False)
        e_xp.add_field(name="🔒 !sorteio <tempo> <premio>", value="Inicia um sorteio no canal.\n**Exemplo:** `!sorteio 1h Nitro`", inline=False)
        e_xp.add_field(name="🔒 !reroll", value="Sorteia um novo ganhador para o último sorteio.", inline=False)
        await guia_channel.send(embed=e_xp)

        # ── EMBED 10: Utilitários (Novo) ──
        e_util = discord.Embed(title="🛠️ Utilitários e Starboard", color=0x3498db)
        e_util.add_field(name="🔓 !userinfo / !serverinfo", value="Mostra informações do usuário ou do servidor.", inline=False)
        e_util.add_field(name="🔓 !avatar @user", value="Mostra a foto de perfil em alta resolução.", inline=False)
        e_util.add_field(name="⭐ Starboard (Automático)", value="Mensagens que receberem 3 reações de ⭐ vão para o canal #destaques.", inline=False)
        await guia_channel.send(embed=e_util)
            
        banco_channel = discord.utils.get(ctx.guild.text_channels, name="banco-de-vozes")
        if not banco_channel:
            banco_channel = await ctx.guild.create_text_channel("banco-de-vozes", category=categoria)
            await banco_channel.send(
                "**🎙️ Banco de Vozes do Servidor**\n"
                "Todos os avisos gerados pelo ElevenLabs ficarão salvos aqui.\n\n"
                "**Como reutilizar sem gastar tokens:**\n"
                "1. Clique com botão direito no arquivo de áudio\n"
                "2. Selecione **Copiar Link**\n"
                "3. Cole no comando: `!aviso_voz 0 <link>`"
            )
            
        await ctx.send(f"✅ Canais e Guias atualizados com sucesso em **{categoria.name}**!")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def painel_ia(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        await ctx.message.delete()
        embed = discord.Embed(title="🧠 Fale com a Inteligência Artificial", description="Clique abaixo para abrir sua sala privada.", color=0x5865F2)
        await ctx.send(embed=embed, view=TicketView())

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_guia_publico(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        
        canal_publico = ctx.guild.get_channel(1374208274668195853)
        if not canal_publico:
            return await ctx.send("❌ Canal público de comandos (ID 1374208274668195853) não encontrado.")
            
        await canal_publico.purge(limit=50)
        
        header = discord.Embed(
            title="📚 Manual de Comandos da Clydes",
            description=("Bem-vindo! Aqui estão todos os comandos que você pode usar no nosso servidor para criar, interagir e se divertir.\n\n"
                         "Todos os comandos abaixo são marcados como 🔓 (Acesso Livre)."),
            color=0x2b2d31
        )
        await canal_publico.send(embed=header)
        
        e_radio = discord.Embed(title="📻 Rádio Lo-fi 24/7", color=0x1abc9c)
        e_radio.add_field(name="🔓 !radio", value="Liga a rádio Lo-fi no canal `lofi-radio` ou no seu canal atual.", inline=False)
        e_radio.add_field(name="🔓 !parar_radio", value="Desconecta a rádio da call.", inline=False)
        await canal_publico.send(embed=e_radio)
        
        e_dl = discord.Embed(title="🎧 Downloads e Análise", color=0x3498db)
        e_dl.add_field(name="🔓 !dl_audio <link>", value="Baixa o áudio de um vídeo do YouTube/SoundCloud.", inline=False)
        e_dl.add_field(name="🔓 !dl_video <link>", value="Baixa o vídeo do YouTube (limite 25MB).", inline=False)
        e_dl.add_field(name="🔓 !info_audio", value="Anexe um MP3/WAV para analisar BPM, Tom Musical, etc.", inline=False)
        await canal_publico.send(embed=e_dl)
        
        e_ia = discord.Embed(title="🤖 Inteligência Artificial (Gemini)", color=0x5865F2)
        e_ia.add_field(name="🔓 Conversar com IA", value="Clique no botão do painel de IA para abrir seu chat privado.", inline=False)
        e_ia.add_field(name="🔓 !help", value="Mostra a ajuda da IA (apenas em canais `ia-`).", inline=False)
        e_ia.add_field(name="🔓 !nome_beat <vibe>", value="Gera 5 nomes comerciais para sua música.", inline=False)
        e_ia.add_field(name="🔓 !analise_capa", value="Anexe uma imagem para análise técnica de design.", inline=False)
        e_ia.add_field(name="🔓 !ideia", value="Gera um desafio criativo aleatório.", inline=False)
        e_ia.add_field(name="🔓 !format <titulo>", value="Formata um arquivo para envio em eventos.", inline=False)
        await canal_publico.send(embed=e_ia)
        
        e_xp = discord.Embed(title="🌟 Engajamento e Utilidades", color=0xf1c40f)
        e_xp.add_field(name="🔓 !rank / !leaderboard", value="Vê seu nível de XP atual ou o top 10 do servidor.", inline=False)
        e_xp.add_field(name="🔓 !sugestao <texto>", value="Cria uma sugestão no canal de sugestões.", inline=False)
        e_xp.add_field(name="🔓 !poll <perg | op1 | op2>", value="Cria uma enquete.", inline=False)
        e_xp.add_field(name="🔓 !userinfo / !serverinfo", value="Mostra dados do seu perfil ou do servidor.", inline=False)
        e_xp.add_field(name="🔓 !avatar @user", value="Mostra e baixa a foto de perfil.", inline=False)
        e_xp.add_field(name="⭐ Starboard (Automático)", value="Mensagens com 3 reações de ⭐ vão para os destaques.", inline=False)
        await canal_publico.send(embed=e_xp)
        
        await ctx.send("✅ Guia público atualizado com sucesso no canal " + canal_publico.mention)


    async def setup(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        await ctx.message.delete()
        embed = discord.Embed(title="🎙️ Bem-Vindo à Clydes!", description="Escolha seus cargos abaixo.", color=0xffaa00)
        await ctx.send(embed=embed, view=RolesView())


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def travar_canais(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        canais_id = [CANAL_BEM_VINDO_ID, CANAL_SELF_ROLES_ID, CANAL_BOOSTS_ID, CANAL_SHOW_EVENTS_ID]
        canais = [ctx.guild.get_channel(cid) for cid in canais_id if ctx.guild.get_channel(cid)]
        
        for name in ["portfolios", "collabs"]:
            c = discord.utils.get(ctx.guild.text_channels, name=name)
            if c: canais.append(c)

        sucesso = 0
        for canal in canais:
            if canal:
                perms = canal.overwrites_for(ctx.guild.default_role)
                perms.send_messages = False
                await canal.set_permissions(ctx.guild.default_role, overwrite=perms)
                sucesso += 1
        await ctx.send(f"🔒 {sucesso} canais travados.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def regras(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        await ctx.message.delete()
        canal = bot.get_channel(CANAL_SELF_ROLES_ID)
        if canal:
            embed = discord.Embed(title="📜 Regras Oficiais - Clydes", description="Sem discurso de ódio. Sem spam. Respeito acima de tudo.", color=0xff0000)
            await canal.send(embed=embed)


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def criar_cargos(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        cargos = ["FL Studio", "Ableton Live", "Pro Tools", "Photoshop", "Premiere Pro", "After Effects", "Produtor Musical", "Beatmaker", "Cantor/Vocalista", "Editor de Vídeo", "Designer", "Músico"]
        for c in cargos:
            if not discord.utils.get(ctx.guild.roles, name=c):
                await ctx.guild.create_role(name=c, mentionable=True)
        await ctx.send("✅ Cargos criados.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_comunidade(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        category = discord.utils.get(ctx.guild.categories, id=COMMUNITY_CATEGORY_ID)
        if not category:
            await ctx.send("❌ Categoria Community não encontrada.")
            return
        
        canais_texto = {"📁┃portfolios": "portfolios", "🤝┃collabs": "collabs"}
        for nome_completo, nome_busca in canais_texto.items():
            if not discord.utils.find(lambda c: nome_busca in c.name.lower(), category.text_channels):
                await ctx.guild.create_text_channel(name=nome_completo, category=category)
        
        if not discord.utils.find(lambda c: "lofi-radio" in c.name.lower(), category.voice_channels):
            await ctx.guild.create_voice_channel(name="📻┃lofi-radio", category=category)
            
        await ctx.send("✅ Canais de comunidade (portfolios, collabs, lofi-radio) criados/verificados com sucesso!")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def painel_collabs(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        canal_collab = discord.utils.find(lambda c: "collabs" in c.name.lower(), ctx.guild.text_channels)
        if not canal_collab:
            category = discord.utils.get(ctx.guild.categories, id=COMMUNITY_CATEGORY_ID)
            canal_collab = await ctx.guild.create_text_channel(name="🤝┃collabs", category=category)
            

        
        desc = (
            "Bem-vindo ao **Quadro de Collabs** oficial da Clydes!\n\n"
            "Se você precisa de um Beatmaker, Vocalista, Editor de Vídeo ou Designer para o seu projeto, este é o lugar certo para recrutar talentos.\n\n"
            "**Como funciona?**\n"
            "1️⃣ Clique no botão **🤝 Pedir Collab** abaixo.\n"
            "2️⃣ Uma janela vai se abrir. Digite o cargo que você procura e descreva o projeto.\n"
            "3️⃣ O bot criará o seu anúncio e notificará todos os especialistas.\n\n"
            "*(Aviso: O chat deste canal é bloqueado. Interaja apenas pelo botão).* "
        )
        embed = discord.Embed(title="🤝 Central de Collabs e Networking", description=desc, color=0x00ffaa)
        await canal_collab.send(embed=embed, view=CollabView())
        await ctx.send("✅ Painel de Collabs atualizado em #collabs.")


    @commands.command()
    @commands.has_permissions(administrator=True)
    async def painel_portfolios(self, ctx):
        if ctx.channel.id != MOD_LOG_ID: return
        canal_portfolios = discord.utils.find(lambda c: "portfolios" in c.name.lower(), ctx.guild.text_channels)
        if not canal_portfolios:
            category = discord.utils.get(ctx.guild.categories, id=COMMUNITY_CATEGORY_ID)
            canal_portfolios = await ctx.guild.create_text_channel(name="📁┃portfolios", category=category)
        
        desc = (
            "Apresente o seu trabalho para a comunidade na nossa **Vitrine de Portfólios**!\n\n"
            "Construa o seu Cartão de Visitas digital. Fique visível para outros produtores, editores e artistas que buscam colaborações.\n\n"
            "**Como funciona?**\n"
            "1️⃣ Clique no botão **📁 Cadastrar / Atualizar Portfólio**.\n"
            "2️⃣ Informe a sua Especialidade (Ex: Beatmaker, Designer).\n"
            "3️⃣ Cole os links das suas redes ou trabalhos.\n"
            "4️⃣ O bot gerará o seu cartão elegante e o deixará exposto aqui no canal.\n\n"
            "*(Aviso: O chat deste canal é bloqueado. Interaja apenas pelo botão).* "
        )
        embed = discord.Embed(title="📁 Vitrine de Portfólios", description=desc, color=0x9b59b6)
        await canal_portfolios.send(embed=embed, view=PortfolioView())
        await ctx.send("✅ Painel de Portfólios atualizado em #portfolios.")




    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setup_guia_publico(self, ctx):
        if ctx.channel.id != MOD_LOG_ID:
            return await ctx.send("❌ Comando restrito ao canal de Logs da Moderação.", delete_after=5)

        guia_channel = ctx.guild.get_channel(1374208274668195853)
        if not guia_channel:
            return await ctx.send("❌ Canal de comandos público (1374208274668195853) não encontrado.")
        
        await guia_channel.purge(limit=50)

        header = discord.Embed(
            title="📚 Cola de Comandos — Clydes",
            description="Aqui estão os comandos públicos que você pode usar no servidor!",
            color=0x2b2d31
        )
        await guia_channel.send(embed=header)

        e_audio = discord.Embed(title="🎵 Comandos de Áudio", color=0x3498db)
        e_audio.add_field(name="🔓 !play_radio <url>", value="Toca uma rádio ao vivo do YouTube.", inline=False)
        e_audio.add_field(name="🔓 !stop_radio", value="Para a rádio e desconecta o bot.", inline=False)
        e_audio.add_field(name="🔓 !dl_audio <url>", value="Baixa o áudio de um vídeo do YouTube.", inline=False)
        e_audio.add_field(name="🔓 !dl_video <url>", value="Baixa o vídeo em MP4 do YouTube.", inline=False)
        e_audio.add_field(name="🔓 !info_audio", value="Analisa BPM e Tom de um arquivo anexado.", inline=False)
        await guia_channel.send(embed=e_audio)

        e_ia = discord.Embed(title="🤖 Comandos de Inteligência Artificial", color=0x9b59b6)
        e_ia.add_field(name="🔓 !nome_beat <vibe>", value="A IA gera 5 nomes comerciais para sua track/beat.", inline=False)
        e_ia.add_field(name="🔓 !analise_capa", value="Anexe uma imagem para análise técnica de design.", inline=False)
        e_ia.add_field(name="🔓 !ideia", value="A IA gera um desafio criativo aleatório para música ou vídeo.", inline=False)
        e_ia.add_field(name="🔓 !format <título>", value="Anexe um arquivo para postar de forma formatada.", inline=False)
        await guia_channel.send(embed=e_ia)

        e_xp = discord.Embed(title="🌟 Engajamento e Utilidades", color=0xf1c40f)
        e_xp.add_field(name="🔓 !rank / !leaderboard", value="Vê seu nível de XP atual ou o top 10 do servidor.", inline=False)
        e_xp.add_field(name="🔓 !sugestao <texto>", value="Cria uma sugestão no canal de sugestões.", inline=False)
        e_xp.add_field(name="🔓 !poll <perg | op1 | op2>", value="Cria uma enquete com reações numeradas.", inline=False)
        e_xp.add_field(name="🔓 !userinfo / !serverinfo", value="Mostra informações do usuário ou do servidor.", inline=False)
        e_xp.add_field(name="🔓 !avatar @user", value="Mostra a foto de perfil em alta resolução.", inline=False)
        await guia_channel.send(embed=e_xp)

        await ctx.send("✅ Guia de comandos público atualizado no canal <#1374208274668195853>!")

async def setup(bot):
    await bot.add_cog(Admin(bot))
