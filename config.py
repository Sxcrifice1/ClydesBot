import os
import json
import imageio_ffmpeg
from dotenv import load_dotenv

load_dotenv()

# ── Token ──
TOKEN = os.getenv('DISCORD_TOKEN')

# ── FFmpeg ──
FFMPEG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg", "ffmpeg-master-latest-win64-gpl", "bin")
if not os.path.exists(FFMPEG_DIR):
    FFMPEG_DIR = os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())
os.environ["PATH"] = FFMPEG_DIR + os.pathsep + os.environ["PATH"]

# ── IDs de Canais ──
CANAL_BEM_VINDO_ID = 1374208272239689885
CANAL_SELF_ROLES_ID = 1374208272889942140
CANAL_BOOSTS_ID = 1374208272889942143
CANAL_SHOW_EVENTS_ID = 1374208273640849488
MOD_LOG_ID = 1374208276576862273
ADMIN_CATEGORY_ID = 1374208276119425079
COMMUNITY_CATEGORY_ID = 1374208273640849491

# ── Arquivos de Dados ──
KEYS_FILE = 'user_keys.json'
XP_FILE = 'xp_data.json'
SUGESTAO_FILE = 'sugestao_counter.json'
WARNS_FILE = 'warns.json'

# ── Configurações ──
STARBOARD_THRESHOLD = 3

# ── Helpers ──
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return {}

def save_json(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f)
