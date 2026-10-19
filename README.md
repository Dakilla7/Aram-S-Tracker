# Aram-S-Tracker

A lightweight, local desktop application for League of Legends designed to track your **All Random All Champions** challenge progress, monitor your capstone milestone points, and scan active ARAM Champ Select lobbies in real-time.

---
<img width="715" height="695" alt="png for readme" src="https://github.com/user-attachments/assets/81fb5a39-7ae6-480a-829c-733d12855c12" />


## ✨ Features

* **🎯 Live ARAM Lobby Scanner:** Automatically detects when you enter Champ Select, scanning your team and reroll bench within seconds.
* **⭐ Priority Sorting & Status:** Instantly flags which champions you still need an S-grade on (`⭐ NEED S`) versus ones you’ve already mastered (`✅ S Earned`), sorted by ARAM Tier (`S+` down to `C`).
* **⚡ 1-Click Bench Swapping & Trading:** Double-click any champion on the reroll bench to instantly swap to it, or double-click a teammate's pick to send/accept a trade.
* **🏆 Milestone & Point Tracker:** Displays your current challenge milestone rank, capstone points, and exactly how many S-grades you need to reach the next tier.
* **📌 Always-on-Top Floating Mode:** Pin the window so it stays visible right next to your game client during Champ Select.
* **🚀 Built-in Auto-Updater:** Automatically checks GitHub for new releases and updates itself with a single click.
* **🔒 100% Safe:** Connects exclusively to the local League Client Update (LCU) API via read-only endpoints and manual UI triggers. Fully compliant with Riot's third-party application policies.

---

## 📥 Installation & Usage

1. Head over to the **[Releases](../../releases)** page of this repository.
2. Download the latest **`ARAM S Tracker.exe`** binary.
3. Double-click the `.exe` whenever you play League (no Python installation or setup required).
4. *(Optional)* If your League client is installed in a custom directory, click the **📁 Set LoL Folder** button in the app to point it to your `League of Legends` installation directory.

---

## 🛠️ Built With

* **Python** (Tkinter GUI & Requests)
* **Pillow (PIL)** for real-time LCU champion portrait rendering
* **PyInstaller** for standalone executable compilation

