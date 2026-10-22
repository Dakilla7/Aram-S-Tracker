import base64
import ctypes
import io
import json
import os
import re
import string
import subprocess
import sys
import threading
import time
import traceback
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import urllib3

try:
    from PIL import Image, ImageTk, ImageDraw
    HAS_PIL = True
except Exception:
    HAS_PIL = False

urllib3.disable_warnings()

# ================= VERSION & AUTO-UPDATER SETTINGS =================
APP_VERSION = "1.4.3"
GITHUB_REPO = "Dakilla7/Aram-S-Tracker"
# ===================================================================

APPDATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AramSTracker")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")

# High-DPI Awareness on Windows
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

# ================= COLOR PALETTES / THEMES =================
THEMES = {
    "Hextech": {
        "name": "Hextech Obsidian",
        "bg_root": "#070b12",
        "bg_card": "#0f1726",
        "bg_header": "#0b121e",
        "bg_sub": "#141f33",
        "bg_hover": "#1d2d4a",
        "border": "#1e2e4a",
        "text_primary": "#f1f5f9",
        "text_secondary": "#8a9bb5",
        "accent_primary": "#c8aa6e",     # Hextech Gold
        "accent_secondary": "#0ac8b9",   # Magic Cyan
        "action_btn_bg": "#2563eb",
        "action_btn_hover": "#3b82f6",
        "progress_fill_aram": "#0ac8b9",
        "progress_fill_sr": "#c8aa6e",
        "tag_need_you_bg": "#1a2d48",
        "tag_need_you_fg": "#f1f5f9",
        "tag_done_you_bg": "#121f33",
        "tag_done_you_fg": "#8a9bb5",
        "tag_need_bg": "#0f1726",
        "tag_need_fg": "#f1f5f9",
        "tag_done_bg": "#090d16",
        "tag_done_fg": "#64748b",
        "tag_unavail_bg": "#060910",
        "tag_unavail_fg": "#475569",
    },
    "Onyx": {
        "name": "Stealth Onyx",
        "bg_root": "#0a0b0e",
        "bg_card": "#13141a",
        "bg_header": "#0e0f14",
        "bg_sub": "#1a1c24",
        "bg_hover": "#252833",
        "border": "#222530",
        "text_primary": "#f8fafc",
        "text_secondary": "#94a3b8",
        "accent_primary": "#10b981",     # Neon Emerald
        "accent_secondary": "#34d399",   # Mint
        "action_btn_bg": "#059669",
        "action_btn_hover": "#10b981",
        "progress_fill_aram": "#34d399",
        "progress_fill_sr": "#10b981",
        "tag_need_you_bg": "#142c22",
        "tag_need_you_fg": "#ecfdf5",
        "tag_done_you_bg": "#101d17",
        "tag_done_you_fg": "#6ee7b7",
        "tag_need_bg": "#13141a",
        "tag_need_fg": "#f8fafc",
        "tag_done_bg": "#0e0f14",
        "tag_done_fg": "#64748b",
        "tag_unavail_bg": "#090a0d",
        "tag_unavail_fg": "#475569",
    },
    "Eclipse": {
        "name": "Midnight Eclipse",
        "bg_root": "#0f1015",
        "bg_card": "#181920",
        "bg_header": "#13141a",
        "bg_sub": "#21222b",
        "bg_hover": "#2c2e3a",
        "border": "#282a36",
        "text_primary": "#f1f2f6",
        "text_secondary": "#9fa3af",
        "accent_primary": "#818cf8",     # Indigo
        "accent_secondary": "#f59e0b",   # Warm Amber
        "action_btn_bg": "#6366f1",
        "action_btn_hover": "#4f46e5",
        "progress_fill_aram": "#818cf8",
        "progress_fill_sr": "#f59e0b",
        "tag_need_you_bg": "#23253b",
        "tag_need_you_fg": "#e0e7ff",
        "tag_done_you_bg": "#191a27",
        "tag_done_you_fg": "#a5b4fc",
        "tag_need_bg": "#181920",
        "tag_need_fg": "#f1f2f6",
        "tag_done_bg": "#111217",
        "tag_done_fg": "#6b7280",
        "tag_unavail_bg": "#0c0d11",
        "tag_unavail_fg": "#4b5563",
    },
    "Arcane": {
        "name": "Arcane Void",
        "bg_root": "#090611",
        "bg_card": "#130d22",
        "bg_header": "#0d0918",
        "bg_sub": "#1b1330",
        "bg_hover": "#261a42",
        "border": "#24193d",
        "text_primary": "#f5f3ff",
        "text_secondary": "#a79fc7",
        "accent_primary": "#c084fc",     # Electric Violet
        "accent_secondary": "#00f5d4",   # Chemtech Cyan
        "action_btn_bg": "#9333ea",
        "action_btn_hover": "#a855f7",
        "progress_fill_aram": "#00f5d4",
        "progress_fill_sr": "#c084fc",
        "tag_need_you_bg": "#271642",
        "tag_need_you_fg": "#faf5ff",
        "tag_done_you_bg": "#1c1130",
        "tag_done_you_fg": "#d8b4fe",
        "tag_need_bg": "#130d22",
        "tag_need_fg": "#f5f3ff",
        "tag_done_bg": "#0c0816",
        "tag_done_fg": "#716b8a",
        "tag_unavail_bg": "#07040d",
        "tag_unavail_fg": "#4c4661",
    },
}

