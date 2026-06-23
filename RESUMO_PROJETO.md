# 🤖 PROJETO BOT CLYDES - STATUS E PROGRESSO

Este documento registra tudo o que já foi implementado no Bot do Discord da comunidade Clydes e o que ficou pendente para as próximas sessões de programação.

## ✅ O QUE JÁ FIZEMOS (CONCLUÍDO)

### 1. Sistema de Servidor e Automação
- **`!criar_cargos`**: O bot gera automaticamente todos os cargos necessários (DAWs, Softwares e Profissões).
- **`!setup`**: Painel visual (menus dropdown) para os usuários escolherem seus cargos e habilidades sozinhos.
- **`!regras`**: Embed oficial das regras do servidor.
- **`!travar_canais`**: Bloqueia o chat nos canais de configuração para evitar que os usuários façam spam nas áreas de regras/setup.
- **Boas-vindas e Boost**: Mensagens automatizadas com a foto do usuário quando ele entra no servidor ou dá Boost.

### 2. Integração com Inteligência Artificial (Google Gemini)
- **`!painel_ia`**: Cria um botão fixo. Quando o usuário clica, o bot cria um **canal de texto 100% privado** exclusivo para ele.
- **Sistema de API Keys Isoladas**: Em vez de o dono do servidor pagar a conta, cada usuário insere sua própria chave grátis do Google. A chave é validada, encriptada, salva em `user_keys.json` e a mensagem é apagada por segurança.
- **Estética e Blindagem**: A IA foi programada para não usar emojis em excesso, responder de forma profissional e negar pedidos de moderação/jailbreak.
- **Auto-Limpeza**: O bot escaneia os canais de IA a cada 1 minuto. Se a sala estiver inativa por 5 minutos, ele deleta o canal para não poluir o servidor.

### 3. Comandos de Criadores (Fase 3)
Esses comandos funcionam de graça dentro da sala de IA de cada membro:
- **`!resumo #canal`** *(Admin)*: A IA lê as últimas conversas de um chat público e faz um resumo direto.
- **`!format <nome>`**: O usuário manda uma foto/áudio sujo no chat, e o bot cria um card profissional lindo e posta automaticamente no canal de Artes.
- **`!ideia`**: A IA gera um desafio criativo aleatório para destravar bloqueios criativos.
- **`!nome_beat <vibe>`**: A IA cria 5 opções de nomes comerciais para músicas baseadas na vibe pedida.
- **`!analise_capa` (IMAGEM)**: O bot visualiza uma imagem e fornece orientações estritamente técnicas de design gráfico (cores, legibilidade, etc), sem dar ideias criativas.

### 4. Sistemas de Portfólio e Collabs (Novo e Interativo)
Foi desenhado um ecossistema completo para fomentar o networking e contratações dentro da comunidade, focado em manter os chats limpos e focados no conteúdo.
- **Painéis Fixos (`!painel_portfolios` e `!painel_collabs`)**: Comandos restritos aos Administradores. Eles invocam um Embed fixo no canal com um botão interativo (`discord.ui.View`). O bot é inteligente: se os canais `#portfolios` ou `#collabs` não existirem no servidor, o bot tem permissão de criá-pará-los e organizar as categorias automaticamente.
- **Formulários Pop-up (Modals)**: Diferente de bots antigos onde o usuário digita comandos enormes, aqui ele clica no botão e o Discord injeta uma janela pop-up na tela (Modal). 
  - Para o **Portfólio**, ele pede: Nome, Link do Trabalho, Especialidade, e Descrição/Serviços.
  - Para o **Collab**, ele pede: Nome do Artista, Proposta da Collab, Estilo Musical, Link de Referência.
- **Estética Automática e Limpeza**: Após o preenchimento e submissão do formulário, o bot pega essas informações e gera um "Cartão Profissional" (Embed) com o logo da Clydes. Os usuários não têm permissão para escrever texto livre nesse canal, apenas interagir com o botão. Isso cria uma vitrine limpa, sem mensagens soltas de "oi", "bom dia" ou spam no meio dos trabalhos.

