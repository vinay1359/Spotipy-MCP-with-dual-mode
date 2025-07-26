from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.progress import Progress
from time import sleep
import asyncio

from server import SpotifyMCPServer

console = Console()
server = SpotifyMCPServer()

async def run_cli():
    await server.authenticate_spotify()
    
    while True:
        console.clear()
        console.print(Panel("Spotify-MCP CLI", style="bold green"), justify="center")

        menu = [
            "Authenticate Spotify",
            "Play a Song",
            "Pause Playback",
            "Resume Playback",
            "Next Track",
            "Previous Track",
            "Set Volume",
            "Create Playlist",
            "Add to Playlist",
            "Search Songs",
            "Show Current Playback",
            "List Playlists",
            "Exit"
        ]

        for i, item in enumerate(menu, 1):
            console.print(f"[{i}] {item}")
        
        choice = IntPrompt.ask("\nChoose an option")

        if choice == 1:
            result = await server.authenticate_spotify()
        elif choice == 2:
            title = Prompt.ask("Enter song title")
            artist = Prompt.ask("Enter artist (optional)", default="")
            result = await server.play_song(title, artist if artist else None)
        elif choice == 3:
            result = await server.pause_playback()
        elif choice == 4:
            result = await server.resume_playback()
        elif choice == 5:
            result = await server.skip_track()
        elif choice == 6:
            result = await server.previous_track()
        elif choice == 7:
            vol = IntPrompt.ask("Volume (0-100)", default=50)
            result = await server.set_volume(vol)
        elif choice == 8:
            name = Prompt.ask("Playlist name")
            pub = Prompt.ask("Make public? (yes/no)", choices=["yes", "no"], default="yes")
            result = await server.create_playlist(name, pub == "yes")
        elif choice == 9:
            song = Prompt.ask("Song title")
            playlist = Prompt.ask("Playlist name")
            artist = Prompt.ask("Artist (optional)", default="")
            result = await server.add_to_playlist(song, playlist, artist if artist else None)
        elif choice == 10:
            query = Prompt.ask("Search query")
            stype = Prompt.ask("Type (track, artist, album, playlist)", choices=["track", "artist", "album", "playlist"], default="track")
            limit = IntPrompt.ask("Limit (1-50)", default=5)
            result = await server.search_songs(query, stype, limit)
        elif choice == 11:
            result = await server.get_current_playback_info()
        elif choice == 12:
            result = await server.get_user_playlists()
        elif choice == 13:
            console.print("Exiting...", style="bold red")
            break
        else:
            result = ["Invalid option"]

        for res in result:
            if hasattr(res, "text") and not isinstance(res, str) and getattr(res, "text") is not None:
                console.print(res.text, style="bold cyan")
            else:
                console.print(str(res), style="bold cyan")
        
        input("\nPress Enter to return to menu...")
