# ⚔️ Aram-S-Tracker

A lightweight, local desktop application for League of Legends designed to track your **All Random All Champions** (`S-` or higher) and **Perfectionist** (`S+` only) challenge progress, monitor your capstone milestone points, and scan active **ARAM** and **Summoner's Rift** Champ Select lobbies in real-time.

---

<p align="center">
    <img width="1079" height="1656" alt="1-4-3 aram" src="https://github.com/user-attachments/assets/641f15f8-875a-4b60-949a-024d7eb581dc" />

</p>

---

## ✨ Features

* **Automatic Game Mode & Challenge Switching:**
  * **ARAM & ARAM Mayhem:** Automatically tracks **All Random All Champions** (`NEED S` / `S EARNED`).
  * **Summoner's Rift (Normal, Draft, Swiftplay, Ranked Solo/Duo & Flex):** Automatically switches to track **Perfectionist** (`NEED S+` / `S+ EARNED`). You can also toggle between modes manually at any time using the top segmented mode selector.
* **Split-Pane Live Lobby Scanner:** Mirrors the League Client layout with **Your Team** on the left (displaying teammates' Riot IDs, assigned lanes, local `[YOU]` highlight, and live trade indicators like `[TRADE]`, `[REQUEST SENT]`, and `[ACCEPT TRADE]`) and the **Reroll Bench / SR Lane Pool** on the right.
* **Smart Summoner's Rift Lane Pool:** Automatically detects your assigned lane (`Top`, `Jungle`, `Mid`, `Bot`, `Support`) in Summoner's Rift lobbies and lists champions for your role sorted with `NEED S+` at the top. Includes segmented lane filter pills (`AUTO`, `TOP`, `JG`, `MID`, `BOT`, `SUP`, `ALL`), instant search bar, and live `[BANNED]` / `[PICKED]` indicators in Draft.
* **1-Click Bench Swap, Trade & SR Hover:**
  * **In ARAM:** Double-click any champion on the reroll bench to grab it immediately, or double-click a teammate to request/accept a champion trade.
  * **In Summoner's Rift:** Double-click any available champion in the Lane Pool to hover/select it directly in Champ Select.
* **Hero Milestone & Progress Card:** Displays your current challenge milestone rank (`Iron` through `Master`) with dynamic tier color badges, capstone points, a custom Hextech Progress Bar, and exact champion targets to reach the next tier.
* **Auto-Detects League Installation:** Automatically locates your `League of Legends` directory across any drive using Riot Client metadata—no manual path setup required (includes a fallback **LoL Folder** button for custom setups).
* **Always-on-Top Floating Mode:** Pin the window so it stays visible right next to your League Client during Champ Select.
* **Built-in Auto-Updater:** Checks GitHub Releases on launch and updates itself to the latest `.exe` with a single click.
* **100% Safe:** Connects exclusively to the local League Client Update (LCU) API via standard client endpoints.

---

## 📥 Installation & Usage

1. Head over to the **[Releases](../../releases)** page of this repository.
2. Download the latest **`ARAM S Tracker.exe`** binary.
3. Double-click the `.exe` whenever you play League (no Python installation or setup required).
4. *(Optional)* If your League client is installed in a non-standard portable directory, click the **📁 Set LoL Folder** button once to select your `League of Legends` folder.

---

## 📦 Building the `.exe` with PyInstaller

To compile a standalone `.exe` locally (excluding heavy optional packages to keep the file size small), run:

```bash
pyinstaller --noconfirm --clean --onefile --noconsole --exclude-module numpy --exclude-module pandas --exclude-module scipy --exclude-module matplotlib --exclude-module cryptography --icon="coolcat.ico" --name "ARAM S Tracker" aram_gui.py
```

---

## 🛠️ Built With

* **Python** (Tkinter GUI & Requests)
* **Pillow (PIL)** for real-time LCU champion portrait rendering
* **PyInstaller** for standalone executable compilation

---

<p align="center">
  <img width="944" height="697" alt="readmescreenshot" src="https://github.com/user-attachments/assets/9bf15296-74fb-45d1-96a8-5c30b23e3666" />
</p>
<p align="center">
  <img width="715" height="695" alt="png for readme" src="https://github.com/user-attachments/assets/81fb5a39-7ae6-480a-829c-733d12855c12" />
</p>
