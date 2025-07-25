import asyncio
import logging
import os
import sys
from typing import Any, Dict, List, Optional
import webbrowser
import aiohttp
from aiohttp import web
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("spotify-mcp")

class SpotifyMCPServer:
    def __init__(self):
        self.server = Server("spotify-mcp")
        self.spotify_client: Optional[spotipy.Spotify] = None
        self.auth_manager: Optional[SpotifyOAuth] = None
        self.callback_server = None
        self.callback_server_task = None
        self.setup_auth()
        self.setup_handlers()

    def setup_auth(self):
        """Setup Spotify OAuth authentication"""
        client_id = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
        redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://[::1]:8888/callback")
        
        if not client_id or not client_secret:
            raise ValueError("SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set")

        # Scopes needed for all functionality
        scope = " ".join([
            "user-read-playback-state",
            "user-modify-playback-state", 
            "user-read-currently-playing",
            "playlist-read-private",
            "playlist-read-collaborative",
            "playlist-modify-public",
            "playlist-modify-private",
            "user-library-read",
            "user-library-modify",
            "streaming"
        ])

        self.auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=scope,
            cache_path=os.path.expanduser("~/.spotify_mcp_cache")
        )

        # Try to get existing token
        token_info = self.auth_manager.get_cached_token()
        if token_info:
            self.spotify_client = spotipy.Spotify(auth_manager=self.auth_manager)
            logger.info("Successfully authenticated with cached token")
        else:
            logger.info("No cached token found. Authentication required.")


    async def start_callback_server(self):
        """Start the OAuth callback server"""
        app = web.Application()
        app.router.add_get('/callback', self.handle_callback)
        
        runner = web.AppRunner(app)
        await runner.setup()
        
        # Try to bind to [::1] first, then localhost if that fails
        site = None
        try:
            site = web.TCPSite(runner, '::1', 8888)
            await site.start()
            logger.info("OAuth callback server started on http://[::1]:8888")
        except Exception as e:
            logger.warning(f"Failed to bind to [::1]:8888: {e}")
            try:
                site = web.TCPSite(runner, 'localhost', 8888)
                await site.start()
                logger.info("OAuth callback server started on http://localhost:8888")
            except Exception as e2:
                logger.error(f"Failed to start callback server: {e2}")
                return None
        
        return runner

    async def handle_callback(self, request):
        """Handle OAuth callback"""
        try:
            query_params = dict(request.query)
            
            if 'code' in query_params:
                # Exchange code for token
                code = query_params['code']
                if not self.auth_manager:
                    logger.error("Spotify authentication manager is not initialized.")
                    return web.Response(text="❌ Spotify authentication manager is not initialized. Check your client ID/secret.", status=400)
                token_info = self.auth_manager.get_access_token(code)
                
                if token_info:
                    self.spotify_client = spotipy.Spotify(auth_manager=self.auth_manager)
                    logger.info("Successfully authenticated via callback!")
                    
                    # Get user info
                    try:
                        user = self.spotify_client.current_user()
                        user_name = user.get('display_name', user.get('id', 'Unknown')) if user else 'Unknown'
                        success_msg = f"✅ Successfully authenticated as {user_name}!"
                    except:
                        success_msg = "✅ Successfully authenticated!"
                    
                    return web.Response(
                        text=f"""
                        <html>
                        <body>
                        <h2>{success_msg}</h2>
                        <p>You can now close this window and return to the chat.</p>
                        <script>setTimeout(() => window.close(), 3000);</script>
                        </body>
                        </html>
                        """,
                        content_type='text/html'
                    )
                else:
                    return web.Response(text="❌ Failed to get access token", status=400)
            
            elif 'error' in query_params:
                error = query_params.get('error', 'unknown_error')
                return web.Response(text=f"❌ Authentication error: {error}", status=400)
            
            else:
                return web.Response(text="❌ Invalid callback request", status=400)
                
        except Exception as e:
            logger.error(f"Callback error: {e}")
            return web.Response(text=f"❌ Callback error: {str(e)}", status=500)

    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """List available Spotify tools"""
            return [
                Tool(
                    name="authenticate_spotify",
                    description="Authenticate with Spotify (run this first)",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="play_song",
                    description="Play a specific song by title and optional artist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "song_title": {"type": "string", "description": "Title of the song"},
                            "artist": {"type": "string", "description": "Artist name (optional for better accuracy)"}
                        },
                        "required": ["song_title"]
                    }
                ),
                Tool(
                    name="pause_playback",
                    description="Pause current playback",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="resume_playback", 
                    description="Resume paused playback",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="skip_track",
                    description="Skip to the next track",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="previous_track",
                    description="Go back to the previous track", 
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="set_volume",
                    description="Set playback volume (0-100)",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "volume_percent": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Volume level 0-100"}
                        },
                        "required": ["volume_percent"]
                    }
                ),
                Tool(
                    name="create_playlist",
                    description="Create a new playlist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "playlist_name": {"type": "string", "description": "Name of the new playlist"},
                            "public": {"type": "boolean", "description": "Make playlist public (default: true)"}
                        },
                        "required": ["playlist_name"]
                    }
                ),
                Tool(
                    name="add_to_playlist",
                    description="Add a song to an existing playlist",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "song_title": {"type": "string", "description": "Title of the song to add"},
                            "playlist_name": {"type": "string", "description": "Name of the playlist"},
                            "artist": {"type": "string", "description": "Artist name (optional for better accuracy)"}
                        },
                        "required": ["song_title", "playlist_name"]
                    }
                ),
                Tool(
                    name="get_current_playback_info",
                    description="Get information about current playback and song",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="search_songs",
                    description="Search for songs, albums, or artists",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "search_type": {"type": "string", "enum": ["track", "album", "artist", "playlist"], "description": "Type of search"},
                            "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Number of results (default: 10)"}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_user_playlists",
                    description="Get user's playlists",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
            """Handle tool calls"""
            
            if name == "authenticate_spotify":
                return await self.authenticate_spotify()
            
            # Check if authenticated for other operations
            if not self.spotify_client:
                return [types.TextContent(
                    type="text",
                    text="❌ Not authenticated. Please run 'authenticate_spotify' first."
                )]

            try:
                if name == "play_song":
                    song_title = arguments.get("song_title")
                    if not isinstance(song_title, str) or not song_title.strip():
                        return [types.TextContent(type="text", text="❌ 'song_title' is required and must be a non-empty string.")]
                    return await self.play_song(song_title, arguments.get("artist"))
                elif name == "pause_playback":
                    return await self.pause_playback()
                elif name == "resume_playback":
                    return await self.resume_playback()
                elif name == "skip_track":
                    return await self.skip_track()
                elif name == "previous_track":
                    return await self.previous_track()
                elif name == "set_volume":
                    volume_percent = arguments.get("volume_percent")
                    if volume_percent is None or not isinstance(volume_percent, int):
                        return [types.TextContent(type="text", text="❌ 'volume_percent' is required and must be an integer between 0 and 100.")]
                    return await self.set_volume(volume_percent)
                elif name == "create_playlist":
                    playlist_name = arguments.get("playlist_name")
                    if not isinstance(playlist_name, str) or not playlist_name.strip():
                        return [types.TextContent(type="text", text="❌ 'playlist_name' is required and must be a non-empty string.")]
                    public = arguments.get("public", True)
                    return await self.create_playlist(playlist_name, public)
                elif name == "add_to_playlist":
                    song_title = arguments.get("song_title")
                    playlist_name = arguments.get("playlist_name")
                    artist = arguments.get("artist")
                    if not isinstance(song_title, str) or not song_title.strip():
                        return [types.TextContent(type="text", text="❌ 'song_title' is required and must be a non-empty string.")]
                    if not isinstance(playlist_name, str) or not playlist_name.strip():
                        return [types.TextContent(type="text", text="❌ 'playlist_name' is required and must be a non-empty string.")]
                    return await self.add_to_playlist(song_title, playlist_name, artist)
                elif name == "get_current_playback_info":
                    return await self.get_current_playback_info()
                elif name == "search_songs":
                    query = arguments.get("query")
                    if not isinstance(query, str) or not query.strip():
                        return [types.TextContent(type="text", text="❌ 'query' is required and must be a non-empty string.")]
                    search_type = arguments.get("search_type", "track")
                    limit = arguments.get("limit", 10)
                    if not isinstance(limit, int) or limit < 1 or limit > 50:
                        limit = 10
                    return await self.search_songs(query, search_type, limit)
                elif name == "get_user_playlists":
                    return await self.get_user_playlists()
                else:
                    return [types.TextContent(type="text", text=f"❌ Unknown tool: {name}")]
                    
            except Exception as e:
                logger.error(f"Error executing {name}: {e}")
                return [types.TextContent(type="text", text=f"❌ Error: {str(e)}")]

    async def authenticate_spotify(self) -> List[types.TextContent]:
        """Handle Spotify authentication"""
        try:
            if self.spotify_client:
                # Test current authentication
                try:
                    user = self.spotify_client.current_user()
                    display_name = user.get('display_name') if user else None
                    user_id = user.get('id') if user else None
                    if display_name and user_id:
                        msg = f"✅ Already authenticated as {display_name} ({user_id})"
                    elif user_id:
                        msg = f"✅ Already authenticated as user ID: {user_id}"
                    else:
                        msg = "✅ Already authenticated."
                    return [types.TextContent(
                        type="text",
                        text=msg
                    )]
                except:
                    pass

            # Start callback server if not already running
            if not self.callback_server:
                self.callback_server = await self.start_callback_server()
                if not self.callback_server:
                    return [types.TextContent(type="text", text="❌ Failed to start OAuth callback server")]

            # Start authentication flow
            if not self.auth_manager:
                return [types.TextContent(type="text", text="❌ Spotify authentication manager is not initialized. Check your client ID/secret.")]
            
            auth_url = self.auth_manager.get_authorize_url()
            webbrowser.open(auth_url)
            
            return [types.TextContent(
                type="text", 
                text=f"🔐 Opening browser for Spotify authentication...\n\nIf browser doesn't open, visit:\n{auth_url}\n\nAfter authorization, the server will automatically receive the token."
            )]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Authentication error: {str(e)}")]


    async def play_song(self, song_title: str, artist: Optional[str] = None) -> List[types.TextContent]:
        """Play a specific song"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            # Build search query
            query = song_title
            if artist:
                query += f" artist:{artist}"
            # Search for the track
            results = self.spotify_client.search(q=query, type='track', limit=1)
            if not results or not results.get('tracks') or not results['tracks'].get('items'):
                return [types.TextContent(type="text", text=f"❌ No tracks found for '{song_title}'" + (f" by {artist}" if artist else ""))]
            track = results['tracks']['items'][0]
            track_uri = track['uri']
            track_name = track['name']
            track_artist = ', '.join([artist['name'] for artist in track['artists']])
            # Play the track
            self.spotify_client.start_playback(uris=[track_uri])
            return [types.TextContent(
                type="text",
                text=f"🎵 Now playing: {track_name} by {track_artist}"
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error playing song: {str(e)}")]

    async def pause_playback(self) -> List[types.TextContent]:
        """Pause current playback"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            self.spotify_client.pause_playback()
            return [types.TextContent(type="text", text="⏸️ Playback paused")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error pausing: {str(e)}")]

    async def resume_playback(self) -> List[types.TextContent]:
        """Resume paused playback"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            self.spotify_client.start_playback()
            return [types.TextContent(type="text", text="▶️ Playback resumed")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error resuming: {str(e)}")]

    async def skip_track(self) -> List[types.TextContent]:
        """Skip to next track"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            self.spotify_client.next_track()
            # Wait a moment and get current track info
            await asyncio.sleep(1)
            current = self.spotify_client.current_playback()
            if current and current.get('item'):
                track_name = current['item']['name']
                artists = ', '.join([artist['name'] for artist in current['item']['artists']])
                return [types.TextContent(type="text", text=f"⏭️ Skipped to: {track_name} by {artists}")]
            else:
                return [types.TextContent(type="text", text="⏭️ Skipped to next track")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error skipping: {str(e)}")]

    async def previous_track(self) -> List[types.TextContent]:
        """Go to previous track"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            self.spotify_client.previous_track()
            # Wait a moment and get current track info
            await asyncio.sleep(1)
            current = self.spotify_client.current_playback()
            if current and current.get('item'):
                track_name = current['item']['name']
                artists = ', '.join([artist['name'] for artist in current['item']['artists']])
                return [types.TextContent(type="text", text=f"⏮️ Previous track: {track_name} by {artists}")]
            else:
                return [types.TextContent(type="text", text="⏮️ Went to previous track")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error going to previous track: {str(e)}")]

    async def set_volume(self, volume_percent: int) -> List[types.TextContent]:
        """Set playback volume"""
        try:
            if volume_percent is None or not isinstance(volume_percent, int):
                return [types.TextContent(type="text", text="❌ 'volume_percent' must be an integer between 0 and 100")]
            if not 0 <= volume_percent <= 100:
                return [types.TextContent(type="text", text="❌ Volume must be between 0 and 100")]
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            self.spotify_client.volume(volume_percent)
            return [types.TextContent(type="text", text=f"🔊 Volume set to {volume_percent}%")]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error setting volume: {str(e)}")]

    async def create_playlist(self, playlist_name: str, public: bool = True) -> List[types.TextContent]:
        """Create a new playlist"""
        try:
            if not playlist_name or not isinstance(playlist_name, str):
                return [types.TextContent(type="text", text="❌ 'playlist_name' must be a non-empty string")]
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            user = self.spotify_client.current_user()
            if not user or 'id' not in user:
                return [types.TextContent(type="text", text="❌ Could not retrieve user information. Please ensure you are authenticated.")]
            playlist = self.spotify_client.user_playlist_create(
                user=user['id'],
                name=playlist_name,
                public=public
            )
            if not playlist or 'id' not in playlist:
                return [types.TextContent(type="text", text="❌ Failed to create playlist. No playlist information returned.")]
            return [types.TextContent(
                type="text",
                text=f"✅ Created {'public' if public else 'private'} playlist: {playlist_name}\nPlaylist ID: {playlist['id']}"
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error creating playlist: {str(e)}")]

    async def add_to_playlist(self, song_title: str, playlist_name: str, artist: Optional[str] = None) -> List[types.TextContent]:
        """Add a song to a playlist"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            if not song_title or not isinstance(song_title, str):
                return [types.TextContent(type="text", text="❌ 'song_title' must be a non-empty string")]
            if not playlist_name or not isinstance(playlist_name, str):
                return [types.TextContent(type="text", text="❌ 'playlist_name' must be a non-empty string")]
            # Find the playlist
            playlists = self.spotify_client.current_user_playlists()
            if not playlists or not playlists.get('items'):
                return [types.TextContent(type="text", text="❌ Could not retrieve playlists")]
            target_playlist = None
            for playlist in playlists['items']:
                if playlist.get('name', '').lower() == playlist_name.lower():
                    target_playlist = playlist
                    break
            if not target_playlist:
                return [types.TextContent(type="text", text=f"❌ Playlist '{playlist_name}' not found")]
            # Search for the song
            query = song_title
            if artist:
                query += f" artist:{artist}"
            results = self.spotify_client.search(q=query, type='track', limit=1)
            if not results or not results.get('tracks') or not results['tracks'].get('items'):
                return [types.TextContent(type="text", text=f"❌ Song '{song_title}' not found")]
            track = results['tracks']['items'][0]
            track_uri = track['uri']
            track_name = track['name']
            track_artist = ', '.join([artist['name'] for artist in track['artists']])
            # Add to playlist
            self.spotify_client.playlist_add_items(target_playlist['id'], [track_uri])
            return [types.TextContent(
                type="text",
                text=f"✅ Added '{track_name}' by {track_artist} to playlist '{playlist_name}'"
            )]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error adding to playlist: {str(e)}")]

    async def get_current_playback_info(self) -> List[types.TextContent]:
        """Get current playback information"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            current = self.spotify_client.current_playback()
            if not current:
                return [types.TextContent(type="text", text="🔇 No active playback")]
            if not current.get('item'):
                return [types.TextContent(type="text", text="🔇 No track currently playing")]
            track = current['item']
            artists = ', '.join([artist['name'] for artist in track['artists']])
            album = track['album']['name']
            # Format duration and progress
            duration_ms = track['duration_ms']
            progress_ms = current.get('progress_ms', 0)
            duration_min = duration_ms // 60000
            duration_sec = (duration_ms % 60000) // 1000
            progress_min = progress_ms // 60000
            progress_sec = (progress_ms % 60000) // 1000
            # Playback state
            is_playing = current['is_playing']
            device = current.get('device', {})
            volume = device.get('volume_percent', 'Unknown')
            info = f"""🎵 **Currently {'Playing' if is_playing else 'Paused'}:**
**Track:** {track['name']}
**Artist:** {artists}
**Album:** {album}
**Progress:** {progress_min}:{progress_sec:02d} / {duration_min}:{duration_sec:02d}
**Volume:** {volume}%
**Device:** {device.get('name', 'Unknown')}
**Shuffle:** {'On' if current.get('shuffle_state') else 'Off'}
**Repeat:** {current.get('repeat_state', 'off').title()}"""
            return [types.TextContent(type="text", text=info)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error getting playback info: {str(e)}")]

    async def search_songs(self, query: str, search_type: str = "track", limit: int = 10) -> List[types.TextContent]:
        """Search for songs, albums, artists, or playlists"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            if not query or not isinstance(query, str):
                return [types.TextContent(type="text", text="❌ 'query' must be a non-empty string")]
            results = self.spotify_client.search(q=query, type=search_type, limit=limit)
            if not results:
                return [types.TextContent(type="text", text=f"❌ No results found for '{query}'")]
            if search_type == "track":
                items = results.get('tracks', {}).get('items', [])
                if not items:
                    return [types.TextContent(type="text", text=f"❌ No tracks found for '{query}'")]
                result_text = f"🔍 **Found {len(items)} track(s) for '{query}':**\n\n"
                for i, track in enumerate(items, 1):
                    artists = ', '.join([artist['name'] for artist in track['artists']])
                    result_text += f"{i}. **{track['name']}** by {artists}\n"
                    result_text += f"   Album: {track['album']['name']}\n\n"
            elif search_type == "artist":
                items = results.get('artists', {}).get('items', [])
                if not items:
                    return [types.TextContent(type="text", text=f"❌ No artists found for '{query}'")]
                result_text = f"🔍 **Found {len(items)} artist(s) for '{query}':**\n\n"
                for i, artist in enumerate(items, 1):
                    followers = artist.get('followers', {}).get('total', 0)
                    result_text += f"{i}. **{artist['name']}**\n"
                    result_text += f"   Followers: {followers:,}\n"
                    if artist.get('genres'):
                        result_text += f"   Genres: {', '.join(artist['genres'][:3])}\n"
                    result_text += "\n"
            else:
                result_text = f"❌ Search type '{search_type}' not supported."
            return [types.TextContent(type="text", text=result_text)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error searching: {str(e)}")]

    async def get_user_playlists(self) -> List[types.TextContent]:
        """Get user's playlists"""
        try:
            if not self.spotify_client:
                return [types.TextContent(type="text", text="❌ Not authenticated. Please run 'authenticate_spotify' first.")]
            playlists = self.spotify_client.current_user_playlists(limit=50)
            if not playlists or not playlists.get('items'):
                return [types.TextContent(type="text", text="📁 No playlists found")]
            result_text = f"📁 **Your Playlists ({len(playlists['items'])}):**\n\n"
            for playlist in playlists['items']:
                track_count = playlist.get('tracks', {}).get('total', 0)
                visibility = "Public" if playlist.get('public', False) else "Private"
                result_text += f"• **{playlist.get('name', 'Unknown')}** ({track_count} tracks, {visibility})\n"
                if playlist.get('description'):
                    result_text += f"  Description: {playlist['description']}\n"
                result_text += "\n"
            return [types.TextContent(type="text", text=result_text)]
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error getting playlists: {str(e)}")]

async def main():
    """Main entry point"""
    server = SpotifyMCPServer()
    
    # Run the server
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="spotify-mcp",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())