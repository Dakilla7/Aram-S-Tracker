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
    from PIL import Image, ImageTk
    HAS_PIL = True
except Exception:
    HAS_PIL = False

urllib3.disable_warnings()

# ================= VERSION & AUTO-UPDATER SETTINGS =================
APP_VERSION = "1.4.1"
GITHUB_REPO = "Dakilla7/Aram-S-Tracker"
# ===================================================================

APPDATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AramSTracker")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")

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
ICON_SIZE = (28, 28)

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


def load_saved_lol_dir():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("lol_dir", "")
    except Exception:
        pass
    return ""


def save_lol_dir(lol_dir):
    try:
        os.makedirs(APPDATA_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"lol_dir": lol_dir}, f, indent=2)
    except Exception:
        pass


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


class AramTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"⚔️ LoL Challenge S-Grade Tracker v{APP_VERSION}")
        self.root.geometry("1040x700")
        self.root.configure(bg="#0f172a")

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
        self.assigned_lane = ""  # "Top", "Jungle", "Mid", "Bot", "Support", or ""

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

        threading.Thread(target=self._poll_loop, daemon=True).start()
        threading.Thread(target=self._check_for_updates, daemon=True).start()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("TNotebook", background="#0f172a", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e293b", foreground="#94a3b8",
                        padding=[14, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab",
                  background=[("selected", "#2563eb")],
                  foreground=[("selected", "#ffffff")])

        style.configure("Treeview",
                        background="#1e293b",
                        foreground="#f8fafc",
                        fieldbackground="#1e293b",
                        rowheight=36,
                        borderwidth=0,
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#0f172a",
                        foreground="#cbd5e1",
                        font=("Segoe UI", 10, "bold"),
                        relief="flat")
        style.map("Treeview", background=[("selected", "#3b82f6")])

    def _build_ui(self):
        header = tk.Frame(self.root, bg="#1e293b", padx=14, pady=10)
        header.pack(fill="x", padx=10, pady=(10, 6))

        title_col = tk.Frame(header, bg="#1e293b")
        title_col.pack(side="left", fill="y")
        self.title_lbl = tk.Label(
            title_col, text=f"❄️ ARAM: All Random All Champions (S-)  •  v{APP_VERSION}",
            fg="#f8fafc", bg="#1e293b", font=("Segoe UI", 12, "bold")
        )
        self.title_lbl.pack(anchor="w")

        self.status_lbl = tk.Label(title_col, text="⏳ Waiting for League client...",
                                   fg="#fbbf24", bg="#1e293b", font=("Segoe UI", 9))
        self.status_lbl.pack(anchor="w", pady=(2, 0))

        ctrl_row = tk.Frame(title_col, bg="#1e293b")
        ctrl_row.pack(anchor="w", pady=(4, 0))

        pin_cb = tk.Checkbutton(
            ctrl_row, text="📌 Pin on Top", variable=self.always_on_top,
            command=lambda: self.root.attributes("-topmost", self.always_on_top.get()),
            bg="#1e293b", fg="#cbd5e1", selectcolor="#0f172a",
            activebackground="#1e293b", activeforeground="#ffffff", font=("Segoe UI", 9)
        )
        pin_cb.pack(side="left", padx=(0, 8))

        folder_btn = tk.Button(
            ctrl_row, text="📁 Set LoL Folder", command=self._choose_lol_folder,
            bg="#334155", fg="#e2e8f0", activebackground="#475569", activeforeground="#ffffff",
            relief="flat", padx=6, pady=1, font=("Segoe UI", 8), cursor="hand2"
        )
        folder_btn.pack(side="left", padx=(0, 8))

        tk.Label(ctrl_row, text="Mode:", fg="#94a3b8", bg="#1e293b",
                 font=("Segoe UI", 8, "bold")).pack(side="left", padx=(2, 2))
        for m_val, m_label in (("ARAM", "❄️ ARAM (S-)"), ("SR", "🏔️ Rift: Perfectionist (S+)")):
            rb = tk.Radiobutton(
                ctrl_row, text=m_label, variable=self.active_mode, value=m_val,
                command=self._on_mode_changed, bg="#1e293b", fg="#cbd5e1",
                selectcolor="#0f172a", activebackground="#1e293b",
                activeforeground="#ffffff", font=("Segoe UI", 8, "bold")
            )
            rb.pack(side="left", padx=2)

        self.update_btn = tk.Button(
            ctrl_row, text="🚀 Update Available!", command=self._perform_self_update,
            bg="#16a34a", fg="#ffffff", activebackground="#15803d", activeforeground="#ffffff",
            relief="flat", padx=8, pady=1, font=("Segoe UI", 8, "bold"), cursor="hand2"
        )

        stats_col = tk.Frame(header, bg="#1e293b")
        stats_col.pack(side="right", fill="y")

        self.progress_lbl = tk.Label(stats_col, text="0 / 0 (0.0%)",
                                     fg="#38bdf8", bg="#1e293b", font=("Segoe UI", 12, "bold"))
        self.progress_lbl.pack(anchor="e")

        self.milestone_lbl = tk.Label(
            stats_col, text="🏆 Milestone: Loading...",
            fg="#fbbf24", bg="#1e293b", font=("Segoe UI", 9, "bold")
        )
        self.milestone_lbl.pack(anchor="e", pady=(4, 0))

        self.next_milestone_lbl = tk.Label(
            stats_col, text="", fg="#cbd5e1", bg="#1e293b", font=("Segoe UI", 9)
        )
        self.next_milestone_lbl.pack(anchor="e")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=4)

        # ================= TAB 1: SPLIT TEAM (LEFT) & BENCH / SR LANE POOL (RIGHT) =================
        self.tab_lobby = tk.Frame(self.notebook, bg="#0f172a")
        self.notebook.add(self.tab_lobby, text="🎯 Live Lobby (0)")

        top_bar = tk.Frame(self.tab_lobby, bg="#1e293b", padx=10, pady=6)
        top_bar.pack(fill="x", padx=6, pady=6)

        self.lobby_banner = tk.Label(
            top_bar,
            text="Not in Champ Select — Enter an ARAM or Summoner's Rift lobby to scan automatically!",
            fg="#94a3b8", bg="#1e293b", font=("Segoe UI", 9, "bold")
        )
        self.lobby_banner.pack(side="left")

        self.action_btn = tk.Button(
            top_bar, text="⚡ Swap / Trade / Hover (Double-Click)",
            command=self._on_button_action,
            bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff",
            relief="flat", padx=10, pady=3, font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        self.action_btn.pack(side="right")

        split_pane = tk.PanedWindow(
            self.tab_lobby, orient="horizontal", bg="#0f172a",
            sashwidth=6, sashrelief="flat", bd=0
        )
        split_pane.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # --- LEFT PANEL: YOUR TEAM ---
        left_frame = tk.Frame(split_pane, bg="#1e293b", bd=1, relief="solid")
        self.team_header_lbl = tk.Label(
            left_frame, text="👥 YOUR TEAM (Double-Click Teammate to Trade)",
            bg="#0f172a", fg="#38bdf8", font=("Segoe UI", 9, "bold"), pady=6, anchor="w", padx=8
        )
        self.team_header_lbl.pack(fill="x")

        team_cols = ("player", "status", "tier")
        self.team_tree = ttk.Treeview(left_frame, columns=team_cols, show="tree headings")
        self._configure_team_columns(self.team_tree)
        self.team_tree.pack(fill="both", expand=True)
        self.team_tree.bind("<Double-1>", lambda _e: self._trigger_tree_action(self.team_tree))
        self.team_tree.bind("<<TreeviewSelect>>", lambda _e: self._clear_other_selection(self.bench_tree))

        # --- RIGHT PANEL: REROLL BENCH (ARAM) OR LANE POOL (SUMMONER'S RIFT) ---
        self.right_frame = tk.Frame(split_pane, bg="#1e293b", bd=1, relief="solid")
        self.bench_header_lbl = tk.Label(
            self.right_frame, text="🪑 REROLL BENCH (Double-Click Champion to Grab)",
            bg="#0f172a", fg="#4ade80", font=("Segoe UI", 9, "bold"), pady=6, anchor="w", padx=8
        )
        self.bench_header_lbl.pack(fill="x")

        # Summoner's Rift Lane Filter Bar (Shown automatically when in SR mode)
        self.sr_filter_frame = tk.Frame(self.right_frame, bg="#0f172a", padx=6, pady=4)

        lane_row = tk.Frame(self.sr_filter_frame, bg="#0f172a")
        lane_row.pack(fill="x")

        self.auto_lane_rb = tk.Radiobutton(
            lane_row, text="🎯 Auto", variable=self.sr_lane_var, value="Auto",
            command=self._refresh_lobby_trees, bg="#0f172a", fg="#38bdf8",
            selectcolor="#1e293b", activebackground="#0f172a", activeforeground="#ffffff",
            font=("Segoe UI", 8, "bold")
        )
        self.auto_lane_rb.pack(side="left", padx=(0, 2))

        for lane_val, lane_txt in (
            ("Top", "🛡️ Top"),
            ("Jungle", "🌲 Jg"),
            ("Mid", "🔮 Mid"),
            ("Bot", "🏹 Bot"),
            ("Support", "✨ Sup"),
            ("All", "All"),
        ):
            rb = tk.Radiobutton(
                lane_row, text=lane_txt, variable=self.sr_lane_var, value=lane_val,
                command=self._refresh_lobby_trees, bg="#0f172a", fg="#cbd5e1",
                selectcolor="#1e293b", activebackground="#0f172a", activeforeground="#ffffff",
                font=("Segoe UI", 8, "bold")
            )
            rb.pack(side="left", padx=1)

        search_row = tk.Frame(self.sr_filter_frame, bg="#0f172a", pady=3)
        search_row.pack(fill="x")

        tk.Label(search_row, text="🔍", fg="#cbd5e1", bg="#0f172a",
                 font=("Segoe UI", 8)).pack(side="left", padx=(0, 3))
        sr_search_entry = tk.Entry(
            search_row, textvariable=self.sr_search_var,
            bg="#1e293b", fg="#ffffff", insertbackground="#ffffff",
            relief="flat", font=("Segoe UI", 9), width=16
        )
        sr_search_entry.pack(side="left", padx=(0, 8), ipady=2)
        self.sr_search_var.trace_add("write", lambda *_: self._refresh_lobby_trees())

        need_cb = tk.Checkbutton(
            search_row, text="⭐ Only Need S+", variable=self.sr_need_only_var,
            command=self._refresh_lobby_trees,
            bg="#0f172a", fg="#4ade80", selectcolor="#1e293b",
            activebackground="#0f172a", activeforeground="#ffffff", font=("Segoe UI", 8, "bold")
        )
        need_cb.pack(side="left")

        bench_tree_container = tk.Frame(self.right_frame, bg="#1e293b")
        bench_tree_container.pack(fill="both", expand=True)

        bench_cols = ("status", "tier", "role")
        self.bench_tree = ttk.Treeview(bench_tree_container, columns=bench_cols, show="tree headings")
        self._configure_bench_columns(self.bench_tree)
        bench_scroll = ttk.Scrollbar(bench_tree_container, orient="vertical", command=self.bench_tree.yview)
        self.bench_tree.configure(yscrollcommand=bench_scroll.set)

        self.bench_tree.pack(side="left", fill="both", expand=True)
        bench_scroll.pack(side="right", fill="y")

        self.bench_tree.bind("<Double-1>", lambda _e: self._trigger_tree_action(self.bench_tree))
        self.bench_tree.bind("<<TreeviewSelect>>", lambda _e: self._clear_other_selection(self.team_tree))

        split_pane.add(left_frame, minsize=410, width=510)
        split_pane.add(self.right_frame, minsize=380, width=500)

        # ================= TAB 2: ALL CHAMPIONS LIST =================
        self.tab_all = tk.Frame(self.notebook, bg="#0f172a")
        self.notebook.add(self.tab_all, text="📋 All Champions (0)")

        filter_bar = tk.Frame(self.tab_all, bg="#0f172a", pady=6)
        filter_bar.pack(fill="x", padx=6)

        tk.Label(filter_bar, text="🔍", fg="#cbd5e1", bg="#0f172a",
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))
        search_entry = tk.Entry(filter_bar, textvariable=self.search_var,
                                bg="#1e293b", fg="#ffffff", insertbackground="#ffffff",
                                relief="flat", font=("Segoe UI", 10), width=20)
        search_entry.pack(side="left", padx=(0, 10), ipady=3)
        self.search_var.trace_add("write", lambda *_: self._refresh_all_tree())

        for mode in ("All", "⭐ Need Grade", "✅ Completed"):
            rb = tk.Radiobutton(
                filter_bar, text=mode, variable=self.filter_var, value=mode,
                command=self._refresh_all_tree, bg="#0f172a", fg="#cbd5e1",
                selectcolor="#1e293b", activebackground="#0f172a",
                activeforeground="#ffffff", font=("Segoe UI", 9, "bold")
            )
            rb.pack(side="left", padx=4)

        tree_frame = tk.Frame(self.tab_all, bg="#0f172a")
        tree_frame.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        all_cols = ("status", "tier", "role")
        self.all_tree = ttk.Treeview(tree_frame, columns=all_cols, show="tree headings")
        self._configure_all_columns(self.all_tree)
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.all_tree.yview)
        self.all_tree.configure(yscrollcommand=scrollbar.set)

        self.all_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _is_champ_done(self, info):
        if self.active_mode.get() == "SR":
            return info.get("done_sr", False)
        return info.get("done_aram", False)

    def _status_labels(self):
        if self.active_mode.get() == "SR":
            return "✅ S+ Earned", "⭐ NEED S+"
        return "✅ S Earned", "⭐ NEED S"

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
            self.status_lbl.config(text=f"📁 Saved folder: {folder}", fg="#38bdf8")

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
                        self.root.after(0, lambda: self.update_btn.config(text=f"🚀 Update to {tag}"))
                        self.root.after(0, lambda: self.update_btn.pack(side="left", padx=4))
                        break
        except Exception:
            pass

    def _perform_self_update(self):
        if not getattr(sys, "frozen", False):
            messagebox.showinfo("Updater", "Self-update only runs inside the compiled .exe!")
            return
        if not self.update_download_url:
            return

        self.update_btn.config(text="⏳ Downloading...", state="disabled")

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
                self.root.after(0, lambda: self.update_btn.config(text="🚀 Retry Update", state="normal"))

        threading.Thread(target=download_and_swap, daemon=True).start()

    def _configure_team_columns(self, tree):
        tree.heading("#0", text="Champion & Trade Status", anchor="w")
        tree.column("#0", width=195, anchor="w", stretch=True)

        tree.heading("player", text="Player (Riot ID)", anchor="w")
        tree.heading("status", text="Challenge Status", anchor="center")
        tree.heading("tier", text="Tier", anchor="center")

        tree.column("player", width=165, anchor="w", stretch=True)
        tree.column("status", width=105, anchor="center", stretch=False)
        tree.column("tier", width=50, anchor="center", stretch=False)

        tree.tag_configure("need_you", background="#14532d", foreground="#86efac")
        tree.tag_configure("done_you", background="#1e3a8a", foreground="#93c5fd")
        tree.tag_configure("need", background="#1e3a2f", foreground="#4ade80")
        tree.tag_configure("done", background="#1e293b", foreground="#64748b")

    def _configure_bench_columns(self, tree):
        tree.heading("#0", text="Champion", anchor="w")
        tree.column("#0", width=175, anchor="w", stretch=True)

        tree.heading("status", text="Challenge Status", anchor="center")
        tree.heading("tier", text="Tier", anchor="center")
        tree.heading("role", text="Lanes / Role", anchor="center")

        tree.column("status", width=105, anchor="center", stretch=False)
        tree.column("tier", width=50, anchor="center", stretch=False)
        tree.column("role", width=125, anchor="center", stretch=False)

        tree.tag_configure("need", background="#1e3a2f", foreground="#4ade80")
        tree.tag_configure("done", background="#1e293b", foreground="#64748b")
        tree.tag_configure("unavailable", background="#0f172a", foreground="#475569")

    def _configure_all_columns(self, tree):
        tree.heading("#0", text="Champion", anchor="w")
        tree.column("#0", width=230, anchor="w", stretch=True)

        tree.heading("status", text="Challenge Status")
        tree.heading("tier", text="ARAM Tier")
        tree.heading("role", text="SR Lanes & Role")

        tree.column("status", width=150, anchor="center", stretch=False)
        tree.column("tier", width=100, anchor="center", stretch=False)
        tree.column("role", width=180, anchor="center", stretch=False)

        tree.tag_configure("need", background="#1e3a2f", foreground="#4ade80")
        tree.tag_configure("done", background="#1e293b", foreground="#64748b")

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
                tk_img = ImageTk.PhotoImage(pil_img)
            else:
                full_img = tk.PhotoImage(data=base64.b64encode(raw))
                scale = max(1, full_img.width() // 28)
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
        """Hover/select a champion in Summoner's Rift Champ Select."""
        session = get_json("/lol-champ-select/v1/session")
        local_cell = session.get("localPlayerCellId", -1)

        # Search for the local player's active or upcoming 'pick' action
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
            return f"🎯 Hovered {champ_name} in Champ Select!"

        # Fallback for Blind/Quickplay or pre-pick intent
        patch_req("/lol-champ-select/v1/session/my-selection", {"championId": cid})
        return f"🎯 Selected {champ_name}!"

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
            self.status_lbl.config(text=f"ℹ️ You already have {champ_name}!", fg="#38bdf8")
            return
        if not action:
            self.status_lbl.config(text=f"⚠️ Cannot trade/swap {champ_name} right now.", fg="#fbbf24")
            return

        def run_action():
            try:
                get_json, _, post_req, patch_req = lcu_client()
                if action == "bench" and cid:
                    post_req(f"/lol-champ-select/v1/session/bench/swap/{cid}")
                    msg = f"✅ Grabbed {champ_name} from the bench!"
                elif action == "sr_hover" and cid:
                    msg = self._hover_sr_champion(get_json, patch_req, cid, champ_name)
                elif action == "trade_acc" and tid is not None:
                    post_req(f"/lol-champ-select/v1/session/champion-swaps/{tid}/accept")
                    msg = f"✅ Accepted trade for {champ_name}!"
                elif action == "trade_req" and tid is not None:
                    post_req(f"/lol-champ-select/v1/session/champion-swaps/{tid}/request")
                    msg = f"📨 Sent trade request for {champ_name}!"
                else:
                    msg = f"⚠️ Action unavailable for {champ_name}."
                self.root.after(0, lambda m=msg: self.status_lbl.config(text=m, fg="#4ade80"))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.status_lbl.config(
                    text=f"⚠️ Action failed: {err[:45]}", fg="#f87171"))

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
            base = f"👤 {name_str}" if name_str else "👤 You"
            return f"{base}{lane_badge}"
        base = f"👥 {name_str}" if name_str else f"👥 Teammate {slot_idx}"
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
        """
        Detect whether the player is in an ARAM or Summoner's Rift queue,
        and detect their assigned/selected lane (Top, Jungle, Mid, Bot, Support).
        """
        detected_mode = None
        q_label = ""
        lane = ""

        # 1. Check Champ Select assignedPosition first if in Champ Select
        if cs_session is not None:
            local_cell = cs_session.get("localPlayerCellId", -1)
            for m in cs_session.get("myTeam", []):
                if m.get("cellId") == local_cell:
                    raw_pos = (m.get("assignedPosition") or "").strip().lower()
                    lane = POSITION_MAP.get(raw_pos, "")
                    break

        # 2. Check Gameflow session
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

        # 3. Check Pre-Game Lobby (/lol-lobby/v2/lobby) for queue mode & selected position preference
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

        # 4. Fallback to Champ Select benchEnabled flag
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

        # Collect banned champion IDs in Draft/Ranked
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
                    display_champ = f"{display_champ}  📩 Accept!"
                    act = "trade_acc"
                elif tstate == "SENT":
                    display_champ = f"{display_champ}  ⏳ Sent"
                    act = None
                elif tstate == "AVAILABLE" and tid is not None:
                    display_champ = f"{display_champ}  🔄"
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
                self.root.after(0, lambda: self.status_lbl.config(
                    text="⏳ Waiting for League client... (or click '📁 Set LoL Folder')", fg="#fbbf24"))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.status_lbl.config(
                    text=f"⚠️ Client loading ({err[:35]})", fg="#f87171"))

            time.sleep(0.8)

    def _update_dashboard(self):
        mode = self.active_mode.get()
        total = len(self.champs)
        done = sum(1 for v in self.champs.values() if self._is_champ_done(v))
        rem = total - done
        pct = (done / total * 100) if total else 0

        if mode == "SR":
            self.title_lbl.config(text=f"🏔️ Summoner's Rift: Perfectionist (S+ Only)  •  v{APP_VERSION}")
            grade_short = "S+"
        else:
            self.title_lbl.config(text=f"❄️ ARAM: All Random All Champions (S-)  •  v{APP_VERSION}")
            grade_short = "S-"

        auto_txt = f"🎯 Auto ({self.assigned_lane})" if self.assigned_lane else "🎯 Auto (All)"
        self.auto_lane_rb.config(text=auto_txt)

        q_suffix = f"  •  Queue: {self.detected_queue_label}" if self.detected_queue_label else ""
        lane_suffix = f" ({self.assigned_lane})" if (mode == "SR" and self.assigned_lane) else ""
        self.status_lbl.config(text=f"🟢 Connected to League Client{q_suffix}{lane_suffix}", fg="#4ade80")
        self.progress_lbl.config(text=f"✅ {done} ({grade_short})  |  ⭐ {rem} Left ({pct:.1f}%)")

        milestones = self.milestones_by_mode.get(mode, DEFAULT_MILESTONES)
        cur_tier, cur_pts = "Unranked", 0
        next_target, next_tier, next_pts = None, None, None

        for req_count, tier_name, pts in milestones:
            if done >= req_count:
                cur_tier, cur_pts = tier_name, pts
            elif next_target is None:
                next_target, next_tier, next_pts = req_count, tier_name, pts

        self.milestone_lbl.config(text=f"🏆 Current Milestone: {cur_tier} ({cur_pts} pts)")

        if next_target is not None:
            needed = next_target - done
            diff_pts = next_pts - cur_pts
            self.next_milestone_lbl.config(
                text=f"🎯 Next: {next_tier} ({next_pts} pts, +{diff_pts}) in {needed} champs ({done}/{next_target})"
            )
        else:
            self.next_milestone_lbl.config(
                text=f"👑 Max Milestone Reached! ({rem} left for 100%)"
            )

        self.notebook.tab(1, text=f"📋 All Champions ({total})")
        self._refresh_all_tree()
        self._refresh_lobby_trees()

    def _refresh_lobby_trees(self):
        self.team_tree.delete(*self.team_tree.get_children())
        self.bench_tree.delete(*self.bench_tree.get_children())
        self.row_actions.clear()

        done_lbl, need_lbl = self._status_labels()
        mode = self.active_mode.get()
        mode_tag = "🏔️ SR Perfectionist (S+)" if mode == "SR" else "❄️ ARAM (S-)"

        # Show or hide the Summoner's Rift Lane Filter Bar above the right tree
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
                my_champ_summary = f"👤 Your Pick: {name} ({status_txt})   •   "
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

        self.team_header_lbl.config(text=f"👥 YOUR TEAM ({len(self.team_lobby)}) — Double-Click Teammate to Trade")

        # 2. Populate Right Tree: Either ARAM Bench OR Summoner's Rift Lane Pool
        if mode == "ARAM":
            self.bench_tree.heading("#0", text="Bench Champion", anchor="w")
            self.bench_tree.heading("role", text="Primary Role", anchor="center")

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
            self.notebook.tab(0, text=f"🎯 Live Lobby ({total_lobby})")
            self.bench_header_lbl.config(text=f"🪑 REROLL BENCH ({len(self.bench_lobby)}) — Double-Click to Grab")

            if not self.team_lobby and not self.bench_lobby:
                self.lobby_banner.config(
                    text=f"[{mode_tag}] Not in Champ Select — Enter a lobby to scan automatically!",
                    fg="#94a3b8"
                )
            else:
                total_need = need_team + need_bench
                self.lobby_banner.config(
                    text=f"[{mode_tag}]  {my_champ_summary}🪑 Bench Needs: {need_bench}   •   👥 Team Needs: {need_team}",
                    fg="#4ade80" if total_need > 0 else "#38bdf8"
                )
        else:
            # SUMMONER'S RIFT LANE POOL
            target_lane = self._get_effective_sr_lane()
            sr_query = self.sr_search_var.get().strip().lower()
            only_need = self.sr_need_only_var.get()

            self.bench_tree.heading("#0", text=f"SR Champion ({target_lane})", anchor="w")
            self.bench_tree.heading("role", text="SR Lanes", anchor="center")

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

            # Sort: Available first -> Need S+ first -> Primary lane match first -> Name
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
                    disp_name = f"  {name}  🚫 Banned"
                    tag = "unavailable"
                elif is_picked:
                    disp_name = f"  {name}  👥 Picked"
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
                text=f"🗺️ SR {lane_title.upper()} POOL ({need_lane_count} Need S+ / {len(pool_names)} Shown) — Double-Click to Hover"
            )
            self.notebook.tab(0, text=f"🎯 Live Lobby ({len(self.team_lobby)})")

            self.lobby_banner.config(
                text=f"[{mode_tag}]  {my_champ_summary}🗺️ {lane_title}: ⭐ {need_lane_count} Need S+  •  ✅ {done_lane_count} Done",
                fg="#4ade80" if need_lane_count > 0 else "#38bdf8"
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

            if fmode == "⭐ Need Grade" and is_done:
                continue
            if fmode == "✅ Completed" and not is_done:
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