# Spotipy MCP Server

<p align="center">
  <img src="https://via.placeholder.com/800x200?text=Trackcraft+MCP+Server" alt="Trackcraft Banner" width="100%" />
  <h1 align="center">Spotipy MCP Server</h1>
  <p align="center"><i>AI-ready Spotify controller for CLI and Claude integration</i></p>
</p>


[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/license/mit/)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![CLI Support](https://img.shields.io/badge/Mode-CLI%20%7C%20AI-green)](#)
[![Spotify](https://img.shields.io/badge/Library-spotify-green)](https://spotipy.readthedocs.io/en/2.22.1/)
[![PRs](https://img.shields.io/badge/PRs-Welcome-brightgreen.svg)](CONTRIBUTING.md)

**Spotipy** is a dual-mode Spotify control server built in Python. It provides:
- a rich, animated command-line interface for manual control
- a Machine Control Protocol (MCP) interface for AI agents like Claude or ChatGPT

---

## Features

- Spotify authentication via OAuth
- Play/pause/resume/skip music
- Set playback volume
- Search music by track, artist, album, or playlist
- View current playback status
- Create and modify user playlists
- Use manually (CLI) or automatically (AI tool calls)

---

## Modes of Operation

### 1. CLI Mode (Manual Control)
```bash
python server.py --mode=manual
```
You’ll see an interactive menu that lets you:
- Play songs
- Search tracks
- Create playlists
- And more

### 2. AI Mode (Claude/Desktop MCP)
```bash
python server.py --mode=ai
```
---

## Setup & Installation

### Requirements
- Python 3.9+
- Spotify Developer Credentials

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Environment Variables
Create a `.env` file:
```dotenv
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```
[Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

---

## Project Structure
```
trackcraft/
├── server.py           # MCP Server (AI + CLI entry)
├── main.py             # CLI interface logic
├── requirements.txt
├── README.md
├── .gitignore
└── .env (not committed)
```

---

## Development Scripts

| Command                | Description                       |
|------------------------|-----------------------------------|
| `python server.py --mode=manual` | Run CLI menu                  |
| `python server.py --mode=ai`     | Start Claude-compatible MCP   |

---

## License

This project is licensed under the **MIT License**. See full text at [MIT license](https://opensource.org/license/mit/)

This project is licensed under the Apache 2.0 License, offering broad permissions with clear conditions.Read more at [Apache 2.0 License](https://apache.org/licenses/LICENSE-2.0)



<div align="center">
  <strong>Star this repo if Spotipy made your music smarter.</strong>
</div>
