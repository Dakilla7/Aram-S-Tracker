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
APP_VERSION = "1.2.0"
GITHUB_REPO = "Dakilla7/Aram-S-Tracker"  # e.g. "GitHub-Name/Repository-Name"
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

MILESTONES = [
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
    """Read Riot's official ProgramData metadata to find League of Legends on ANY drive/folder."""
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
    """Automatically locate the League lockfile on any friend's PC without hardcoding."""
    candidates = []

    # 1. User-selected folder (if they ever used the 'Set Folder' button)
    saved_dir = load_saved_lol_dir()
    if saved_dir:
        candidates.append(os.path.join(saved_dir, "lockfile"))

    # 2. Environment variable
    if os.environ.get("LOL_LOCKFILE"):
        candidates.append(os.environ["LOL_LOCKFILE"])

    # 3. Official Riot Client ProgramData install path (works for custom folders on any drive!)
    meta_lockfile = get_riot_metadata_lockfile()
    if meta_lockfile:
        candidates.append(meta_lockfile)

    # 4. Scan common folders across all drive letters (C: through Z:)
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
    """Remove leftover .exe.old file after a self-update."""
    if getattr(sys, "frozen", False):
        old_exe = sys.executable + ".old"
        if os.path.exists(old_exe):
            try:
                os.remove(old_exe)
            except Exception:
                pass


def parse_version(v_str):
    return tuple(int(x) for x in re.findall(r"\d+", str(v_str)))


def location_priority(loc):
    if loc.startswith("👤 You"):
        return 0
    if loc.startswith("🪑 Bench"):
        return 1
    return 2


class AramTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"⚔️ ARAM S-Grade Tracker v{APP_VERSION}")
        self.root.geometry("720x670")
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
        self.lobby = {}
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
        tk.Label(title_col, text=f"⚔️ ARAM S-Grade Tracker v{APP_VERSION}",
                 fg="#f8fafc", bg="#1e293b", font=("Segoe UI", 13, "bold")).pack(anchor="w")
        self.status_lbl = tk.Label(title_col, text="⏳ Waiting for League client...",
                                   fg="#fbbf24", bg="#1e293b", font=("Segoe UI", 9))
        self.status_lbl.pack(anchor="w", pady=(2, 0))

        ctrl_row = tk.Frame(title_col, bg="#1e293b")
        ctrl_row.pack(anchor="w", pady=(3, 0))

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
        folder_btn.pack(side="left", padx=(0, 6))

        # Hidden until an update is found on GitHub
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

        # TAB 1: Live ARAM Lobby & Bench
        self.tab_lobby = tk.Frame(self.notebook, bg="#0f172a")
        self.notebook.add(self.tab_lobby, text="🎯 Live ARAM Lobby (0)")

        top_bar = tk.Frame(self.tab_lobby, bg="#1e293b", padx=10, pady=6)
        top_bar.pack(fill="x", padx=6, pady=6)

        self.lobby_banner = tk.Label(
            top_bar,
            text="Not in Champ Select — Enter an ARAM lobby to scan automatically!",
            fg="#94a3b8", bg="#1e293b", font=("Segoe UI", 9, "bold")
        )
        self.lobby_banner.pack(side="left")

        self.action_btn = tk.Button(
            top_bar, text="⚡ Swap / Trade (Double-Click)",
            command=self._on_swap_or_trade,
            bg="#2563eb", fg="#ffffff", activebackground="#1d4ed8", activeforeground="#ffffff",
            relief="flat", padx=10, pady=3, font=("Segoe UI", 9, "bold"), cursor="hand2"
        )
        self.action_btn.pack(side="right")

        lobby_cols = ("location", "status", "tier", "role")
        self.lobby_tree = ttk.Treeview(self.tab_lobby, columns=lobby_cols, show="tree headings")
        self._configure_lobby_columns(self.lobby_tree)
        self.lobby_tree.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        self.lobby_tree.bind("<Double-1>", lambda _e: self._on_swap_or_trade())

        # TAB 2: All Champions List
        self.tab_all = tk.Frame(self.notebook, bg="#0f172a")
        self.notebook.add(self.tab_all, text="📋 All Champions (0)")

        filter_bar = tk.Frame(self.tab_all, bg="#0f172a", pady=6)
        filter_bar.pack(fill="x", padx=6)

        tk.Label(filter_bar, text="🔍", fg="#cbd5e1", bg="#0f172a",
                 font=("Segoe UI", 10)).pack(side="left", padx=(0, 4))
        search_entry = tk.Entry(filter_bar, textvariable=self.search_var,
                                bg="#1e293b", fg="#ffffff", insertbackground="#ffffff",
                                relief="flat", font=("Segoe UI", 10), width=18)
        search_entry.pack(side="left", padx=(0, 10), ipady=3)
        self.search_var.trace_add("write", lambda *_: self._refresh_all_tree())

        for mode in ("All", "⭐ Need S", "✅ S Earned"):
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

    def _choose_lol_folder(self):
        folder = filedialog.askdirectory(title="Select your 'League of Legends' folder")
        if folder:
            save_lol_dir(folder)
            self.status_lbl.config(text=f"📁 Saved folder: {folder}", fg="#38bdf8")

    def _check_for_updates(self):
        """Check GitHub Releases in the background for a newer version."""
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

                # Rename currently running .exe -> .exe.old and write new .exe
                os.rename(cur_exe, old_exe)
                with open(cur_exe, "wb") as f:
                    f.write(r.content)

                # Strip old PyInstaller temp-folder variables and force a fresh unpack
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

    def _configure_lobby_columns(self, tree):
        tree.heading("#0", text="Champion", anchor="w")
        tree.column("#0", width=185, anchor="w", stretch=True)

        tree.heading("location", text="Holder / Action")
        tree.heading("status", text="S-Grade Status")
        tree.heading("tier", text="ARAM Tier")
        tree.heading("role", text="Primary Role")

        tree.column("location", width=165, anchor="center", stretch=False)
        tree.column("status", width=125, anchor="center", stretch=False)
        tree.column("tier", width=80, anchor="center", stretch=False)
        tree.column("role", width=105, anchor="center", stretch=False)

        tree.tag_configure("need_you", background="#14532d", foreground="#86efac")
        tree.tag_configure("done_you", background="#1e3a8a", foreground="#93c5fd")
        tree.tag_configure("need", background="#1e3a2f", foreground="#4ade80")
        tree.tag_configure("done", background="#1e293b", foreground="#64748b")

    def _configure_all_columns(self, tree):
        tree.heading("#0", text="Champion", anchor="w")
        tree.column("#0", width=220, anchor="w", stretch=True)

        tree.heading("status", text="S-Grade Status")
        tree.heading("tier", text="ARAM Tier")
        tree.heading("role", text="Primary Role")

        tree.column("status", width=145, anchor="center", stretch=False)
        tree.column("tier", width=105, anchor="center", stretch=False)
        tree.column("role", width=125, anchor="center", stretch=False)

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

    def _on_swap_or_trade(self):
        sel = self.lobby_tree.selection()
        if not sel:
            return

        champ_name = self.lobby_tree.item(sel[0], "text").strip()
        entry = self.lobby.get(champ_name)
        if not entry:
            return

        action = entry.get("action")
        cid = entry.get("cid")
        tid = entry.get("tid")

        if action == "self":
            self.status_lbl.config(text=f"ℹ️ You already have {champ_name} equipped!", fg="#38bdf8")
            return
        if not action:
            self.status_lbl.config(text=f"⚠️ Cannot trade/swap {champ_name} right now.", fg="#fbbf24")
            return

        def run_action():
            try:
                _, _, post_req = lcu_client()
                if action == "bench" and cid:
                    post_req(f"/lol-champ-select/v1/session/bench/swap/{cid}")
                    msg = f"✅ Swapped to {champ_name} from the bench!"
                elif action == "trade_acc" and tid is not None:
                    post_req(f"/lol-champ-select/v1/session/champion-swaps/{tid}/accept")
                    msg = f"✅ Accepted trade for {champ_name}!"
                elif action == "trade_req" and tid is not None:
                    post_req(f"/lol-champ-select/v1/session/champion-swaps/{tid}/request")
                    msg = f"📨 Sent trade request for {champ_name}!"
                else:
                    msg = f"⚠️ Trade unavailable for {champ_name}."
                self.root.after(0, lambda m=msg: self.status_lbl.config(text=m, fg="#4ade80"))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.status_lbl.config(
                    text=f"⚠️ Action failed: {err[:45]}", fg="#f87171"))

        threading.Thread(target=run_action, daemon=True).start()

    def _fetch_all_data(self, get_json):
        summary = [c for c in get_json("/lol-game-data/assets/v1/champion-summary.json") if c["id"] > 0]
        challenges = get_json("/lol-challenges/v1/challenges/local-player")

        done_ids = set()
        for c in challenges.values():
            if "all random all champions" in c.get("name", "").lower():
                done_ids.update(c.get("completedIds", []))

        champs = {}
        id_to_name = {}

        for c in summary:
            cid = c["id"]
            name = c["name"]
            completed = cid in done_ids
            tier, static_role = STATIC_DATA.get(name, ("", ""))
            role = static_role or ((c.get("roles") or [""])[0]).capitalize()
            icon_path = c.get("squarePortraitPath") or f"/lol-game-data/assets/v1/champion-icons/{cid}.png"

            id_to_name[cid] = name
            if name not in champs:
                champs[name] = {
                    "id": cid,
                    "done": completed,
                    "tier": tier,
                    "role": role,
                    "icon_path": icon_path
                }
            else:
                champs[name]["done"] = champs[name]["done"] or completed

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
            self.root.after(0, self._refresh_lobby_tree)

    def _fetch_lobby(self, get_json):
        try:
            session = get_json("/lol-champ-select/v1/session")
        except requests.HTTPError as e:
            if e.response is not None and e.response.status_code == 404:
                return None
            raise

        local_cell = session.get("localPlayerCellId", -1)
        swaps_list = session.get("championSwaps") or session.get("trades", [])
        cell_trades = {t.get("cellId"): t for t in swaps_list}
        lobby_map = {}

        bench_ids = [b.get("championId", 0) for b in session.get("benchChampions", [])]
        bench_ids.extend(session.get("benchChampionIds", []))
        for cid in bench_ids:
            if cid in self.id_to_name:
                lobby_map[self.id_to_name[cid]] = {
                    "loc": "🪑 Bench (Grab)",
                    "action": "bench",
                    "cid": cid,
                    "tid": None
                }

        for m in session.get("myTeam", []):
            cell_id = m.get("cellId")
            is_me = (cell_id == local_cell)
            trade_info = cell_trades.get(cell_id, {})
            tid = trade_info.get("id")
            tstate = trade_info.get("state", "")

            cid = m.get("championId", 0)
            intent = m.get("championPickIntent", 0)

            if is_me:
                if cid in self.id_to_name:
                    lobby_map[self.id_to_name[cid]] = {
                        "loc": "👤 You", "action": "self", "cid": cid, "tid": None
                    }
                if intent in self.id_to_name and intent != cid:
                    lobby_map[self.id_to_name[intent]] = {
                        "loc": "👤 You (Hover)", "action": "self", "cid": intent, "tid": None
                    }
            else:
                if tstate == "RECEIVED":
                    loc_label = "👥 Teammate (📩 Accept!)"
                    act = "trade_acc"
                elif tstate == "SENT":
                    loc_label = "👥 Teammate (⏳ Sent)"
                    act = None
                elif tstate == "AVAILABLE" and tid is not None:
                    loc_label = "👥 Teammate (🔄 Trade)"
                    act = "trade_req"
                else:
                    loc_label = "👥 Teammate"
                    act = None

                if cid in self.id_to_name:
                    lobby_map[self.id_to_name[cid]] = {
                        "loc": loc_label, "action": act, "cid": cid, "tid": tid
                    }
                if intent in self.id_to_name and intent != cid:
                    lobby_map[self.id_to_name[intent]] = {
                        "loc": "👥 Teammate (Hover)", "action": None, "cid": intent, "tid": None
                    }

        return lobby_map

    def _poll_loop(self):
        last_sync = 0
        last_lobby = None

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
                    lobby = self._fetch_lobby(get_json)
                    if lobby != last_lobby:
                        self.lobby = lobby or {}
                        last_lobby = lobby
                        self.root.after(0, self._refresh_lobby_tree)

            except FileNotFoundError:
                self.root.after(0, lambda: self.status_lbl.config(
                    text="⏳ Waiting for League client... (or click '📁 Set LoL Folder')", fg="#fbbf24"))
            except Exception as e:
                self.root.after(0, lambda err=str(e): self.status_lbl.config(
                    text=f"⚠️ Client loading ({err[:35]})", fg="#f87171"))

            time.sleep(0.8)

    def _update_dashboard(self):
        total = len(self.champs)
        done = sum(1 for v in self.champs.values() if v["done"])
        rem = total - done
        pct = (done / total * 100) if total else 0

        self.status_lbl.config(text="🟢 Connected to League Client", fg="#4ade80")
        self.progress_lbl.config(text=f"✅ {done} Earned  |  ⭐ {rem} Left ({pct:.1f}%)")

        cur_tier, cur_pts = "Unranked", 0
        next_target, next_tier, next_pts = None, None, None

        for req_count, tier_name, pts in MILESTONES:
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
                text=f"👑 Max Milestone (Master 150) Reached! ({rem} left for 100%)"
            )

        self.notebook.tab(1, text=f"📋 All Champions ({total})")
        self._refresh_all_tree()
        self._refresh_lobby_tree()

    def _refresh_lobby_tree(self):
        selected_champ = None
        sel = self.lobby_tree.selection()
        if sel:
            selected_champ = self.lobby_tree.item(sel[0], "text").strip()

        self.lobby_tree.delete(*self.lobby_tree.get_children())
        self.notebook.tab(0, text=f"🎯 Live ARAM Lobby ({len(self.lobby)})")

        if not self.lobby:
            self.lobby_banner.config(
                text="Not in Champ Select — Enter an ARAM lobby to scan automatically!",
                fg="#94a3b8"
            )
            return

        sorted_lobby = sorted(
            self.lobby.keys(),
            key=lambda n: (
                self.champs.get(n, {}).get("done", False),
                location_priority(self.lobby[n]["loc"]),
                TIER_ORDER.get(self.champs.get(n, {}).get("tier", ""), 5),
                n
            )
        )

        need_count = 0
        my_champ_summary = ""

        for name in sorted_lobby:
            info = self.champs.get(name, {"done": False, "tier": "", "role": ""})
            loc = self.lobby[name]["loc"]
            is_done = info["done"]
            if not is_done:
                need_count += 1

            status_txt = "✅ S Earned" if is_done else "⭐ NEED S"
            if loc.startswith("👤 You"):
                tag = "done_you" if is_done else "need_you"
                my_champ_summary = f"👤 {name} ({status_txt})  •  "
            else:
                tag = "done" if is_done else "need"

            icon = self._get_tk_icon(name)

            item_id = self.lobby_tree.insert(
                "", "end",
                text=f"  {name}",
                image=icon,
                values=(loc, status_txt, info["tier"], info["role"]),
                tags=(tag,)
            )
            if name == selected_champ:
                self.lobby_tree.selection_set(item_id)

        self.lobby_banner.config(
            text=f"{my_champ_summary}⭐ {need_count} Need S  •  ✅ {len(self.lobby) - need_count} Mastered",
            fg="#4ade80" if need_count > 0 else "#38bdf8"
        )
        self.notebook.select(0)

    def _refresh_all_tree(self):
        self.all_tree.delete(*self.all_tree.get_children())
        query = self.search_var.get().strip().lower()
        mode = self.filter_var.get()

        for name in sorted(self.champs.keys()):
            info = self.champs[name]
            is_done = info["done"]

            if mode == "⭐ Need S" and is_done:
                continue
            if mode == "✅ S Earned" and not is_done:
                continue
            if query and query not in name.lower() and query not in info["role"].lower():
                continue

            status_txt = "✅ S Earned" if is_done else "⭐ NEED S"
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