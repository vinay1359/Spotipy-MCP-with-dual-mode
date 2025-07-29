# Spotipy MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/license/mit/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-green)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![Mode](https://img.shields.io/badge/Mode-CLI%20%7C%20AI-green)](#)
[![Spotipy](https://img.shields.io/badge/Library-Spotipy%202.22-brightgreen)](https://spotipy.readthedocs.io/en/2.22.1/)
[![PRs](https://img.shields.io/badge/PRs-Welcome-green)](CONTRIBUTING.md)

---

**Spotipy MCP Server** is a dual-mode tool server for controlling Spotify through your terminal or via AI assistants like Claude or ChatGPT.

Built in Python using `spotipy`, `aiohttp`, and `rich`, it supports both real-time manual use and seamless AI integration.

---

## 🎵 Supported Features

| Feature                     | Description                              | Free Account | Premium Required |
|----------------------------|------------------------------------------|--------------|------------------|
| Spotify Authentication     | OAuth login using client credentials     | ✅            | ✅                |
| Search (songs, albums, etc)| Search Spotify catalog                   | ✅            | ✅                |
| Get Playback Info          | Current track, device, status info       | ✅            | ✅                |
| View Playlists             | Fetch user playlists                     | ✅            | ✅                |
| Create Playlist            | Create a new playlist                    | ✅            | ✅                |
| Add to Playlist            | Add tracks to an existing playlist       | ✅            | ✅                |
| Play Song                  | Start playing a specific song            | ❌            | ✅                |
| Pause / Resume Playback    | Pause or resume music                    | ❌            | ✅                |
| Skip / Previous Track      | Skip to next or previous song            | ❌            | ✅                |
| Set Volume                 | Adjust playback volume                   | ❌            | ✅                |

---

## 🚀 Modes of Operation

### 1. Manual Mode (CLI)

```bash
python server.py --mode=manual
```

Launches an animated terminal UI to control your Spotify account without using the app.

### 2. AI Mode (Claude / ChatGPT / LangChain)

```bash
python server.py --mode=ai
```

Enables MCP tool server mode, allowing an AI agent to send structured tool calls and control your playback.

---

## ⚙️ Installation & Setup

### Requirements

- Python 3.9+
- Spotify Developer credentials (Client ID, Secret)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment

Create a `.env` file in your root directory:

```dotenv
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

[Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

---

## 🗂️ Project Structure

```
spotipy-mcp-server/
├── server.py         # Main CLI + AI server
├── main.py           # Interactive terminal interface
├── requirements.txt  # Dependencies
├── .gitignore
├── README.md
└── .env              # (ignored)
```

---

## 🔧 Commands

| Command | Description |
|---------|-------------|
| `python server.py --mode=manual` | Launch terminal UI |
| `python server.py --mode=ai`     | Start MCP server for AI |

---

## 📄 License

This project is open source and dual-licensed:

- **MIT License** — [opensource.org/license/mit](https://opensource.org/license/mit/)
- **Apache 2.0 License** — [apache.org/licenses/LICENSE-2.0](https://www.apache.org/licenses/LICENSE-2.0)

Use it freely with attribution. Choose the license that fits your use case best.


<div align="center">
  <strong>Star this repo if Spotipy MCP made your Spotify experience smarter.</strong>
</div>