# {Champion Name: (ARAM Tier, Primary Role, (Summoner's Rift Lanes...))}
STATIC_DATA = {
    "Aatrox": ("A", "Fighter", ("Top",)),
    "Ahri": ("A", "Mage", ("Mid",)),
    "Akali": ("B", "Assassin", ("Mid", "Top")),
    "Akshan": ("A", "Marksman", ("Mid", "Top")),
    "Alistar": ("S", "Tank", ("Support",)),
    "Ambessa": ("A", "Fighter", ("Top", "Jungle")),
    "Amumu": ("S", "Tank", ("Jungle", "Support")),
    "Anivia": ("S", "Mage", ("Mid", "Support")),
    "Annie": ("A", "Mage", ("Mid", "Support")),
    "Aphelios": ("A", "Marksman", ("Bot",)),
    "Ashe": ("S", "Marksman", ("Bot", "Support")),
    "Aurelion Sol": ("S+", "Mage", ("Mid",)),
    "Aurora": ("A", "Mage", ("Mid", "Top")),
    "Azir": ("A", "Mage", ("Mid",)),
    "Bard": ("B", "Support", ("Support",)),
    "Bel'Veth": ("B", "Fighter", ("Jungle",)),
    "Blitzcrank": ("S", "Tank", ("Support",)),
    "Brand": ("S+", "Mage", ("Support", "Mid", "Jungle")),
    "Braum": ("A", "Support", ("Support",)),
    "Briar": ("B", "Fighter", ("Jungle", "Top")),
    "Caitlyn": ("S", "Marksman", ("Bot",)),
    "Camille": ("B", "Fighter", ("Top", "Support")),
    "Cassiopeia": ("A", "Mage", ("Mid", "Top")),
    "Cho'Gath": ("S", "Tank", ("Top", "Mid")),
    "Corki": ("A", "Marksman", ("Mid", "Bot")),
    "Darius": ("A", "Fighter", ("Top",)),
    "Diana": ("A", "Fighter", ("Jungle", "Mid")),
    "Dr. Mundo": ("S", "Tank", ("Top", "Jungle")),
    "Draven": ("B", "Marksman", ("Bot",)),
    "Ekko": ("A", "Assassin", ("Jungle", "Mid")),
    "Elise": ("B", "Mage", ("Jungle", "Support")),
    "Evelynn": ("C", "Assassin", ("Jungle",)),
    "Ezreal": ("S", "Marksman", ("Bot", "Mid")),
    "Fiddlesticks": ("S", "Mage", ("Jungle", "Support")),
    "Fiora": ("C", "Fighter", ("Top",)),
    "Fizz": ("B", "Assassin", ("Mid",)),
    "Galio": ("A", "Tank", ("Mid", "Support")),
    "Gangplank": ("A", "Fighter", ("Top", "Mid")),
    "Garen": ("A", "Fighter", ("Top", "Mid")),
    "Gnar": ("A", "Fighter", ("Top",)),
    "Gragas": ("S", "Fighter", ("Top", "Jungle", "Mid")),
    "Graves": ("A", "Marksman", ("Jungle",)),
    "Gwen": ("A", "Fighter", ("Top", "Jungle")),
    "Hecarim": ("A", "Fighter", ("Jungle",)),
    "Heimerdinger": ("S", "Mage", ("Mid", "Top", "Support")),
    "Hwei": ("S+", "Mage", ("Mid", "Support", "Bot")),
    "Illaoi": ("S", "Fighter", ("Top",)),
    "Irelia": ("B", "Fighter", ("Top", "Mid")),
    "Ivern": ("B", "Support", ("Jungle", "Support")),
    "Janna": ("A", "Support", ("Support",)),
    "Jarvan IV": ("A", "Tank", ("Jungle",)),
    "Jax": ("A", "Fighter", ("Top", "Jungle")),
    "Jayce": ("S", "Fighter", ("Top", "Mid")),
    "Jhin": ("S+", "Marksman", ("Bot",)),
    "Jinx": ("S+", "Marksman", ("Bot",)),
    "K'Sante": ("A", "Tank", ("Top",)),
    "Kai'Sa": ("S", "Marksman", ("Bot", "Mid")),
    "Kalista": ("B", "Marksman", ("Bot",)),
    "Karma": ("S", "Mage", ("Support", "Mid", "Top")),
    "Karthus": ("S+", "Mage", ("Jungle", "Bot", "Mid")),
    "Kassadin": ("A", "Assassin", ("Mid",)),
    "Katarina": ("A", "Assassin", ("Mid",)),
    "Kayle": ("A", "Fighter", ("Top", "Mid")),
    "Kayn": ("A", "Fighter", ("Jungle",)),
    "Kennen": ("S", "Mage", ("Top", "Mid")),
    "Kha'Zix": ("B", "Assassin", ("Jungle",)),
    "Kindred": ("B", "Marksman", ("Jungle",)),
    "Kled": ("A", "Fighter", ("Top",)),
    "Kog'Maw": ("S", "Marksman", ("Bot", "Mid")),
    "LeBlanc": ("B", "Assassin", ("Mid",)),
    "Lee Sin": ("A", "Fighter", ("Jungle",)),
    "Leona": ("S", "Tank", ("Support",)),
    "Lillia": ("S", "Fighter", ("Jungle", "Top")),
    "Lissandra": ("S", "Mage", ("Mid",)),
    "Lucian": ("A", "Marksman", ("Bot", "Mid")),
    "Lulu": ("A", "Support", ("Support",)),
    "Lux": ("S+", "Mage", ("Support", "Mid")),
    "Malphite": ("S", "Tank", ("Top", "Mid", "Support")),
    "Malzahar": ("A", "Mage", ("Mid",)),
    "Maokai": ("S+", "Tank", ("Support", "Jungle", "Top")),
    "Master Yi": ("A", "Assassin", ("Jungle",)),
    "Mel": ("A", "Mage", ("Mid", "Support")),
    "Milio": ("A", "Support", ("Support",)),
    "Miss Fortune": ("S+", "Marksman", ("Bot",)),
    "Mordekaiser": ("A", "Fighter", ("Top", "Jungle")),
    "Morgana": ("S", "Mage", ("Support", "Mid", "Jungle")),
    "Naafiri": ("A", "Assassin", ("Mid", "Jungle")),
    "Nami": ("A", "Support", ("Support",)),
    "Nasus": ("A", "Fighter", ("Top",)),
    "Nautilus": ("S", "Tank", ("Support",)),
    "Neeko": ("A", "Mage", ("Mid", "Support")),
    "Nidalee": ("A", "Mage", ("Jungle",)),
    "Nilah": ("A", "Fighter", ("Bot",)),
    "Nocturne": ("B", "Assassin", ("Jungle",)),
    "Nunu & Willump": ("A", "Tank", ("Jungle",)),
    "Olaf": ("A", "Fighter", ("Top", "Jungle")),
    "Orianna": ("S", "Mage", ("Mid",)),
    "Ornn": ("S", "Tank", ("Top",)),
    "Pantheon": ("A", "Fighter", ("Support", "Mid", "Top", "Jungle")),
    "Poppy": ("A", "Tank", ("Top", "Jungle", "Support")),
    "Pyke": ("S", "Support", ("Support",)),
    "Qiyana": ("B", "Assassin", ("Mid", "Jungle")),
    "Quinn": ("C", "Marksman", ("Top", "Mid")),
    "Rakan": ("A", "Support", ("Support",)),
    "Rammus": ("A", "Tank", ("Jungle",)),
    "Rek'Sai": ("B", "Fighter", ("Jungle",)),
    "Rell": ("S", "Tank", ("Support",)),
    "Renata Glasc": ("S", "Support", ("Support",)),
    "Renekton": ("B", "Fighter", ("Top",)),
    "Rengar": ("B", "Assassin", ("Jungle", "Top")),
    "Riven": ("B", "Fighter", ("Top",)),
    "Rumble": ("S", "Fighter", ("Top", "Mid")),
    "Ryze": ("A", "Mage", ("Mid", "Top")),
    "Samira": ("S", "Marksman", ("Bot",)),
    "Sejuani": ("A", "Tank", ("Jungle", "Top")),
    "Senna": ("S+", "Marksman", ("Support", "Bot")),
    "Seraphine": ("S+", "Mage", ("Support", "Bot", "Mid")),
    "Sett": ("S", "Fighter", ("Top", "Support")),
    "Shaco": ("B", "Assassin", ("Jungle", "Support")),
    "Shen": ("A", "Tank", ("Top", "Support")),
    "Shyvana": ("A", "Fighter", ("Jungle",)),
    "Singed": ("A", "Tank", ("Top",)),
    "Sion": ("S", "Tank", ("Top",)),
    "Sivir": ("S", "Marksman", ("Bot",)),
    "Skarner": ("A", "Tank", ("Jungle", "Top")),
    "Smolder": ("S+", "Marksman", ("Bot", "Mid", "Top")),
    "Sona": ("S+", "Support", ("Support",)),
    "Soraka": ("S", "Support", ("Support",)),
    "Swain": ("S", "Mage", ("Support", "Mid", "Bot")),
    "Sylas": ("A", "Mage", ("Mid", "Top", "Jungle")),
    "Syndra": ("A", "Mage", ("Mid",)),
    "Tahm Kench": ("A", "Tank", ("Top", "Support")),
    "Taliyah": ("A", "Mage", ("Mid", "Jungle")),
    "Talon": ("B", "Assassin", ("Mid", "Jungle")),
    "Taric": ("S", "Support", ("Support",)),
    "Teemo": ("S+", "Marksman", ("Top", "Jungle", "Support")),
    "Thresh": ("S", "Support", ("Support",)),
    "Tristana": ("A", "Marksman", ("Bot", "Mid")),
    "Trundle": ("A", "Fighter", ("Top", "Jungle")),
    "Tryndamere": ("B", "Fighter", ("Top",)),
    "Twisted Fate": ("A", "Mage", ("Mid", "Bot")),
    "Twitch": ("S", "Marksman", ("Bot", "Support")),
    "Udyr": ("A", "Fighter", ("Jungle", "Top")),
    "Urgot": ("A", "Fighter", ("Top",)),
    "Varus": ("S+", "Marksman", ("Bot", "Mid")),
    "Vayne": ("A", "Marksman", ("Bot", "Top")),
    "Veigar": ("S+", "Mage", ("Mid", "Bot", "Support")),
    "Vel'Koz": ("S", "Mage", ("Support", "Mid")),
    "Vex": ("A", "Mage", ("Mid",)),
    "Vi": ("A", "Fighter", ("Jungle",)),
    "Viego": ("A", "Assassin", ("Jungle",)),
    "Viktor": ("S", "Mage", ("Mid",)),
    "Vladimir": ("A", "Mage", ("Mid", "Top")),
    "Volibear": ("A", "Fighter", ("Top", "Jungle")),
    "Warwick": ("B", "Fighter", ("Jungle", "Top")),
    "Wukong": ("S", "Fighter", ("Jungle", "Top")),
    "Xayah": ("A", "Marksman", ("Bot",)),
    "Xerath": ("S+", "Mage", ("Support", "Mid")),
    "Xin Zhao": ("A", "Fighter", ("Jungle",)),
    "Yasuo": ("A", "Fighter", ("Mid", "Top", "Bot")),
    "Yone": ("A", "Fighter", ("Mid", "Top")),
    "Yorick": ("B", "Fighter", ("Top",)),
    "Yuumi": ("A", "Support", ("Support",)),
    "Zac": ("S", "Tank", ("Jungle", "Top", "Support")),
    "Zed": ("B", "Assassin", ("Mid", "Jungle")),
    "Zeri": ("A", "Marksman", ("Bot",)),
    "Ziggs": ("S+", "Mage", ("Bot", "Mid")),
    "Zilean": ("A", "Support", ("Support", "Mid")),
    "Zoe": ("A", "Mage", ("Mid", "Support")),
    "Zyra": ("S", "Mage", ("Support", "Jungle")),
}

ROLE_FALLBACK_LANES = {
    "Fighter": ("Top", "Jungle"),
    "Tank": ("Top", "Jungle", "Support"),
    "Mage": ("Mid", "Support"),
    "Assassin": ("Mid", "Jungle"),
    "Marksman": ("Bot",),
    "Support": ("Support",),
}

POSITION_MAP = {
    "top": "Top",
    "jungle": "Jungle",
    "middle": "Mid",
    "mid": "Mid",
    "bottom": "Bot",
    "bot": "Bot",
    "adc": "Bot",
    "utility": "Support",
    "support": "Support",
}

LANE_SHORT_BADGE = {
    "Top": "[TOP]",
    "Jungle": "[JG]",
    "Mid": "[MID]",
    "Bot": "[BOT]",
    "Support": "[SUP]",
}

TIER_ORDER = {"S+": 0, "S": 1, "A": 2, "B": 3, "C": 4, "": 5}
ICON_SIZE = (30, 30)

STANDARD_TIER_PTS = [
    ("IRON", "Iron", 5),
    ("BRONZE", "Bronze", 10),
    ("SILVER", "Silver", 15),
    ("GOLD", "Gold", 25),
    ("PLATINUM", "Platinum", 40),
    ("DIAMOND", "Diamond", 60),
    ("MASTER", "Master", 100),
]

DEFAULT_MILESTONES = [
    (1, "Iron", 5),
    (5, "Bronze", 10),
    (15, "Silver", 15),
    (30, "Gold", 25),
    (50, "Platinum", 40),
    (100, "Diamond", 60),
    (150, "Master", 100),
]

# Milestone Tier Colors: (text, background, border)
TIER_COLORS = {
    "IRON": ("#a19d94", "#24201c", "#3d372e"),
    "BRONZE": ("#cd7f32", "#2a1c12", "#4a2d1a"),
    "SILVER": ("#cbd5e1", "#1e2633", "#334155"),
    "GOLD": ("#fbbf24", "#31230c", "#634714"),
    "PLATINUM": ("#2dd4bf", "#0d2b27", "#134e48"),
    "DIAMOND": ("#60a5fa", "#172540", "#1e3a8a"),
    "MASTER": ("#c084fc", "#2e1247", "#581c87"),
    "UNRANKED": ("#94a3b8", "#182337", "#223354"),
}


def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def save_config_value(key, val):
    try:
        os.makedirs(APPDATA_DIR, exist_ok=True)
        data = load_config()
        data[key] = val
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def load_saved_lol_dir():
    return load_config().get("lol_dir", "")


def save_lol_dir(lol_dir):
    save_config_value("lol_dir", lol_dir)


def get_riot_metadata_lockfile():
    program_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
    yaml_path = os.path.join(
        program_data, "Riot Games", "Metadata", "league_of_legends.live",
        "league_of_legends.live.product_settings.yaml"
    )
    if os.path.exists(yaml_path):
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                content = f.read()
            match = re.search(r'product_install_full_path:\s*["\']?([^"\'\r\n]+)["\']?', content)
            if match:
                install_dir = os.path.normpath(match.group(1).strip())
                return os.path.join(install_dir, "lockfile")
        except Exception:
            pass
    return ""


def find_lockfile():
    candidates = []
    saved_dir = load_saved_lol_dir()
    if saved_dir:
        candidates.append(os.path.join(saved_dir, "lockfile"))
    if os.environ.get("LOL_LOCKFILE"):
        candidates.append(os.environ["LOL_LOCKFILE"])
    meta_lockfile = get_riot_metadata_lockfile()
    if meta_lockfile:
        candidates.append(meta_lockfile)
    for drive in string.ascii_uppercase:
        if os.path.exists(f"{drive}:\\"):
            candidates.append(f"{drive}:\\Riot Games\\League of Legends\\lockfile")
            candidates.append(f"{drive}:\\Games\\Riot Games\\League of Legends\\lockfile")

    for path in candidates:
        if path and os.path.exists(path):
            return path
    return None


def lcu_client():
    lockfile = find_lockfile()
    if not lockfile:
        raise FileNotFoundError("League client lockfile not found.")
    with open(lockfile, encoding="utf-8") as f:
        _, _, port, password, proto = f.read().strip().split(":")
    base = f"{proto}://127.0.0.1:{port}"
    auth = base64.b64encode(f"riot:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {auth}"}

    def get_json(path):
        r = requests.get(base + path, headers=headers, verify=False, timeout=8)
        r.raise_for_status()
        return r.json()

    def get_bytes(path):
        r = requests.get(base + path, headers=headers, verify=False, timeout=8)
        r.raise_for_status()
        return r.content

    def post_req(path, json_body=None):
        r = requests.post(base + path, headers=headers, json=json_body, verify=False, timeout=5)
        r.raise_for_status()
        return r

    def patch_req(path, json_body=None):
        r = requests.patch(base + path, headers=headers, json=json_body, verify=False, timeout=5)
        r.raise_for_status()
        return r

    return get_json, get_bytes, post_req, patch_req