### 5. Motor de Áudio e Download Universal (A Mágica Complexa)
Construímos do zero um sistema robusto que transforma o bot em uma verdadeira ferramenta de estúdio para os produtores:
- **Radiografia Musical (`!info_audio`)**:
  - O usuário anexa um arquivo (`.mp3`, `.wav` ou `.ogg`) no chat.
  - O bot baixa esse arquivo para o servidor temporalmente.
  - Usamos a biblioteca **`mutagen`** para extrair metadados brutos (Duração exata, Sample Rate em Hz, Bitrate, e mapeamento de Canais Mono/Stereo).
  - Como o `.mp3` é compactado, injetamos uma camada de conversão para transformar o áudio em ondas lineares decodificáveis usando o **FFmpeg**.
  - Após decodificar, a biblioteca de engenharia de áudio **`librosa`** analisa o espectro sonoro (sinal puro):
    - **Algoritmo de Correção Half-Time**: O bot detecta o BPM, mas entende que arquivos curtos (loops menores que 15s) tendem a enganar a IA e mostrar metade do BPM real. O sistema agora dobra o valor matematicamente se o BPM der menor que 90 (ex: 70 vira 140), ou avisa a dualidade (ex: 140 BPM ou 70 half-time).
    - **Chroma STFT**: Ele mapeia a frequência das notas ao longo do tempo e as correlaciona matematicamente com os 12 perfis da escala diatônica (Maior e Menor) para achar o **Tom exato** (ex: D# Menor).
- **Download Sem Fronteiras (`!dl_audio` e `!dl_video`)**:
  - Você envia qualquer link do mundo (YouTube, SoundCloud, TikTok, Reels, Facebook).
  - Usamos o **`yt-dlp`** em conjunto com um runtime JavaScript embutido (**`Deno`**) para burlar e quebrar as proteções das plataformas e extrair os links de CDN diretamente.
  - O código foi blindado com **Geo-Bypass** (burla restrições de país) e **Retry System** (caso a conexão caia, ele tenta de novo silenciosamente).
  - Para áudio, injetamos os binários oficiais do **FFmpeg.exe** e **FFprobe.exe** direto na raiz do projeto. Isso permite que o bot puxe a melhor qualidade possível e converta cirurgicamente o arquivo para `.mp3` a **192kbps**.
  - Para vídeo, o motor junta o melhor arquivo de vídeo sem áudio com o melhor arquivo de áudio puro, mesclando ambos num pacote `.mp4` de alta compressão.
  - **Filtro de Sobrecarga**: O Discord tem um limite estrito de 25MB para arquivos. O bot calcula o tamanho resultante em bytes. Se for maior que 25MB, ele aborta, apaga o arquivo temporário da RAM, e sugere ao usuário que mande um trecho menor (em vez de quebrar e dar erro fatal). Tudo limpo e otimizado.

### 6. Sistemas Rodando em Segundo Plano (Background)
- **AutoMod Rigoroso**: O bot rastreia todas as mensagens de canais normais, usando RegEx para combater táticas de evasão. Ele destrói espaçamentos e caracteres especiais (ex: `N4z1st4`, `n i g g a`) matematicamente. Se der match numa lista negra, a mensagem evapora instantaneamente e o usuário toma um Timeout de 10 minutos para esfriar a cabeça.
- **Desafios Semanais**: Script crontab ativado. Toda sexta-feira às 18h00 cravadas, faça chuva ou faça sol, o bot anuncia um desafio criativo dinâmico no canal de eventos, gerando engajamento contínuo.
- **Process Cleanup**: A arquitetura do bot garante que os arquivos `.mp3`/`.mp4` gerados pela IA ou baixados da web sejam deletados do disco (`os.remove`) logo após a mensagem ser disparada no Discord. Isso significa que o servidor nunca vai encher o HD (Prevenção contra Memory Leak e Disk Full).

---

## 🛠️ PRÓXIMA MISSÃO: O QUE FAREMOS A SEGUIR (ROADMAP)

O bot já é um monstro na infraestrutura e segurança. Na nossa próxima sessão, o foco será em Transformação Musical Contínua e Deploy em Produção:

1. **Rádio Lo-fi 24/7 (`!radio`)**: 
   - A base do comando já foi escrita. Precisaremos pegar o ambiente do FFmpeg (que já está configurado na raiz com sucesso) e ligá-lo diretamente aos "Voice Channels" do Discord (usando o `discord.VoiceClient`).
   - O bot entrará sozinho na call de voz e iniciará um streaming via PCM Audio. 
   - Objetivo: Ficar transmitindo uma stream de rádio infinita em alta qualidade para quem estiver estudando ou produzindo na call.

2. **Fechamento de Pacote e Blindagem**:
   - Atualizar a lista completa de bibliotecas no arquivo `requirements.txt` (ter certeza que pacotes gigantes como `librosa`, `yt-dlp`, `imageio-ffmpeg` e `deno-vm` estão "lockados" na versão correta para evitar que a nuvem tente baixar uma versão bugada).
   - Revisão geral de IDs de Canais de produção (garantir que os IDs das salas do seu servidor final correspondam ao código).

3. **Deploy em Produção (Hospedagem na Discloud)**:
   - Você tem o ambiente da Discloud configurado (arquivo `discloud.config`).
   - Vamos usar o script `delete.js` para derrubar qualquer resíduo antigo que esteja rodando na nuvem.
   - Ziparemos o código fonte atualizado (apenas os arquivos essenciais, removendo caches e pastas pesadas desnecessárias) e faremos o upload.
   - Analisaremos os logs do painel da nuvem para confirmar que o bot ligou, carregou a IA Gemini, alocou a RAM necessária (o `librosa` é pesado) e se conectou na porta de escuta do Discord sem cair.

4. **Expansão de Ideias (Opcional)**:
   - Uma vez na nuvem, podemos afinar permissões ou criar novos módulos se você tiver mais ideias de automação para a comunidade Clydes.
