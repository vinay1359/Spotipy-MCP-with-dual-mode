# Spotify-MCP

A command-line and Claude-compatible tool server for controlling Spotify playback using Python.  
Built with spotipy, aiohttp, and rich for a clean CLI and AI-integrated experience.

---

## 🔹 Features

- Authenticate with Spotify via OAuth
- Play, pause, skip, or resume tracks
- Control volume and playback
- Search songs, artists, albums, or playlists
- Create and manage your own playlists
- Get current playback info
- Claude (or other LLMs) can call all features via MCP

---

## 🔹 Modes of Operation

This project supports two modes:

### 1. Manual CLI Mode

Launches a full-featured terminal UI with a clean menu system:

```bash
python server.py --mode=manual
```

You’ll see a menu like:

```
1. Authenticate Spotify
2. Play a Song
3. Pause Playback
...
13. Exit
```

### 2. AI Mode (Claude Desktop / LangChain / OpenAI)

Runs the MCP tool server that allows Claude or other agents to call your tools:

```bash
python server.py --mode=ai
```

---

## 🔹 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Example `requirements.txt`:

```
spotipy
aiohttp
rich
```

---

## 🔹 Environment Variables

Set the following environment variables (in `.env` or system environment):

```
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
```

Create these credentials at:  
https://developer.spotify.com/dashboard

---

## 🔹 Project Structure

```
spotify-mcp/
├── server.py         # MCP tool server (Claude + CLI backend)
├── main.py           # CLI interactive mode
├── README.md
├── requirements.txt
├── .gitignore
```

---

## 🔹 Claude Tool Call Example

```json
{
  "tool_name": "create_playlist",
  "arguments": {
    "playlist_name": "Late Night Coding",
    "public": false
  }
}
```

The server will create a playlist instantly using the Spotify Web API.

---

## 🔹 Git Ignore Setup

```
# Python
__pycache__/
*.py[cod]
*.log

# Envs
.venv/
.env
*.cache
.spotify_mcp_cache

# Editor & OS
.vscode/
.DS_Store
Thumbs.db
```

---

## 🔹 License

MIT License.

Free to use, modify, and distribute with credit.

---

## 🔹 Author

Built by [Your Name]  
Designed for AI automation and terminal productivity.

---

## 🔹 Final Words

Spotify-MCP is minimal by design, but powerful in capability.  
Whether you're controlling playback through Claude or managing music directly from the terminal — this project gives you the freedom and flow you need.
