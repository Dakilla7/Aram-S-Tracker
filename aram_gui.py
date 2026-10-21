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
APP_VERSION = "1.4.0"
GITHUB_REPO = "Dakilla7/Aram-S-Tracker"
# ===================================================================

APPDATA_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "AramSTracker")
CONFIG_FILE = os.path.join(APPDATA_DIR, "config.json")

# {Champion Name: (ARAM Tier, Primary Role)}
STATIC_DATA = {
    "Aatrox": ("A", "Fighter"), "Ahri": ("A", "Mage"), "Akali": ("B", "Assassin"),
    "Akshan": ("A", "Marksman"), "Alistar": ("S", "Tank"), "Ambessa": ("A", "Fighter"),
    "Amumu": ("S", "Tank"), "Anivia": ("S", "Mage"), "Annie": ("A", "Mage"),
    "Aphelios": ("A", "Marksman"), "Ashe": ("S", "Marksman"), "Aurelion Sol": ("S+", "Mage"),
    "Aurora": ("A", "Mage"), "Azir": ("A", "Mage"), "Bard": ("B", "Support"),
    "Bel'Veth": ("B", "Fighter"), "Blitzcrank": ("S", "Tank"), "Brand": ("S+", "Mage"),
    "Braum": ("A", "Support"), "Briar": ("B", "Fighter"), "Caitlyn": ("S", "Marksman"),
    "Camille": ("B", "Fighter"), "Cassiopeia": ("A", "Mage"), "Cho'Gath": ("S", "Tank"),
    "Corki": ("A", "Marksman"), "Darius": ("A", "Fighter"), "Diana": ("A", "Fighter"),
    "Dr. Mundo": ("S", "Tank"), "Draven": ("B", "Marksman"), "Ekko": ("A", "Assassin"),
    "Elise": ("B", "Mage"), "Evelynn": ("C", "Assassin"), "Ezreal": ("S", "Marksman"),
    "Fiddlesticks": ("S", "Mage"), "Fiora": ("C", "Fighter"), "Fizz": ("B", "Assassin"),
    "Galio": ("A", "Tank"), "Gangplank": ("A", "Fighter"), "Garen": ("A", "Fighter"),
    "Gnar": ("A", "Fighter"), "Gragas": ("S", "Fighter"), "Graves": ("A", "Marksman"),
    "Gwen": ("A", "Fighter"), "Hecarim": ("A", "Fighter"), "Heimerdinger": ("S", "Mage"),
    "Hwei": ("S+", "Mage"), "Illaoi": ("S", "Fighter"), "Irelia": ("B", "Fighter"),
    "Ivern": ("B", "Support"), "Janna": ("A", "Support"), "Jarvan IV": ("A", "Tank"),
    "Jax": ("A", "Fighter"), "Jayce": ("S", "Fighter"), "Jhin": ("S+", "Marksman"),
    "Jinx": ("S+", "Marksman"), "K'Sante": ("A", "Tank"), "Kai'Sa": ("S", "Marksman"),
    "Kalista": ("B", "Marksman"), "Karma": ("S", "Mage"), "Karthus": ("S+", "Mage"),
    "Kassadin": ("A", "Assassin"), "Katarina": ("A", "Assassin"), "Kayle": ("A", "Fighter"),
    "Kayn": ("A", "Fighter"), "Kennen": ("S", "Mage"), "Kha'Zix": ("B", "Assassin"),
    "Kindred": ("B", "Marksman"), "Kled": ("A", "Fighter"), "Kog'Maw": ("S", "Marksman"),
    "LeBlanc": ("B", "Assassin"), "Lee Sin": ("A", "Fighter"), "Leona": ("S", "Tank"),
    "Lillia": ("S", "Fighter"), "Lissandra": ("S", "Mage"), "Lucian": ("A", "Marksman"),
    "Lulu": ("A", "Support"), "Lux": ("S+", "Mage"), "Malphite": ("S", "Tank"),
    "Malzahar": ("A", "Mage"), "Maokai": ("S+", "Tank"), "Master Yi": ("A", "Assassin"),
    "Mel": ("A", "Mage"), "Milio": ("A", "Support"), "Miss Fortune": ("S+", "Marksman"),
    "Mordekaiser": ("A", "Fighter"), "Morgana": ("S", "Mage"), "Naafiri": ("A", "Assassin"),
    "Nami": ("A", "Support"), "Nasus": ("A", "Fighter"), "Nautilus": ("S", "Tank"),
    "Neeko": ("A", "Mage"), "Nidalee": ("A", "Mage"), "Nilah": ("A", "Fighter"),
    "Nocturne": ("B", "Assassin"), "Nunu & Willump": ("A", "Tank"), "Olaf": ("A", "Fighter"),
    "Orianna": ("S", "Mage"), "Ornn": ("S", "Tank"), "Pantheon": ("A", "Fighter"),
    "Poppy": ("A", "Tank"), "Pyke": ("S", "Support"), "Qiyana": ("B", "Assassin"),
    "Quinn": ("C", "Marksman"), "Rakan": ("A", "Support"), "Rammus": ("A", "Tank"),
    "Rek'Sai": ("B", "Fighter"), "Rell": ("S", "Tank"), "Renata Glasc": ("S", "Support"),
    "Renekton": ("B", "Fighter"), "Rengar": ("B", "Assassin"), "Riven": ("B", "Fighter"),
    "Rumble": ("S", "Fighter"), "Ryze": ("A", "Mage"), "Samira": ("S", "Marksman"),
    "Sejuani": ("A", "Tank"), "Senna": ("S+", "Marksman"), "Seraphine": ("S+", "Mage"),
    "Sett": ("S", "Fighter"), "Shaco": ("B", "Assassin"), "Shen": ("A", "Tank"),
    "Shyvana": ("A", "Fighter"), "Singed": ("A", "Tank"), "Sion": ("S", "Tank"),
    "Sivir": ("S", "Marksman"), "Skarner": ("A", "Tank"), "Smolder": ("S+", "Marksman"),
    "Sona": ("S+", "Support"), "Soraka": ("S", "Support"), "Swain": ("S", "Mage"),
    "Sylas": ("A", "Mage"), "Syndra": ("A", "Mage"), "Tahm Kench": ("A", "Tank"),
    "Taliyah": ("A", "Mage"), "Talon": ("B", "Assassin"), "Taric": ("S", "Support"),
    "Teemo": ("S+", "Marksman"), "Thresh": ("S", "Support"), "Tristana": ("A", "Marksman"),
    "Trundle": ("A", "Fighter"), "Tryndamere": ("B", "Fighter"), "Twisted Fate": ("A", "Mage"),
    "Twitch": ("S", "Marksman"), "Udyr": ("A", "Fighter"), "Urgot": ("A", "Fighter"),
    "Varus": ("S+", "Marksman"), "Vayne": ("A", "Marksman"), "Veigar": ("S+", "Mage"),
    "Vel'Koz": ("S", "Mage"), "Vex": ("A", "Mage"), "Vi": ("A", "Fighter"),
    "Viego": ("A", "Assassin"), "Viktor": ("S", "Mage"), "Vladimir": ("A", "Mage"),
    "Volibear": ("A", "Fighter"), "Warwick": ("B", "Fighter"), "Wukong": ("S", "Fighter"),
    "Xayah": ("A", "Marksman"), "Xerath": ("S+", "Mage"), "Xin Zhao": ("A", "Fighter"),
    "Yasuo": ("A", "Fighter"), "Yone": ("A", "Fighter"), "Yorick": ("B", "Fighter"),
    "Yuumi": ("A", "Support"), "Zac": ("S", "Tank"), "Zed": ("B", "Assassin"),
    "Zeri": ("A", "Marksman"), "Ziggs": ("S+", "Mage"), "Zilean": ("A", "Support"),
    "Zoe": ("A", "Mage"), "Zyra": ("S", "Mage"),
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

    def post_req(path):
        r = requests.post(base + path, headers=headers, verify=False, timeout=5)
        r.raise_for_status()
        return r

    return get_json, get_bytes, post_req


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
        self.root.geometry("960x680")
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
        self.row_actions = {}

        # Active challenge mode: "ARAM" (All Random All Champions S-) or "SR" (Perfectionist S+)
        self.active_mode = tk.StringVar(value="ARAM")
        self.detected_queue_label = ""
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

        # Mode Switcher (Also switches automatically when entering ARAM or Summoner's Rift lobbies)
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

        # ================= TAB 1: SPLIT TEAM (LEFT) & BENCH (RIGHT) =================
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
            top_bar, text="⚡ Swap / Trade Selected (or Double-Click)",
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

        # --- RIGHT PANEL: REROLL BENCH ---
        right_frame = tk.Frame(split_pane, bg="#1e293b", bd=1, relief="solid")
        self.bench_header_lbl = tk.Label(
            right_frame, text="🪑 REROLL BENCH (Double-Click Champion to Grab)",
            bg="#0f172a", fg="#4ade80", font=("Segoe UI", 9, "bold"), pady=6, anchor="w", padx=8
        )
        self.bench_header_lbl.pack(fill="x")

        bench_cols = ("status", "tier", "role")
        self.bench_tree = ttk.Treeview(right_frame, columns=bench_cols, show="tree headings")
        self._configure_bench_columns(self.bench_tree)
        self.bench_tree.pack(fill="both", expand=True)
        self.bench_tree.bind("<Double-1>", lambda _e: self._trigger_tree_action(self.bench_tree))
        self.bench_tree.bind("<<TreeviewSelect>>", lambda _e: self._clear_other_selection(self.team_tree))

        split_pane.add(left_frame, minsize=400, width=500)
        split_pane.add(right_frame, minsize=340, width=430)

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
        tree.column("#0", width=200, anchor="w", stretch=True)

        tree.heading("player", text="Player (Riot ID)", anchor="w")
        tree.heading("status", text="Challenge Status", anchor="center")
        tree.heading("tier", text="Tier", anchor="center")

        tree.column("player", width=155, anchor="w", stretch=True)
        tree.column("status", width=105, anchor="center", stretch=False)
        tree.column("tier", width=55, anchor="center", stretch=False)

        tree.tag_configure("need_you", background="#14532d", foreground="#86efac")
        tree.tag_configure("done_you", background="#1e3a8a", foreground="#93c5fd")
        tree.tag_configure("need", background="#1e3a2f", foreground="#4ade80")
        tree.tag_configure("done", background="#1e293b", foreground="#64748b")

    def _configure_bench_columns(self, tree):
        tree.heading("#0", text="Bench Champion", anchor="w")
        tree.column("#0", width=170, anchor="w", stretch=True)

        tree.heading("status", text="Challenge Status", anchor="center")
        tree.heading("tier", text="Tier", anchor="center")
        tree.heading("role", text="Role", anchor="center")

        tree.column("status", width=110, anchor="center", stretch=False)
        tree.column("tier", width=60, anchor="center", stretch=False)
        tree.column("role", width=95, anchor="center", stretch=False)

        tree.tag_configure("need", background="#1e3a2f", foreground="#4ade80")
        tree.tag_configure("done", background="#1e293b", foreground="#64748b")

    def _configure_all_columns(self, tree):
        tree.heading("#0", text="Champion", anchor="w")
        tree.column("#0", width=240, anchor="w", stretch=True)

        tree.heading("status", text="Challenge Status")
        tree.heading("tier", text="ARAM Tier")
        tree.heading("role", text="Primary Role")

        tree.column("status", width=160, anchor="center", stretch=False)
        tree.column("tier", width=110, anchor="center", stretch=False)
        tree.column("role", width=140, anchor="center", stretch=False)

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
                _, _, post_req = lcu_client()
                if action == "bench" and cid:
                    post_req(f"/lol-champ-select/v1/session/bench/swap/{cid}")
                    msg = f"✅ Grabbed {champ_name} from the bench!"
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

        if is_me:
            return f"👤 {name_str} (You)" if name_str else "👤 You"
        return f"👥 {name_str}" if name_str else f"👥 Teammate {slot_idx}"

    def _extract_standard_milestones(self, c_obj):
        """Extract Iron->Master thresholds cleanly while ignoring Grandmaster/Challenger/seasonal."""
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

            # 1. All Random All Champions (ID 101301) - S- or higher in ARAM
            if cid_int == 101301 or "all random all champions" in cname:
                aram_done_ids.update(c.get("completedIds", []))
                if cid_int == 101301 or cname == "all random all champions":
                    ms = self._extract_standard_milestones(c)
                    if ms:
                        self.milestones_by_mode["ARAM"] = ms

            # 2. Perfectionist (ID 210001) - S+ on different champions in Summoner's Rift
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
            tier, static_role = STATIC_DATA.get(name, ("", ""))
            role = static_role or ((c.get("roles") or [""])[0]).capitalize()
            icon_path = c.get("squarePortraitPath") or f"/lol-game-data/assets/v1/champion-icons/{cid}.png"

            id_to_name[cid] = name
            if name not in champs:
                champs[name] = {
                    "id": cid,
                    "done_aram": done_aram,
                    "done_sr": done_sr,
                    "tier": tier,
                    "role": role,
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

    def _detect_queue_mode(self, get_json, cs_session=None):
        """
        Auto-detect whether the player is in an ARAM / ARAM Mayhem lobby
        or a Summoner's Rift (Normal, Draft, Ranked Solo/Duo, Flex) lobby.
        Returns ("ARAM" | "SR" | None, queue_description_str).
        """
        # 1. Check active Gameflow session (works in Lobby, Queue, and Champ Select)
        try:
            gf = get_json("/lol-gameflow/v1/session")
            gdata = gf.get("gameData", {})
            q = gdata.get("queue", {})
            map_id = q.get("mapId") or gf.get("map", {}).get("id")
            gmode = (q.get("gameMode") or gf.get("map", {}).get("gameMode") or "").upper()
            qdesc = (q.get("description") or q.get("shortName") or gmode).strip()

            if map_id == 12 or "ARAM" in gmode or "ARAM" in qdesc.upper() or "MAYHEM" in qdesc.upper():
                return "ARAM", (qdesc or "ARAM")
            if map_id == 11 or gmode in ("CLASSIC", "SWIFTPLAY"):
                return "SR", (qdesc or "Summoner's Rift")
        except Exception:
            pass

        # 2. Check Pre-Game Lobby (/lol-lobby/v2/lobby)
        try:
            lob = get_json("/lol-lobby/v2/lobby")
            gcfg = lob.get("gameConfig", {})
            map_id = gcfg.get("mapId")
            gmode = (gcfg.get("gameMode") or "").upper()
            if map_id == 12 or "ARAM" in gmode or "KIWI" in gmode:
                return "ARAM", "ARAM Lobby"
            if map_id == 11 or gmode in ("CLASSIC", "SWIFTPLAY"):
                return "SR", "Summoner's Rift Lobby"
        except Exception:
            pass

        # 3. Fallback to Champ Select benchEnabled flag
        if cs_session is not None:
            if cs_session.get("benchEnabled", False):
                return "ARAM", "ARAM"
            return "SR", "Summoner's Rift"

        return None, ""

    def _fetch_lobby(self, get_json):
        session = None
        try:
            session = get_json("/lol-champ-select/v1/session")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code != 404:
                raise
        except Exception:
            pass

        # Detect queue mode even before Champ Select starts (e.g. while sitting in Lobby/Queue)
        detected_mode, q_label = self._detect_queue_mode(get_json, session)
        if detected_mode and detected_mode != self.active_mode.get():
            self.active_mode.set(detected_mode)
            self.detected_queue_label = q_label
            self.root.after(0, self._update_dashboard)
        elif q_label != self.detected_queue_label:
            self.detected_queue_label = q_label
            self.root.after(0, self._update_dashboard)

        if not session:
            return None, None

        local_cell = session.get("localPlayerCellId", -1)
        swaps_list = session.get("championSwaps") or session.get("trades", [])
        cell_trades = {t.get("cellId"): t for t in swaps_list}

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

            # Put trade emojis right after the champion name instead of the player name
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

        return team_list, bench_list

    def _poll_loop(self):
        last_sync = 0
        last_state = None

        while True:
            try:
                get_json, get_bytes, _ = lcu_client()
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
                    team_list, bench_list = self._fetch_lobby(get_json)
                    cur_state = (team_list, bench_list, self.active_mode.get())
                    if cur_state != last_state:
                        self.team_lobby = team_list or []
                        self.bench_lobby = bench_list or []
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

        q_suffix = f"  •  Queue: {self.detected_queue_label}" if self.detected_queue_label else ""
        self.status_lbl.config(text=f"🟢 Connected to League Client{q_suffix}", fg="#4ade80")
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

        total_lobby = len(self.team_lobby) + len(self.bench_lobby)
        self.notebook.tab(0, text=f"🎯 Live Lobby ({total_lobby})")
        self.team_header_lbl.config(text=f"👥 YOUR TEAM ({len(self.team_lobby)}) — Double-Click Teammate to Trade")
        self.bench_header_lbl.config(text=f"🪑 REROLL BENCH ({len(self.bench_lobby)}) — Double-Click to Grab")

        if not self.team_lobby and not self.bench_lobby:
            self.lobby_banner.config(
                text=f"[{mode_tag}] Not in Champ Select — Enter a lobby to scan automatically!",
                fg="#94a3b8"
            )
            return

        need_team = 0
        my_champ_summary = ""

        sorted_team = sorted(self.team_lobby, key=lambda x: (not x["is_me"]))
        for item in sorted_team:
            name = item["champ"]
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

        total_need = need_team + need_bench
        self.lobby_banner.config(
            text=f"[{mode_tag}]  {my_champ_summary}🪑 Bench Needs: {need_bench}   •   👥 Team Needs: {need_team}",
            fg="#4ade80" if total_need > 0 else "#38bdf8"
        )
        self.notebook.select(0)

    def _refresh_all_tree(self):
        self.all_tree.delete(*self.all_tree.get_children())
        query = self.search_var.get().strip().lower()
        fmode = self.filter_var.get()
        done_lbl, need_lbl = self._status_labels()

        for name in sorted(self.champs.keys()):
            info = self.champs[name]
            is_done = self._is_champ_done(info)

            if fmode == "⭐ Need Grade" and is_done:
                continue
            if fmode == "✅ Completed" and not is_done:
                continue
            if query and query not in name.lower() and query not in info["role"].lower():
                continue

            status_txt = done_lbl if is_done else need_lbl
            tag = "done" if is_done else "need"
            icon = self._get_tk_icon(name)

            self.all_tree.insert(
                "", "end",
                text=f"  {name}",
                image=icon,
                values=(status_txt, info["tier"], info["role"]),
                tags=(tag,)
            )


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = AramTrackerApp(root)
        root.mainloop()
    except Exception:
        messagebox.showerror("ARAM S Tracker Error", traceback.format_exc())