def cleanup_old_exe():
    if getattr(sys, "frozen", False):
        old_exe = sys.executable + ".old"
        if os.path.exists(old_exe):
            try:
                os.remove(old_exe)
            except Exception:
                pass


def parse_version(v_str):
    return tuple(int(x) for x in re.findall(r"\d+", str(v_str)))


# ================= MODERN CUSTOM WIDGETS =================

class HextechProgressBar(tk.Canvas):
    """Sleek custom canvas progress bar with rounded ends and crisp track."""
    def __init__(self, parent, width=320, height=10, bg="#101726",
                 track_color="#182337", fill_color="#c8aa6e", border_color="#223354", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, bd=0, **kwargs)
        self.track_color = track_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.progress = 0.0
        self.bind("<Configure>", lambda e: self.draw())

    def set_progress(self, current, total):
        self.progress = (current / total) if total > 0 else 0.0
        self.progress = max(0.0, min(1.0, self.progress))
        self.draw()

    def apply_theme(self, bg, track_color, border_color, fill_color):
        self.configure(bg=bg)
        self.track_color = track_color
        self.border_color = border_color
        self.fill_color = fill_color
        self.draw()

    def draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w < 10 or h < 4:
            return

        r = h // 2
        # Track background
        self.create_rectangle(r, 0, w - r, h, fill=self.track_color, outline=self.border_color, width=1)
        self.create_oval(0, 0, 2 * r, h, fill=self.track_color, outline=self.border_color, width=1)
        self.create_oval(w - 2 * r, 0, w, h, fill=self.track_color, outline=self.border_color, width=1)
        self.create_rectangle(r, 1, w - r, h - 1, fill=self.track_color, outline="")

        # Fill progress
        fill_w = int(w * self.progress)
        if fill_w > 2:
            fill_w = min(w, fill_w)
            if fill_w >= 2 * r:
                self.create_oval(0, 1, 2 * r, h - 1, fill=self.fill_color, outline="")
                self.create_rectangle(r, 1, fill_w - (r if fill_w < w else 0), h - 1, fill=self.fill_color, outline="")
                if fill_w >= w - r:
                    self.create_oval(w - 2 * r, 1, w, h - 1, fill=self.fill_color, outline="")
            else:
                self.create_rectangle(1, 1, fill_w, h - 1, fill=self.fill_color, outline="")


