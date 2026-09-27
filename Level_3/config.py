"""
Configuration and global state for the music player.
"""

# Supported audio file extensions
SUPPORTED_EXTENSIONS = (".mp3", ".wav", ".ogg")

# Global state variables
playlist = []
current_track_index = 0
is_paused = False
shuffle_mode = False
repeat_mode = False
stop_pressed = False
song_length = 0
album_arts = {}  # Cache for album art images
current_album_art = None  # Currently displayed album art

# UI colors
BG_COLOR = "#1a1a2e"
PLAYLIST_BG = "#2a2a4e"
PLAYLIST_SELECT = "#4a4a8e"
TEXT_COLOR = "#888"