class SegmentedControl(tk.Frame):
    """Modern flat segmented control for selecting game modes, roles, or filters."""
    def __init__(self, parent, options, variable, command=None,
                 bg="#0c1322", active_bg="#1a2d4b", active_fg="#c8aa6e",
                 normal_bg="#141d30", normal_fg="#8a9bb5", hover_bg="#1e2e4a",
                 border_color="#223354", font=("Segoe UI", 8, "bold"),
                 padx=10, pady=4, **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.options = options
        self.variable = variable
        self.command = command
        self.active_bg = active_bg
        self.active_fg = active_fg
        self.normal_bg = normal_bg
        self.normal_fg = normal_fg
        self.hover_bg = hover_bg
        self.border_color = border_color
        self.btn_font = font
        self.btn_padx = padx
        self.btn_pady = pady
        self.labels = {}

        self.inner = tk.Frame(self, bg=border_color, bd=1)
        self.inner.pack(fill="both", expand=True)

        for val, text in options:
            lbl = tk.Label(
                self.inner, text=text, font=self.btn_font,
                padx=self.btn_padx, pady=self.btn_pady, cursor="hand2"
            )
            lbl.pack(side="left", padx=1, pady=1)
            lbl.bind("<Button-1>", lambda e, v=val: self._on_click(v))
            lbl.bind("<Enter>", lambda e, l=lbl, v=val: self._on_enter(l, v))
            lbl.bind("<Leave>", lambda e, l=lbl, v=val: self._on_leave(l, v))
            self.labels[val] = lbl

        self.variable.trace_add("write", lambda *_: self.refresh())
        self.refresh()

    def _on_click(self, val):
        if self.variable.get() != val:
            self.variable.set(val)
            if self.command:
                self.command()

    def _on_enter(self, lbl, val):
        if self.variable.get() != val:
            lbl.config(bg=self.hover_bg, fg="#e2e8f0")

    def _on_leave(self, lbl, val):
        if self.variable.get() != val:
            lbl.config(bg=self.normal_bg, fg=self.normal_fg)

    def set_label_text(self, val, new_text):
        if val in self.labels:
            self.labels[val].config(text=new_text)

    def apply_theme(self, bg, active_bg, active_fg, normal_bg, normal_fg, hover_bg, border_color):
        self.configure(bg=bg)
        self.inner.configure(bg=border_color)
        self.active_bg = active_bg
        self.active_fg = active_fg
        self.normal_bg = normal_bg
        self.normal_fg = normal_fg
        self.hover_bg = hover_bg
        self.border_color = border_color
        self.refresh()

    def refresh(self):
        cur = self.variable.get()
        for val, lbl in self.labels.items():
            if val == cur:
                lbl.config(bg=self.active_bg, fg=self.active_fg)
            else:
                lbl.config(bg=self.normal_bg, fg=self.normal_fg)


# ================= MAIN APPLICATION CLASS =================

class AramTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"LoL Challenge S-Grade Tracker v{APP_VERSION}")
        self.root.geometry("1080x720")
        self.root.minsize(980, 640)

        self.current_theme = load_config().get("theme", "Onyx")
        if self.current_theme not in THEMES:
            self.current_theme = "Onyx"

        t = THEMES[self.current_theme]
        self.root.configure(bg=t["bg_root"])

        cleanup_old_exe()

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(f"aram.stracker.app.{APP_VERSION}")
        except Exception:
            pass
        try:
            if getattr(sys, "frozen", False):
                self.root.iconbitmap(sys.executable)
            elif os.path.exists("coolcat.ico"):
                self.root.iconbitmap("coolcat.ico")
        except Exception:
            pass

        self.champs = {}
        self.id_to_name = {}
        self.raw_icons = {}
        self.tk_icons = {}
        self.summoner_cache = {}
        self.team_lobby = []
        self.bench_lobby = []
        self.banned_ids = set()
        self.row_actions = {}

        # Active challenge mode: "ARAM" (All Random All Champions S-) or "SR" (Perfectionist S+)
        self.active_mode = tk.StringVar(value="ARAM")
        self.detected_queue_label = ""
        self.assigned_lane = ""

        # SR right-panel filter controls
        self.sr_lane_var = tk.StringVar(value="Auto")
        self.sr_search_var = tk.StringVar()
        self.sr_need_only_var = tk.BooleanVar(value=False)

        self.milestones_by_mode = {
            "ARAM": list(DEFAULT_MILESTONES),
            "SR": list(DEFAULT_MILESTONES),
        }

        self.update_download_url = None
        self.latest_version = None
        self.always_on_top = tk.BooleanVar(value=False)
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")

        self._setup_styles()
        self._build_ui()
        self._apply_theme(self.current_theme, save_to_config=False)

        threading.Thread(target=self._poll_loop, daemon=True).start()
        threading.Thread(target=self._check_for_updates, daemon=True).start()

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use("clam")

        t = THEMES[self.current_theme]

        # Polished modern dark tabs
        self.style.configure("TNotebook", background=t["bg_root"], borderwidth=0)
        self.style.configure("TNotebook.Tab", background=t["bg_card"], foreground=t["text_secondary"],
                             padding=[18, 8], font=("Segoe UI", 9, "bold"), borderwidth=0)
        self.style.map("TNotebook.Tab",
                       background=[("selected", t["bg_hover"]), ("active", t["bg_sub"])],
                       foreground=[("selected", t["accent_secondary"]), ("active", t["text_primary"])])

        # Modern high-density treeview with 38px rows
        self.style.configure("Treeview",
                             background=t["bg_card"],
                             foreground=t["text_primary"],
                             fieldbackground=t["bg_card"],
                             rowheight=38,
                             borderwidth=0,
                             font=("Segoe UI", 9))
        self.style.configure("Treeview.Heading",
                             background=t["bg_header"],
                             foreground=t["accent_primary"],
                             font=("Segoe UI", 9, "bold"),
                             padding=[6, 6],
                             relief="flat")
        self.style.map("Treeview.Heading",
                       background=[("active", t["bg_sub"])],
                       foreground=[("active", t["text_primary"])])
        self.style.map("Treeview",
                       background=[("selected", t["bg_hover"])],
                       foreground=[("selected", "#ffffff")])

    def _build_ui(self):
        t = THEMES[self.current_theme]

        # ================= 1. TOP HEADER / APP BAR =================
        self.header_container = tk.Frame(self.root, bg=t["border"], bd=1)
        self.header_container.pack(fill="x", padx=10, pady=(10, 4))

        self.header_nav = tk.Frame(self.header_container, bg=t["bg_header"], padx=14, pady=8)
        self.header_nav.pack(fill="x")

        # Left Column: Branding, Version, and Live Connection Status
        self.brand_col = tk.Frame(self.header_nav, bg=t["bg_header"])
        self.brand_col.pack(side="left", fill="y")

        self.brand_row = tk.Frame(self.brand_col, bg=t["bg_header"])
        self.brand_row.pack(anchor="w")

        self.title_lbl = tk.Label(
            self.brand_row, text="CHALLENGE S-TRACKER",
            fg=t["accent_primary"], bg=t["bg_header"], font=("Segoe UI", 12, "bold")
        )
        self.title_lbl.pack(side="left")

        self.version_pill = tk.Label(
            self.brand_row, text=f"v{APP_VERSION}",
            fg=t["text_secondary"], bg=t["bg_sub"], font=("Segoe UI", 8, "bold"), padx=6, pady=1
        )
        self.version_pill.pack(side="left", padx=(8, 0))

        self.status_row = tk.Frame(self.brand_col, bg=t["bg_header"])
        self.status_row.pack(anchor="w", pady=(3, 0))

        self.status_dot = tk.Label(self.status_row, text="○", fg="#fbbf24", bg=t["bg_header"], font=("Segoe UI", 9, "bold"))
        self.status_dot.pack(side="left", padx=(0, 4))

        self.status_lbl = tk.Label(
            self.status_row, text="Waiting for League client...",
            fg="#fbbf24", bg=t["bg_header"], font=("Segoe UI", 8)
        )
        self.status_lbl.pack(side="left")

        # Center: Segmented Game Mode Switcher
        self.mode_frame = tk.Frame(self.header_nav, bg=t["bg_header"])
        self.mode_frame.pack(side="left", expand=True)

        self.mode_selector = SegmentedControl(
            self.mode_frame,
            options=[("ARAM", "ARAM • S-"), ("SR", "RIFT • S+ PERFECTIONIST")],
            variable=self.active_mode,
            command=self._on_mode_changed,
            bg=t["bg_header"],
            active_bg=t["bg_hover"],
            active_fg=t["accent_primary"],
            normal_bg=t["bg_sub"],
            normal_fg=t["text_secondary"],
            hover_bg=t["bg_hover"],
            border_color=t["border"],
            font=("Segoe UI", 9, "bold"),
            padx=14, pady=5
        )
        self.mode_selector.pack()

        # Right: Quick Window Controls (Pin, Theme, Set Folder, Update)
        self.controls_col = tk.Frame(self.header_nav, bg=t["bg_header"])
        self.controls_col.pack(side="right", fill="y")

        self.pin_btn = tk.Button(
            self.controls_col, text="PIN", command=self._toggle_pin,
            bg=t["bg_sub"], fg=t["text_secondary"], activebackground=t["bg_hover"], activeforeground=t["text_primary"],
            relief="flat", bd=0, padx=8, pady=3, font=("Segoe UI", 8, "bold"), cursor="hand2"
        )
        self.pin_btn.pack(side="right", padx=(4, 0))

        self.theme_btn = tk.Button(
            self.controls_col, text="Theme ▾", command=self._open_theme_menu,
            bg=t["bg_sub"], fg=t["text_secondary"], activebackground=t["bg_hover"], activeforeground=t["text_primary"],
            relief="flat", bd=0, padx=8, pady=3, font=("Segoe UI", 8, "bold"), cursor="hand2"
        )
        self.theme_btn.pack(side="right", padx=(4, 0))

        self.folder_btn = tk.Button(
            self.controls_col, text="LoL Folder", command=self._choose_lol_folder,
            bg=t["bg_sub"], fg=t["text_secondary"], activebackground=t["bg_hover"], activeforeground=t["text_primary"],
            relief="flat", bd=0, padx=8, pady=3, font=("Segoe UI", 8, "bold"), cursor="hand2"
        )
        self.folder_btn.pack(side="right", padx=(4, 0))

        self.update_btn = tk.Button(
            self.controls_col, text="Update Available", command=self._perform_self_update,
            bg="#15803d", fg="#ffffff", activebackground="#16a34a", activeforeground="#ffffff",
            relief="flat", bd=0, padx=8, pady=3, font=("Segoe UI", 8, "bold"), cursor="hand2"
        )

        # ================= 2. HERO MILESTONE & PROGRESS CARD =================
        self.milestone_card = tk.Frame(self.root, bg=t["border"], bd=1)
        self.milestone_card.pack(fill="x", padx=10, pady=(2, 6))

        self.m_inner = tk.Frame(self.milestone_card, bg=t["bg_card"], padx=14, pady=8)
        self.m_inner.pack(fill="x")

        # Left Column: Milestone Rank Tier Badge
        self.tier_col = tk.Frame(self.m_inner, bg=t["bg_card"])
        self.tier_col.pack(side="left", padx=(0, 16))

        self.milestone_tier_frame = tk.Frame(self.tier_col, bg=t["border"], bd=1)
        self.milestone_tier_frame.pack(side="left")

        self.milestone_tier_lbl = tk.Label(
            self.milestone_tier_frame, text="UNRANKED",
            fg=t["text_secondary"], bg=t["bg_sub"], font=("Segoe UI", 9, "bold"), padx=10, pady=3
        )
        self.milestone_tier_lbl.pack(side="left")

        self.milestone_pts_lbl = tk.Label(
            self.tier_col, text="0 PTS",
            fg=t["accent_primary"], bg=t["bg_card"], font=("Segoe UI", 9, "bold"), padx=8
        )
        self.milestone_pts_lbl.pack(side="left")

        # Center Column: Progress Counts & Hextech Canvas Progress Bar
        self.center_col = tk.Frame(self.m_inner, bg=t["bg_card"])
        self.center_col.pack(side="left", fill="x", expand=True)

        self.progress_text_row = tk.Frame(self.center_col, bg=t["bg_card"])
        self.progress_text_row.pack(fill="x")

        self.progress_count_lbl = tk.Label(
            self.progress_text_row, text="0 / 0 Champions Completed",
            fg=t["text_primary"], bg=t["bg_card"], font=("Segoe UI", 9, "bold")
        )
        self.progress_count_lbl.pack(side="left")

        self.progress_pct_lbl = tk.Label(
            self.progress_text_row, text="0.0%",
            fg=t["accent_secondary"], bg=t["bg_card"], font=("Segoe UI", 9, "bold")
        )
        self.progress_pct_lbl.pack(side="right")

        self.hextech_progress = HextechProgressBar(
            self.center_col, width=380, height=10,
            bg=t["bg_card"], track_color=t["bg_sub"], fill_color=t["progress_fill_sr"], border_color=t["border"]
        )
        self.hextech_progress.pack(fill="x", pady=(4, 0))

        # Right Column: Target Milestone & Remaining Summary
        self.target_col = tk.Frame(self.m_inner, bg=t["bg_card"])
        self.target_col.pack(side="right", padx=(16, 0))

        self.needed_summary_lbl = tk.Label(
            self.target_col, text="0 Need Grade",
            fg="#f59e0b", bg=t["bg_card"], font=("Segoe UI", 9, "bold")
        )
        self.needed_summary_lbl.pack(anchor="e")

        self.next_milestone_lbl = tk.Label(
            self.target_col, text="Loading milestone...",
            fg=t["text_secondary"], bg=t["bg_card"], font=("Segoe UI", 8)
        )
        self.next_milestone_lbl.pack(anchor="e", pady=(2, 0))

        # ================= 3. NOTEBOOK (TABS) =================
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(2, 6))

        # ================= TAB 1: SPLIT LIVE LOBBY =================
        self.tab_lobby = tk.Frame(self.notebook, bg=t["bg_root"])
        self.notebook.add(self.tab_lobby, text="Live Lobby (0)")

        self.top_bar_container = tk.Frame(self.tab_lobby, bg=t["border"], bd=1)
        self.top_bar_container.pack(fill="x", padx=6, pady=6)

        self.top_bar = tk.Frame(self.top_bar_container, bg=t["bg_card"], padx=12, pady=6)
        self.top_bar.pack(fill="x")

        self.lobby_banner = tk.Label(
            self.top_bar,
            text="Waiting for Champ Select  •  Enter a game lobby to scan live champions automatically",
            fg=t["text_secondary"], bg=t["bg_card"], font=("Segoe UI", 9)
        )
        self.lobby_banner.pack(side="left")

        self.action_btn = tk.Button(
            self.top_bar, text="QUICK ACTION (DOUBLE-CLICK)",
            command=self._on_button_action,
            bg=t["action_btn_bg"], fg="#ffffff", activebackground=t["action_btn_hover"], activeforeground="#ffffff",
            relief="flat", bd=0, padx=14, pady=4, font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        self.action_btn.pack(side="right")
        self.action_btn.bind("<Enter>", lambda e: self.action_btn.config(bg=THEMES[self.current_theme]["action_btn_hover"]))
        self.action_btn.bind("<Leave>", lambda e: self.action_btn.config(bg=THEMES[self.current_theme]["action_btn_bg"]))

        self.split_pane = tk.PanedWindow(
            self.tab_lobby, orient="horizontal", bg=t["bg_root"],
            sashwidth=6, sashrelief="flat", bd=0
        )
        self.split_pane.pack(fill="both", expand=True, padx=6, pady=(0, 4))

        # --- LEFT PANEL: YOUR TEAM ---
        self.left_frame = tk.Frame(self.split_pane, bg=t["border"], bd=1)
        self.team_header_lbl = tk.Label(
            self.left_frame, text="YOUR TEAM (0)  •  Double-Click to Trade",
            bg=t["bg_header"], fg=t["accent_primary"], font=("Segoe UI", 9, "bold"), pady=7, anchor="w", padx=10
        )
        self.team_header_lbl.pack(fill="x")

        team_cols = ("player", "status", "tier")
        self.team_tree = ttk.Treeview(self.left_frame, columns=team_cols, show="tree headings")
        self._configure_team_columns(self.team_tree)
        self.team_tree.pack(fill="both", expand=True)
        self.team_tree.bind("<Double-1>", lambda _e: self._trigger_tree_action(self.team_tree))
        self.team_tree.bind("<<TreeviewSelect>>", lambda _e: self._clear_other_selection(self.bench_tree))

        # --- RIGHT PANEL: REROLL BENCH (ARAM) OR LANE POOL (SR) ---
        self.right_frame = tk.Frame(self.split_pane, bg=t["border"], bd=1)
        self.bench_header_lbl = tk.Label(
            self.right_frame, text="REROLL BENCH (0)  •  Double-Click to Grab",
            bg=t["bg_header"], fg=t["accent_secondary"], font=("Segoe UI", 9, "bold"), pady=7, anchor="w", padx=10
        )
        self.bench_header_lbl.pack(fill="x")

        # Summoner's Rift Lane Filter Bar
        self.sr_filter_frame = tk.Frame(self.right_frame, bg=t["bg_card"], padx=8, pady=5)

        self.lane_row = tk.Frame(self.sr_filter_frame, bg=t["bg_card"])
        self.lane_row.pack(fill="x")

        self.lane_selector = SegmentedControl(
            self.lane_row,
            options=[
                ("Auto", "AUTO"),
                ("Top", "TOP"),
                ("Jungle", "JG"),
                ("Mid", "MID"),
                ("Bot", "BOT"),
                ("Support", "SUP"),
                ("All", "ALL"),
            ],
            variable=self.sr_lane_var,
            command=self._refresh_lobby_trees,
            bg=t["bg_card"],
            active_bg=t["accent_secondary"],
            active_fg=t["bg_root"],
            normal_bg=t["bg_sub"],
            normal_fg=t["text_secondary"],
            hover_bg=t["bg_hover"],
            border_color=t["border"],
            font=("Segoe UI", 8, "bold"),
            padx=8, pady=3
        )
        self.lane_selector.pack(side="left")

        self.search_row = tk.Frame(self.sr_filter_frame, bg=t["bg_card"], pady=4)
        self.search_row.pack(fill="x")

        self.search_box = tk.Frame(self.search_row, bg=t["border"], bd=1)
        self.search_box.pack(side="left", padx=(0, 8))

        self.search_box_lbl = tk.Label(self.search_box, text="SEARCH:", fg=t["text_secondary"], bg=t["bg_sub"], font=("Segoe UI", 8, "bold"), padx=6)
        self.search_box_lbl.pack(side="left")
        self.sr_search_entry = tk.Entry(
            self.search_box, textvariable=self.sr_search_var,
            bg=t["bg_sub"], fg=t["text_primary"], insertbackground=t["text_primary"],
            relief="flat", bd=0, font=("Segoe UI", 9), width=16
        )
        self.sr_search_entry.pack(side="left", padx=4, ipady=3)
        self.sr_search_var.trace_add("write", lambda *_: self._refresh_lobby_trees())

        self.need_only_btn = tk.Button(
            self.search_row, text="NEED S+ ONLY",
            command=self._toggle_need_only,
            bg=t["bg_sub"], fg=t["text_secondary"], activebackground=t["bg_hover"], activeforeground=t["text_primary"],
            relief="flat", bd=0, padx=8, pady=3, font=("Segoe UI", 8, "bold"), cursor="hand2"
        )
        self.need_only_btn.pack(side="left")

        self.bench_tree_container = tk.Frame(self.right_frame, bg=t["bg_card"])
        self.bench_tree_container.pack(fill="both", expand=True)

        bench_cols = ("status", "tier", "role")
        self.bench_tree = ttk.Treeview(self.bench_tree_container, columns=bench_cols, show="tree headings")
        self._configure_bench_columns(self.bench_tree)
        bench_scroll = ttk.Scrollbar(self.bench_tree_container, orient="vertical", command=self.bench_tree.yview)
        self.bench_tree.configure(yscrollcommand=bench_scroll.set)

        self.bench_tree.pack(side="left", fill="both", expand=True)
        bench_scroll.pack(side="right", fill="y")

        self.bench_tree.bind("<Double-1>", lambda _e: self._trigger_tree_action(self.bench_tree))
        self.bench_tree.bind("<<TreeviewSelect>>", lambda _e: self._clear_other_selection(self.team_tree))

        self.split_pane.add(self.left_frame, minsize=420, width=540)
        self.split_pane.add(self.right_frame, minsize=380, width=490)

        # ================= TAB 2: ALL CHAMPIONS CATALOG =================
        self.tab_all = tk.Frame(self.notebook, bg=t["bg_root"])
        self.notebook.add(self.tab_all, text="Champion Catalog (0)")

        self.filter_bar_container = tk.Frame(self.tab_all, bg=t["border"], bd=1)
        self.filter_bar_container.pack(fill="x", padx=6, pady=6)

        self.filter_bar = tk.Frame(self.filter_bar_container, bg=t["bg_card"], padx=12, pady=6)
        self.filter_bar.pack(fill="x")

        self.search_box_all = tk.Frame(self.filter_bar, bg=t["border"], bd=1)
        self.search_box_all.pack(side="left", padx=(0, 12))

        self.search_box_all_lbl = tk.Label(self.search_box_all, text="SEARCH:", fg=t["text_secondary"], bg=t["bg_sub"], font=("Segoe UI", 8, "bold"), padx=6)
        self.search_box_all_lbl.pack(side="left")
        self.search_entry = tk.Entry(
            self.search_box_all, textvariable=self.search_var,
            bg=t["bg_sub"], fg=t["text_primary"], insertbackground=t["text_primary"],
            relief="flat", bd=0, font=("Segoe UI", 9), width=22
        )
        self.search_entry.pack(side="left", padx=4, ipady=3)
        self.search_var.trace_add("write", lambda *_: self._refresh_all_tree())

        self.catalog_filter = SegmentedControl(
            self.filter_bar,
            options=[
                ("All", "ALL CHAMPIONS"),
                ("Need", "NEED GRADE"),
                ("Completed", "COMPLETED"),
            ],
            variable=self.filter_var,
            command=self._refresh_all_tree,
            bg=t["bg_card"],
            active_bg=t["bg_hover"],
            active_fg=t["accent_primary"],
            normal_bg=t["bg_sub"],
            normal_fg=t["text_secondary"],
            hover_bg=t["bg_hover"],
            border_color=t["border"],
            font=("Segoe UI", 8, "bold"),
            padx=10, pady=4
        )
        self.catalog_filter.pack(side="left")

        self.tree_frame = tk.Frame(self.tab_all, bg=t["border"], bd=1)
        self.tree_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        all_cols = ("status", "tier", "role")
        self.all_tree = ttk.Treeview(self.tree_frame, columns=all_cols, show="tree headings")
        self._configure_all_columns(self.all_tree)
        scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.all_tree.yview)
        self.all_tree.configure(yscrollcommand=scrollbar.set)

        self.all_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _open_theme_menu(self):
        t = THEMES[self.current_theme]
        menu = tk.Menu(
            self.root, tearoff=0,
            bg=t["bg_sub"], fg=t["text_primary"],
            activebackground=t["action_btn_bg"], activeforeground="#ffffff",
            font=("Segoe UI", 9)
        )
        for key, data in THEMES.items():
            prefix = "●  " if self.current_theme == key else "    "
            menu.add_command(
                label=f"{prefix}{data['name']}",
                command=lambda k=key: self._apply_theme(k)
            )
        try:
            x = self.theme_btn.winfo_rootx()
            y = self.theme_btn.winfo_rooty() + self.theme_btn.winfo_height() + 2
            menu.post(x, y)
        except Exception:
            pass

    def _apply_theme(self, theme_key, save_to_config=True):
        if theme_key not in THEMES:
            return
        self.current_theme = theme_key
        if save_to_config:
            save_config_value("theme", theme_key)

        t = THEMES[theme_key]
        self.theme_btn.config(text=f"Theme: {t['name'].split()[0]} ▾")

        # Root and Containers
        self.root.configure(bg=t["bg_root"])
        self.header_container.configure(bg=t["border"])
        self.header_nav.configure(bg=t["bg_header"])
        self.brand_col.configure(bg=t["bg_header"])
        self.brand_row.configure(bg=t["bg_header"])
        self.status_row.configure(bg=t["bg_header"])
        self.title_lbl.configure(fg=t["accent_primary"], bg=t["bg_header"])
        self.version_pill.configure(fg=t["text_secondary"], bg=t["bg_sub"])
        self.status_dot.configure(bg=t["bg_header"])
        self.status_lbl.configure(bg=t["bg_header"])
        self.mode_frame.configure(bg=t["bg_header"])
        self.controls_col.configure(bg=t["bg_header"])

        # Control Buttons
        self.pin_btn.configure(
            bg=t["bg_hover"] if self.always_on_top.get() else t["bg_sub"],
            fg=t["accent_secondary"] if self.always_on_top.get() else t["text_secondary"],
            activebackground=t["bg_hover"], activeforeground=t["text_primary"]
        )
        self.theme_btn.configure(bg=t["bg_sub"], fg=t["text_secondary"], activebackground=t["bg_hover"], activeforeground=t["text_primary"])
        self.folder_btn.configure(bg=t["bg_sub"], fg=t["text_secondary"], activebackground=t["bg_hover"], activeforeground=t["text_primary"])

        # Milestone Card
        self.milestone_card.configure(bg=t["border"])
        self.m_inner.configure(bg=t["bg_card"])
        self.tier_col.configure(bg=t["bg_card"])
        self.milestone_tier_frame.configure(bg=t["border"])
        self.milestone_pts_lbl.configure(bg=t["bg_card"])
        self.center_col.configure(bg=t["bg_card"])
        self.progress_text_row.configure(bg=t["bg_card"])
        self.progress_count_lbl.configure(fg=t["text_primary"], bg=t["bg_card"])
        self.target_col.configure(bg=t["bg_card"])
        self.next_milestone_lbl.configure(fg=t["text_secondary"], bg=t["bg_card"])

        # Tabs & Lobby Elements
        self.tab_lobby.configure(bg=t["bg_root"])
        self.top_bar_container.configure(bg=t["border"])
        self.top_bar.configure(bg=t["bg_card"])
        self.lobby_banner.configure(bg=t["bg_card"])
        self.action_btn.configure(bg=t["action_btn_bg"], activebackground=t["action_btn_hover"])
        self.split_pane.configure(bg=t["bg_root"])
        self.left_frame.configure(bg=t["border"])
        self.right_frame.configure(bg=t["border"])
        self.team_header_lbl.configure(bg=t["bg_header"], fg=t["accent_primary"])
        self.bench_header_lbl.configure(bg=t["bg_header"], fg=t["accent_secondary"])
        self.sr_filter_frame.configure(bg=t["bg_card"])
        self.lane_row.configure(bg=t["bg_card"])
        self.search_row.configure(bg=t["bg_card"])
        self.search_box.configure(bg=t["border"])
        self.search_box_lbl.configure(bg=t["bg_sub"], fg=t["text_secondary"])
        self.sr_search_entry.configure(bg=t["bg_sub"], fg=t["text_primary"], insertbackground=t["text_primary"])
        self.bench_tree_container.configure(bg=t["bg_card"])

        # Tab 2 Elements
        self.tab_all.configure(bg=t["bg_root"])
        self.filter_bar_container.configure(bg=t["border"])
        self.filter_bar.configure(bg=t["bg_card"])
        self.search_box_all.configure(bg=t["border"])
        self.search_box_all_lbl.configure(bg=t["bg_sub"], fg=t["text_secondary"])
        self.search_entry.configure(bg=t["bg_sub"], fg=t["text_primary"], insertbackground=t["text_primary"])
        self.tree_frame.configure(bg=t["border"])

        # Segmented Controls
        self.mode_selector.apply_theme(
            bg=t["bg_header"], active_bg=t["bg_hover"], active_fg=t["accent_primary"],
            normal_bg=t["bg_sub"], normal_fg=t["text_secondary"],
            hover_bg=t["bg_hover"], border_color=t["border"]
        )
        self.lane_selector.apply_theme(
            bg=t["bg_card"], active_bg=t["accent_secondary"], active_fg=t["bg_root"],
            normal_bg=t["bg_sub"], normal_fg=t["text_secondary"],
            hover_bg=t["bg_hover"], border_color=t["border"]
        )
        self.catalog_filter.apply_theme(
            bg=t["bg_card"], active_bg=t["bg_hover"], active_fg=t["accent_primary"],
            normal_bg=t["bg_sub"], normal_fg=t["text_secondary"],
            hover_bg=t["bg_hover"], border_color=t["border"]
        )

        # TTK Styles
        self.style.configure("TNotebook", background=t["bg_root"])
        self.style.configure("TNotebook.Tab", background=t["bg_card"], foreground=t["text_secondary"])
        self.style.map("TNotebook.Tab",
                       background=[("selected", t["bg_hover"]), ("active", t["bg_sub"])],
                       foreground=[("selected", t["accent_secondary"]), ("active", t["text_primary"])])

        self.style.configure("Treeview",
                             background=t["bg_card"],
                             foreground=t["text_primary"],
                             fieldbackground=t["bg_card"])
        self.style.configure("Treeview.Heading",
                             background=t["bg_header"],
                             foreground=t["accent_primary"])
        self.style.map("Treeview",
                       background=[("selected", t["bg_hover"])])

        # Treeview Row Tags
        self.team_tree.tag_configure("need_you", background=t["tag_need_you_bg"], foreground=t["tag_need_you_fg"])
        self.team_tree.tag_configure("done_you", background=t["tag_done_you_bg"], foreground=t["tag_done_you_fg"])
        self.team_tree.tag_configure("need", background=t["tag_need_bg"], foreground=t["tag_need_fg"])
        self.team_tree.tag_configure("done", background=t["tag_done_bg"], foreground=t["tag_done_fg"])

        self.bench_tree.tag_configure("need", background=t["tag_need_bg"], foreground=t["tag_need_fg"])
        self.bench_tree.tag_configure("done", background=t["tag_done_bg"], foreground=t["tag_done_fg"])
        self.bench_tree.tag_configure("unavailable", background=t["tag_unavail_bg"], foreground=t["tag_unavail_fg"])

        self.all_tree.tag_configure("need", background=t["tag_need_bg"], foreground=t["tag_need_fg"])
        self.all_tree.tag_configure("done", background=t["tag_done_bg"], foreground=t["tag_done_fg"])

        # Progress Bar
        fill_col = t["progress_fill_sr"] if self.active_mode.get() == "SR" else t["progress_fill_aram"]
        self.hextech_progress.apply_theme(
            bg=t["bg_card"], track_color=t["bg_sub"], border_color=t["border"], fill_color=fill_col
        )
        self.progress_pct_lbl.config(fg=fill_col)

    def _toggle_pin(self):
        val = not self.always_on_top.get()
        self.always_on_top.set(val)
        self.root.attributes("-topmost", val)
        t = THEMES[self.current_theme]
        if val:
            self.pin_btn.config(text="PIN: ON", bg=t["bg_hover"], fg=t["accent_secondary"])
        else:
            self.pin_btn.config(text="PIN", bg=t["bg_sub"], fg=t["text_secondary"])

    def _toggle_need_only(self):
        val = not self.sr_need_only_var.get()
        self.sr_need_only_var.set(val)
        t = THEMES[self.current_theme]
        if val:
            self.need_only_btn.config(bg=t["bg_hover"], fg=t["accent_secondary"])
        else:
            self.need_only_btn.config(bg=t["bg_sub"], fg=t["text_secondary"])
        self._refresh_lobby_trees()

    def _set_connection_status(self, is_connected, message):
        t = THEMES[self.current_theme]
        if is_connected:
            self.status_dot.config(text="●", fg=t["accent_secondary"])
            self.status_lbl.config(text=message, fg=t["accent_secondary"])
        else:
            self.status_dot.config(text="○", fg="#fbbf24")
            self.status_lbl.config(text=message, fg="#fbbf24")

    def _is_champ_done(self, info):
        if self.active_mode.get() == "SR":
            return info.get("done_sr", False)
        return info.get("done_aram", False)

    def _status_labels(self):
        if self.active_mode.get() == "SR":
            return "S+ EARNED", "NEED S+"
        return "S EARNED", "NEED S"

    def _get_effective_sr_lane(self):
        choice = self.sr_lane_var.get()
        if choice == "Auto":
            return self.assigned_lane or "All"
        return choice

    def _on_mode_changed(self):
        self._update_dashboard()

    def _clear_other_selection(self, other_tree):
        if other_tree.selection():
            other_tree.selection_remove(other_tree.selection())

    def _choose_lol_folder(self):
        folder = filedialog.askdirectory(title="Select your 'League of Legends' folder")
        if folder:
            save_lol_dir(folder)
            self._set_connection_status(False, f"Saved folder: {folder}")

    def _check_for_updates(self):
        if "/" not in GITHUB_REPO or "YOUR_GITHUB" in GITHUB_REPO:
            return
        try:
            url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
            r = requests.get(url, timeout=8)
            if r.status_code != 200:
                return
            data = r.json()
            tag = data.get("tag_name", "")
            if parse_version(tag) > parse_version(APP_VERSION):
                for asset in data.get("assets", []):
                    if asset.get("name", "").lower().endswith(".exe"):
                        self.update_download_url = asset.get("browser_download_url")
                        self.latest_version = tag
                        self.root.after(0, lambda: self.update_btn.config(text=f"Update to {tag}"))
                        self.root.after(0, lambda: self.update_btn.pack(side="right", padx=(0, 6)))
                        break
        except Exception:
            pass

    def _perform_self_update(self):
        if not getattr(sys, "frozen", False):
            messagebox.showinfo("Updater", "Self-update only runs inside the compiled .exe!")
            return
        if not self.update_download_url:
            return

        self.update_btn.config(text="Downloading...", state="disabled")

        def download_and_swap():
            try:
                r = requests.get(self.update_download_url, timeout=60)
                r.raise_for_status()

                cur_exe = sys.executable
                old_exe = cur_exe + ".old"
                if os.path.exists(old_exe):
                    os.remove(old_exe)

                os.rename(cur_exe, old_exe)
                with open(cur_exe, "wb") as f:
                    f.write(r.content)

                clean_env = {
                    k: v for k, v in os.environ.items()
                    if not k.startswith("_PYI") and k not in ("_MEIPASS2", "TCL_LIBRARY", "TK_LIBRARY")
                }
                clean_env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"

                subprocess.Popen(
                    [cur_exe],
                    env=clean_env,
                    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                )
                self.root.after(0, self.root.destroy)
            except Exception as e:
                self.root.after(0, lambda err=str(e): messagebox.showerror("Update Failed", err))
                self.root.after(0, lambda: self.update_btn.config(text="Retry Update", state="normal"))

        threading.Thread(target=download_and_swap, daemon=True).start()

    def _configure_team_columns(self, tree):
        tree.heading("#0", text="CHAMPION & ACTION", anchor="w")
        tree.column("#0", width=175, minwidth=130, anchor="w", stretch=True)

        tree.heading("player", text="PLAYER (RIOT ID)", anchor="w")
        tree.heading("status", text="STATUS", anchor="center")
        tree.heading("tier", text="TIER", anchor="center")

        tree.column("player", width=150, minwidth=110, anchor="w", stretch=True)
        tree.column("status", width=95, minwidth=85, anchor="center", stretch=False)
        tree.column("tier", width=50, minwidth=45, anchor="center", stretch=False)

    def _configure_bench_columns(self, tree):
        tree.heading("#0", text="CHAMPION", anchor="w")
        tree.column("#0", width=165, minwidth=120, anchor="w", stretch=True)

        tree.heading("status", text="STATUS", anchor="center")
        tree.heading("tier", text="TIER", anchor="center")
        tree.heading("role", text="LANES / ROLE", anchor="center")

        tree.column("status", width=95, minwidth=85, anchor="center", stretch=False)
        tree.column("tier", width=50, minwidth=45, anchor="center", stretch=False)
        tree.column("role", width=125, minwidth=100, anchor="center", stretch=False)

    def _configure_all_columns(self, tree):
        tree.heading("#0", text="CHAMPION", anchor="w")
        tree.column("#0", width=240, anchor="w", stretch=True)

        tree.heading("status", text="STATUS", anchor="center")
        tree.heading("tier", text="ARAM TIER", anchor="center")
        tree.heading("role", text="SR LANES & ROLE", anchor="center")

        tree.column("status", width=150, anchor="center", stretch=False)
        tree.column("tier", width=100, anchor="center", stretch=False)
        tree.column("role", width=200, anchor="center", stretch=False)

    def _get_tk_icon(self, name):
        if name in self.tk_icons:
            return self.tk_icons[name]
        raw = self.raw_icons.get(name)
        if not raw:
            return ""
        try:
            if HAS_PIL:
                pil_img = Image.open(io.BytesIO(raw)).convert("RGBA")
                resample = getattr(Image, "Resampling", Image).LANCZOS
                pil_img = pil_img.resize(ICON_SIZE, resample)
                try:
                    draw = ImageDraw.Draw(pil_img)
                    draw.rectangle([0, 0, ICON_SIZE[0] - 1, ICON_SIZE[1] - 1], outline=(30, 46, 74, 255))
                except Exception:
                    pass
                tk_img = ImageTk.PhotoImage(pil_img)
            else:
                full_img = tk.PhotoImage(data=base64.b64encode(raw))
                scale = max(1, full_img.width() // 30)
                tk_img = full_img.subsample(scale, scale)
            self.tk_icons[name] = tk_img
            return tk_img
        except Exception:
            return ""

    def _on_button_action(self):
        if self.bench_tree.selection():
            self._trigger_tree_action(self.bench_tree)
        elif self.team_tree.selection():
            self._trigger_tree_action(self.team_tree)

    def _hover_sr_champion(self, get_json, patch_req, cid, champ_name):
        session = get_json("/lol-champ-select/v1/session")
        local_cell = session.get("localPlayerCellId", -1)

        target_action_id = None
        for action_group in session.get("actions", []):
            for act in action_group:
                if act.get("actorCellId") == local_cell and act.get("type") == "pick" and not act.get("completed"):
                    target_action_id = act.get("id")
                    if act.get("isInProgress"):
                        break
            if target_action_id is not None:
                break

        if target_action_id is not None:
            patch_req(f"/lol-champ-select/v1/session/actions/{target_action_id}", {"championId": cid})
            return f"Hovered {champ_name} in Champ Select!"

        patch_req("/lol-champ-select/v1/session/my-selection", {"championId": cid})
        return f"Selected {champ_name}!"

    def _trigger_tree_action(self, tree):
        sel = tree.selection()
        if not sel:
            return
        entry = self.row_actions.get(sel[0])
        if not entry:
            return

        action = entry.get("action")
        cid = entry.get("cid")
        tid = entry.get("tid")
        champ_name = entry.get("champ", "Champion")

        if action == "self":
            self._set_connection_status(True, f"You already have {champ_name}!")
            return
        if not action:
            self._set_connection_status(True, f"Cannot trade or swap {champ_name} right now.")
            return

        def run_action():
            try:
                get_json, _, post_req, patch_req = lcu_client()
                if action == "bench" and cid:
                    post_req(f"/lol-champ-select/v1/session/bench/swap/{cid}")
                    msg = f"Grabbed {champ_name} from the bench!"
                elif action == "sr_hover" and cid:
                    msg = self._hover_sr_champion(get_json, patch_req, cid, champ_name)
                elif action == "trade_acc" and tid is not None:
                    post_req(f"/lol-champ-select/v1/session/champion-swaps/{tid}/accept")
                    msg = f"Accepted trade for {champ_name}!"
                elif action == "trade_req" and tid is not None:
                    post_req(f"/lol-champ-select/v1/session/champion-swaps/{tid}/request")
                    msg = f"Sent trade request for {champ_name}!"
                else:
                    msg = f"Action unavailable for {champ_name}."
                self.root.after(0, lambda m=msg: self._set_connection_status(True, m))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self._set_connection_status(False, f"Action failed: {err[:45]}"))

        threading.Thread(target=run_action, daemon=True).start()

    def _resolve_player_name(self, m, is_me, slot_idx, get_json):
        gname = (m.get("gameName") or "").strip()
        tagline = (m.get("tagLine") or "").strip()
        dname = (m.get("displayName") or "").strip()

        name_str = f"{gname}#{tagline}" if (gname and tagline) else (gname or dname)

        sum_id = m.get("summonerId", 0)
        puuid = (m.get("puuid") or "").strip()
        cache_key = sum_id if (sum_id and sum_id > 0) else puuid

        if not name_str and cache_key:
            if cache_key in self.summoner_cache:
                name_str = self.summoner_cache[cache_key]
            else:
                try:
                    if sum_id and sum_id > 0:
                        s_data = get_json(f"/lol-summoner/v1/summoners/{sum_id}")
                    elif puuid:
                        s_data = get_json(f"/lol-summoner/v2/summoners/puuid/{puuid}")
                    else:
                        s_data = {}
                    gn = (s_data.get("gameName") or "").strip()
                    tl = (s_data.get("tagLine") or "").strip()
                    dn = (s_data.get("displayName") or s_data.get("internalName") or "").strip()
                    name_str = f"{gn}#{tl}" if (gn and tl) else (gn or dn)
                    if name_str:
                        self.summoner_cache[cache_key] = name_str
                except Exception:
                    pass

        raw_pos = (m.get("assignedPosition") or "").strip().lower()
        mapped_lane = POSITION_MAP.get(raw_pos, "")
        lane_badge = f" {LANE_SHORT_BADGE[mapped_lane]}" if mapped_lane in LANE_SHORT_BADGE else ""

        if is_me:
            base = f"{name_str} [YOU]" if name_str else "You [YOU]"
            return f"{base}{lane_badge}"
        base = name_str if name_str else f"Teammate {slot_idx}"
        return f"{base}{lane_badge}"

    def _extract_standard_milestones(self, c_obj):
        thresholds = c_obj.get("thresholds")
        if not isinstance(thresholds, dict):
            return None
        parsed = []
        for api_tier, label, pts in STANDARD_TIER_PTS:
            t_info = thresholds.get(api_tier)
            val = 0
            if isinstance(t_info, (int, float)):
                val = int(t_info)
            elif isinstance(t_info, dict):
                val = int(t_info.get("value", 0))
            if val > 0:
                parsed.append((val, label, pts))
        return parsed if parsed else None

    def _fetch_all_data(self, get_json):
        summary = [c for c in get_json("/lol-game-data/assets/v1/champion-summary.json") if c["id"] > 0]
        challenges = get_json("/lol-challenges/v1/challenges/local-player")

        aram_done_ids = set()
        sr_done_ids = set()

        for cid_key, c in challenges.items():
            cname = c.get("name", "").strip().lower()
            cid_int = c.get("id") or (int(cid_key) if str(cid_key).isdigit() else 0)

            if cid_int == 101301 or "all random all champions" in cname:
                aram_done_ids.update(c.get("completedIds", []))
                if cid_int == 101301 or cname == "all random all champions":
                    ms = self._extract_standard_milestones(c)
                    if ms:
                        self.milestones_by_mode["ARAM"] = ms

            if cid_int == 210001 or cname == "perfectionist":
                sr_done_ids.update(c.get("completedIds", []))
                ms = self._extract_standard_milestones(c)
                if ms:
                    self.milestones_by_mode["SR"] = ms

        champs = {}
        id_to_name = {}

        for c in summary:
            cid = c["id"]
            name = c["name"]
            done_aram = cid in aram_done_ids
            done_sr = cid in sr_done_ids

            static_entry = STATIC_DATA.get(name)
            if static_entry:
                tier, static_role, lanes = static_entry
            else:
                tier, static_role, lanes = "", "", ()

            role = static_role or ((c.get("roles") or [""])[0]).capitalize()
            if not lanes:
                lanes = ROLE_FALLBACK_LANES.get(role, ("Top", "Mid"))

            icon_path = c.get("squarePortraitPath") or f"/lol-game-data/assets/v1/champion-icons/{cid}.png"

            id_to_name[cid] = name
            if name not in champs:
                champs[name] = {
                    "id": cid,
                    "done_aram": done_aram,
                    "done_sr": done_sr,
                    "tier": tier,
                    "role": role,
                    "lanes": lanes,
                    "icon_path": icon_path
                }
            else:
                champs[name]["done_aram"] = champs[name]["done_aram"] or done_aram
                champs[name]["done_sr"] = champs[name]["done_sr"] or done_sr

        return champs, id_to_name

    def _load_missing_icons(self, get_bytes):
        loaded_new = False
        for name, info in list(self.champs.items()):
            if name not in self.raw_icons and info.get("icon_path"):
                try:
                    self.raw_icons[name] = get_bytes(info["icon_path"])
                    loaded_new = True
                except Exception:
                    pass
        if loaded_new:
            self.root.after(0, self._refresh_all_tree)
            self.root.after(0, self._refresh_lobby_trees)

    def _detect_queue_and_lane(self, get_json, cs_session=None):
        detected_mode = None
        q_label = ""
        lane = ""

        # 1. Champ select assignedPosition
        if cs_session is not None:
            local_cell = cs_session.get("localPlayerCellId", -1)
            for m in cs_session.get("myTeam", []):
                if m.get("cellId") == local_cell:
                    raw_pos = (m.get("assignedPosition") or "").strip().lower()
                    lane = POSITION_MAP.get(raw_pos, "")
                    break

        # 2. Gameflow session
        try:
            gf = get_json("/lol-gameflow/v1/session")
            gdata = gf.get("gameData", {})
            q = gdata.get("queue", {})
            map_id = q.get("mapId") or gf.get("map", {}).get("id")
            gmode = (q.get("gameMode") or gf.get("map", {}).get("gameMode") or "").upper()
            qdesc = (q.get("description") or q.get("shortName") or gmode).strip()

            if map_id == 12 or "ARAM" in gmode or "ARAM" in qdesc.upper() or "MAYHEM" in qdesc.upper():
                detected_mode, q_label = "ARAM", (qdesc or "ARAM")
            elif map_id == 11 or gmode in ("CLASSIC", "SWIFTPLAY"):
                detected_mode, q_label = "SR", (qdesc or "Summoner's Rift")
        except Exception:
            pass

        # 3. Pre-Game Lobby
        try:
            lob = get_json("/lol-lobby/v2/lobby")
            gcfg = lob.get("gameConfig", {})
            map_id = gcfg.get("mapId")
            gmode = (gcfg.get("gameMode") or "").upper()
            if not detected_mode:
                if map_id == 12 or "ARAM" in gmode or "KIWI" in gmode:
                    detected_mode, q_label = "ARAM", "ARAM Lobby"
                elif map_id == 11 or gmode in ("CLASSIC", "SWIFTPLAY"):
                    detected_mode, q_label = "SR", "Summoner's Rift Lobby"

            if not lane:
                local_member = lob.get("localMember", {})
                pref1 = (local_member.get("firstPositionPreference") or "").strip().lower()
                lane = POSITION_MAP.get(pref1, "")
        except Exception:
            pass

        # 4. Fallback to Champ Select benchEnabled
        if not detected_mode and cs_session is not None:
            if cs_session.get("benchEnabled", False):
                detected_mode, q_label = "ARAM", "ARAM"
            else:
                detected_mode, q_label = "SR", "Summoner's Rift"

        return detected_mode, q_label, lane

    def _fetch_lobby(self, get_json):
        session = None
        try:
            session = get_json("/lol-champ-select/v1/session")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code != 404:
                raise
        except Exception:
            pass

        detected_mode, q_label, detected_lane = self._detect_queue_and_lane(get_json, session)
        ui_needs_update = False

        if detected_mode and detected_mode != self.active_mode.get():
            self.active_mode.set(detected_mode)
            ui_needs_update = True
        if q_label != self.detected_queue_label:
            self.detected_queue_label = q_label
            ui_needs_update = True
        if detected_lane != self.assigned_lane:
            self.assigned_lane = detected_lane
            ui_needs_update = True

        if ui_needs_update:
            self.root.after(0, self._update_dashboard)

        if not session:
            return None, None, set()

        local_cell = session.get("localPlayerCellId", -1)
        swaps_list = session.get("championSwaps") or session.get("trades", [])
        cell_trades = {t.get("cellId"): t for t in swaps_list}

        banned_ids = set()
        bans_obj = session.get("bans", {})
        for b_list in (bans_obj.get("myTeamBans", []), bans_obj.get("theirTeamBans", [])):
            for cid in b_list:
                if cid and cid > 0:
                    banned_ids.add(cid)
        for action_group in session.get("actions", []):
            for act in action_group:
                if act.get("type") == "ban" and act.get("completed"):
                    cid = act.get("championId", 0)
                    if cid > 0:
                        banned_ids.add(cid)

        team_list = []
        for idx, m in enumerate(session.get("myTeam", []), start=1):
            cell_id = m.get("cellId")
            is_me = (cell_id == local_cell)
            player_name = self._resolve_player_name(m, is_me, idx, get_json)

            cid = m.get("championId", 0)
            intent = m.get("championPickIntent", 0)
            active_id = cid if cid in self.id_to_name else (intent if intent in self.id_to_name else 0)
            if not active_id:
                continue

            champ_name = self.id_to_name[active_id]
            is_hover = (cid == 0 and intent > 0)
            display_champ = f"{champ_name} (Hover)" if is_hover else champ_name

            trade_info = cell_trades.get(cell_id, {})
            tid = trade_info.get("id")
            tstate = trade_info.get("state", "")

            if is_me:
                act = "self"
            else:
                if tstate == "RECEIVED":
                    display_champ = f"{display_champ}   [ACCEPT TRADE]"
                    act = "trade_acc"
                elif tstate == "SENT":
                    display_champ = f"{display_champ}   [REQUEST SENT]"
                    act = None
                elif tstate == "AVAILABLE" and tid is not None:
                    display_champ = f"{display_champ}   [TRADE]"
                    act = "trade_req"
                else:
                    act = None

            team_list.append({
                "champ": champ_name,
                "display_champ": display_champ,
                "player": player_name,
                "action": act,
                "cid": active_id,
                "tid": tid,
                "is_me": is_me
            })

        bench_ids = []
        for b in session.get("benchChampions", []):
            cid = b.get("championId", 0)
            if cid in self.id_to_name and cid not in bench_ids:
                bench_ids.append(cid)
        for cid in session.get("benchChampionIds", []):
            if cid in self.id_to_name and cid not in bench_ids:
                bench_ids.append(cid)

        bench_list = [
            {
                "champ": self.id_to_name[cid],
                "action": "bench",
                "cid": cid,
                "tid": None
            }
            for cid in bench_ids
        ]

        return team_list, bench_list, banned_ids

    def _poll_loop(self):
        last_sync = 0
        last_state = None

        while True:
            try:
                get_json, get_bytes, _, _ = lcu_client()
                now = time.time()

                if now - last_sync >= 30 or not self.champs:
                    champs, id_map = self._fetch_all_data(get_json)
                    self.champs = champs
                    self.id_to_name = id_map
                    last_sync = now
                    self.root.after(0, self._update_dashboard)

                    if len(self.raw_icons) < len(self.champs):
                        self._load_missing_icons(get_bytes)

                if self.id_to_name:
                    team_list, bench_list, banned_ids = self._fetch_lobby(get_json)
                    cur_state = (team_list, bench_list, banned_ids, self.active_mode.get(), self.assigned_lane)
                    if cur_state != last_state:
                        self.team_lobby = team_list or []
                        self.bench_lobby = bench_list or []
                        self.banned_ids = banned_ids or set()
                        last_state = cur_state
                        self.root.after(0, self._refresh_lobby_trees)

            except FileNotFoundError:
                self.root.after(0, lambda: self._set_connection_status(
                    False, "Waiting for League client... (or click 'LoL Folder')"))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self._set_connection_status(
                    False, f"Client loading ({err[:35]})"))

            time.sleep(0.8)

    def _update_dashboard(self):
        mode = self.active_mode.get()
        t = THEMES[self.current_theme]
        total = len(self.champs)
        done = sum(1 for v in self.champs.values() if self._is_champ_done(v))
        rem = total - done
        pct = (done / total * 100) if total else 0

        grade_short = "S+" if mode == "SR" else "S-"

        # Update Lane selector Auto label
        auto_txt = f"AUTO ({self.assigned_lane.upper()})" if self.assigned_lane else "AUTO"
        self.lane_selector.set_label_text("Auto", auto_txt)

        # Update Connection & Queue status
        q_suffix = f"  •  Queue: {self.detected_queue_label}" if self.detected_queue_label else ""
        lane_suffix = f" ({self.assigned_lane})" if (mode == "SR" and self.assigned_lane) else ""
        self._set_connection_status(True, f"Connected to League Client{q_suffix}{lane_suffix}")

        # Update Milestone calculations
        milestones = self.milestones_by_mode.get(mode, DEFAULT_MILESTONES)
        cur_tier, cur_pts = "Unranked", 0
        next_target, next_tier, next_pts = None, None, None

        for req_count, tier_name, pts in milestones:
            if done >= req_count:
                cur_tier, cur_pts = tier_name, pts
            elif next_target is None:
                next_target, next_tier, next_pts = req_count, tier_name, pts

        tier_key = cur_tier.upper()
        fg_col, bg_col, border_col = TIER_COLORS.get(tier_key, TIER_COLORS["UNRANKED"])
        self.milestone_tier_lbl.config(text=tier_key, fg=fg_col, bg=bg_col)
        self.milestone_tier_frame.config(bg=border_col)
        self.milestone_pts_lbl.config(text=f"{cur_pts} PTS", fg=t["accent_primary"])

        # Update Progress Bar & Hero Card
        fill_col = t["progress_fill_sr"] if mode == "SR" else t["progress_fill_aram"]
        self.hextech_progress.fill_color = fill_col
        self.hextech_progress.set_progress(done, total)

        self.progress_count_lbl.config(text=f"{done} / {total} Champions Completed", fg=t["text_primary"])
        self.progress_pct_lbl.config(text=f"{pct:.1f}%", fg=fill_col)
        self.needed_summary_lbl.config(text=f"{rem} Need {grade_short}")

        if next_target is not None:
            needed = next_target - done
            diff_pts = next_pts - cur_pts
            self.next_milestone_lbl.config(
                text=f"Next: {next_tier} ({next_pts} pts, +{diff_pts}) in {needed} champs ({done}/{next_target})",
                fg=t["text_secondary"]
            )
        else:
            self.next_milestone_lbl.config(
                text=f"Max Milestone Reached! ({rem} left for 100%)",
                fg=t["text_secondary"]
            )

        self.notebook.tab(1, text=f"Champion Catalog ({total})")
        self._refresh_all_tree()
        self._refresh_lobby_trees()

    def _refresh_lobby_trees(self):
        self.team_tree.delete(*self.team_tree.get_children())
        self.bench_tree.delete(*self.bench_tree.get_children())
        self.row_actions.clear()

        done_lbl, need_lbl = self._status_labels()
        mode = self.active_mode.get()
        t = THEMES[self.current_theme]
        mode_tag = "SR Perfectionist (S+)" if mode == "SR" else "ARAM (S-)"

        if mode == "SR":
            self.sr_filter_frame.pack(fill="x", before=self.bench_tree.master)
        else:
            self.sr_filter_frame.pack_forget()

        # 1. Populate Left Tree: Your Team
        need_team = 0
        my_champ_summary = ""
        picked_champ_names = set()

        sorted_team = sorted(self.team_lobby, key=lambda x: (not x["is_me"]))
        for item in sorted_team:
            name = item["champ"]
            picked_champ_names.add(name)
            info = self.champs.get(name, {"done_aram": False, "done_sr": False, "tier": "", "role": ""})
            is_done = self._is_champ_done(info)
            if not is_done:
                need_team += 1

            status_txt = done_lbl if is_done else need_lbl
            if item["is_me"]:
                tag = "done_you" if is_done else "need_you"
                my_champ_summary = f"Your Pick: {name} [{status_txt}]  •  "
            else:
                tag = "done" if is_done else "need"

            icon = self._get_tk_icon(name)
            row_id = self.team_tree.insert(
                "", "end",
                text=f"  {item['display_champ']}",
                image=icon,
                values=(item["player"], status_txt, info["tier"]),
                tags=(tag,)
            )
            self.row_actions[row_id] = item

        self.team_header_lbl.config(text=f"YOUR TEAM ({len(self.team_lobby)})  •  Double-Click to Trade")

        # 2. Populate Right Tree: Either ARAM Bench OR Summoner's Rift Lane Pool
        if mode == "ARAM":
            self.bench_tree.heading("#0", text="BENCH CHAMPION", anchor="w")
            self.bench_tree.heading("role", text="PRIMARY ROLE", anchor="center")

            sorted_bench = sorted(
                self.bench_lobby,
                key=lambda x: (
                    self._is_champ_done(self.champs.get(x["champ"], {})),
                    TIER_ORDER.get(self.champs.get(x["champ"], {}).get("tier", ""), 5),
                    x["champ"]
                )
            )

            need_bench = 0
            for item in sorted_bench:
                name = item["champ"]
                info = self.champs.get(name, {"done_aram": False, "done_sr": False, "tier": "", "role": ""})
                is_done = self._is_champ_done(info)
                if not is_done:
                    need_bench += 1

                status_txt = done_lbl if is_done else need_lbl
                tag = "done" if is_done else "need"
                icon = self._get_tk_icon(name)

                row_id = self.bench_tree.insert(
                    "", "end",
                    text=f"  {name}",
                    image=icon,
                    values=(status_txt, info["tier"], info["role"]),
                    tags=(tag,)
                )
                self.row_actions[row_id] = item

            total_lobby = len(self.team_lobby) + len(self.bench_lobby)
            self.notebook.tab(0, text=f"Live Lobby ({total_lobby})")
            self.bench_header_lbl.config(text=f"REROLL BENCH ({len(self.bench_lobby)})  •  Double-Click to Grab")

            if not self.team_lobby and not self.bench_lobby:
                self.lobby_banner.config(
                    text=f"[{mode_tag}] Waiting for Champ Select  •  Enter a lobby to scan automatically",
                    fg=t["text_secondary"]
                )
            else:
                total_need = need_team + need_bench
                self.lobby_banner.config(
                    text=f"[{mode_tag}]  {my_champ_summary}Bench Needs: {need_bench}   •   Team Needs: {need_team}",
                    fg=t["accent_secondary"] if total_need > 0 else t["accent_primary"]
                )
        else:
            # SUMMONER'S RIFT LANE POOL
            target_lane = self._get_effective_sr_lane()
            sr_query = self.sr_search_var.get().strip().lower()
            only_need = self.sr_need_only_var.get()

            self.bench_tree.heading("#0", text=f"SR CHAMPION ({target_lane.upper()})", anchor="w")
            self.bench_tree.heading("role", text="SR LANES", anchor="center")

            pool_names = []
            for name, info in self.champs.items():
                lanes = info.get("lanes", ())
                if target_lane != "All" and target_lane not in lanes:
                    continue
                if only_need and self._is_champ_done(info):
                    continue
                if sr_query and sr_query not in name.lower() and sr_query not in info.get("role", "").lower():
                    continue
                pool_names.append(name)

            pool_names.sort(
                key=lambda n: (
                    (self.champs[n]["id"] in self.banned_ids or n in picked_champ_names),
                    self._is_champ_done(self.champs[n]),
                    (0 if (target_lane != "All" and self.champs[n].get("lanes", ("",))[0] == target_lane) else 1),
                    n
                )
            )

            need_lane_count = 0
            done_lane_count = 0

            for name in pool_names:
                info = self.champs[name]
                cid = info["id"]
                is_done = self._is_champ_done(info)
                if is_done:
                    done_lane_count += 1
                else:
                    need_lane_count += 1

                is_banned = cid in self.banned_ids
                is_picked = name in picked_champ_names

                if is_banned:
                    disp_name = f"  {name}   [BANNED]"
                    tag = "unavailable"
                elif is_picked:
                    disp_name = f"  {name}   [PICKED]"
                    tag = "done" if is_done else "need"
                else:
                    disp_name = f"  {name}"
                    tag = "done" if is_done else "need"

                status_txt = done_lbl if is_done else need_lbl
                lanes_str = " / ".join(info.get("lanes", (info.get("role", ""),)))
                icon = self._get_tk_icon(name)

                row_id = self.bench_tree.insert(
                    "", "end",
                    text=disp_name,
                    image=icon,
                    values=(status_txt, info["tier"], lanes_str),
                    tags=(tag,)
                )
                self.row_actions[row_id] = {
                    "champ": name,
                    "action": "sr_hover" if not (is_banned or is_picked) else None,
                    "cid": cid,
                    "tid": None
                }

            lane_title = f"{target_lane} Lane" if target_lane != "All" else "All Lanes"
            self.bench_header_lbl.config(
                text=f"SR {lane_title.upper()} POOL ({need_lane_count} Need S+ / {len(pool_names)} Total)  •  Double-Click to Hover"
            )
            self.notebook.tab(0, text=f"Live Lobby ({len(self.team_lobby)})")

            self.lobby_banner.config(
                text=f"[{mode_tag}]  {my_champ_summary}{lane_title}: {need_lane_count} Need S+  •  {done_lane_count} Done",
                fg=t["accent_secondary"] if need_lane_count > 0 else t["accent_primary"]
            )

    def _refresh_all_tree(self):
        self.all_tree.delete(*self.all_tree.get_children())
        query = self.search_var.get().strip().lower()
        fmode = self.filter_var.get()
        done_lbl, need_lbl = self._status_labels()

        for name in sorted(self.champs.keys()):
            info = self.champs[name]
            is_done = self._is_champ_done(info)
            lanes_str = f"{' / '.join(info.get('lanes', ()))} ({info['role']})"

            if fmode == "Need" and is_done:
                continue
            if fmode == "Completed" and not is_done:
                continue
            if query and query not in name.lower() and query not in lanes_str.lower():
                continue

            status_txt = done_lbl if is_done else need_lbl
            tag = "done" if is_done else "need"
            icon = self._get_tk_icon(name)

            self.all_tree.insert(
                "", "end",
                text=f"  {name}",
                image=icon,
                values=(status_txt, info["tier"], lanes_str),
                tags=(tag,)
            )


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AramTrackerApp(root)
        root.mainloop()
    except Exception:
        messagebox.showerror("ARAM S Tracker Error", traceback.format_exc())
