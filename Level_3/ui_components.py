"""
UI components for the music player including carousel, control bar, and panels.
"""

import tkinter as tk
from tkinter.constants import HORIZONTAL
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from config import BG_COLOR, PLAYLIST_BG, PLAYLIST_SELECT, TEXT_COLOR
from music_player import (
    load_music, play_music, pause_music, stop_music, toggle_shuffle, 
    toggle_repeat, next_song, previous_song, seek_music, update_carousel
)


def create_carousel(main_container):
    """Create the album art carousel section."""
    carousel_frame = tb.Frame(main_container)
    carousel_frame.pack(fill="both", expand=True, pady=20)

    # Left album art (previous track)
    left_art_label = tb.Label(carousel_frame, text="", font=("Arial", 12))
    left_art_label.pack(side="left", padx=20)

    # Center album art (current track) - larger
    center_frame = tb.Frame(carousel_frame)
    center_frame.pack(side="left", expand=True)

    main_art_label = tb.Label(center_frame, text="🎵", font=("Arial", 80))
    main_art_label.pack(pady=10)

    song_title = tb.Label(center_frame, text="No Track Selected", 
                          font=("Segoe UI", 18, "bold"), foreground="white")
    song_title.pack(pady=5)

    artist_label = tb.Label(center_frame, text="Load music to start", 
                           font=("Segoe UI", 12), foreground="#888")
    artist_label.pack(pady=5)

    # Right album art (next track)
    right_art_label = tb.Label(carousel_frame, text="", font=("Arial", 12))
    right_art_label.pack(side="right", padx=20)

    return left_art_label, main_art_label, right_art_label, song_title, artist_label


def create_progress_section(main_container, seek_callback):
    """Create the progress bar and time labels section."""
    progress_frame = tb.Frame(main_container)
    progress_frame.pack(fill="x", pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = tb.Scale(
        progress_frame,
        from_=0,
        to=100,
        orient=HORIZONTAL,
        variable=progress_var,
        command=seek_callback,
        bootstyle=INFO,
        length=800,
    )
    progress_bar.pack(fill="x", padx=20)

    # Time labels
    time_frame = tb.Frame(progress_frame)
    time_frame.pack(fill="x", padx=20)

    elapsed_label = tb.Label(time_frame, text="00:00", 
                            font=("Segoe UI", 10), foreground=TEXT_COLOR)
    elapsed_label.pack(side="left")

    duration_label = tb.Label(time_frame, text="00:00", 
                             font=("Segoe UI", 10), foreground=TEXT_COLOR)
    duration_label.pack(side="left", expand=True)

    remaining_label = tb.Label(time_frame, text="-00:00", 
                              font=("Segoe UI", 10), foreground=TEXT_COLOR)
    remaining_label.pack(side="right")

    return progress_var, elapsed_label, duration_label, remaining_label


def create_control_bar(main_container, callbacks):
    """Create the modern control bar with playback controls and features."""
    control_bar = tb.Frame(main_container, bootstyle="dark")
    control_bar.pack(fill="x", pady=20, ipady=15)

    # Left side: Mini album art + track info
    control_left = tb.Frame(control_bar)
    control_left.pack(side="left", padx=20)

    mini_art_label = tb.Label(control_left, text="🎵", font=("Arial", 24))
    mini_art_label.pack(side="left", padx=10)

    track_info = tb.Frame(control_left)
    track_info.pack(side="left")
    tb.Label(track_info, text="Now Playing", 
            font=("Segoe UI", 8, "bold"), foreground="#666").pack()
    track_name_label = tb.Label(track_info, text="No track", 
                               font=("Segoe UI", 10), foreground="white")
    track_name_label.pack()

    # Center: Playback controls
    controls_center = tb.Frame(control_bar)
    controls_center.pack(side="left", expand=True)

    shuffle_btn = tb.Button(controls_center, text="🔀", bootstyle=SECONDARY, 
                          command=callbacks['toggle_shuffle'], width=3)
    shuffle_btn.pack(side="left", padx=5)

    tb.Button(controls_center, text="⏮", bootstyle=SECONDARY, 
             command=callbacks['previous'], width=4).pack(side="left", padx=5)
    tb.Button(controls_center, text="▶", bootstyle=SUCCESS, 
             command=callbacks['play'], width=5).pack(side="left", padx=5)
    tb.Button(controls_center, text="⏸", bootstyle=INFO, 
             command=callbacks['pause'], width=4).pack(side="left", padx=5)
    tb.Button(controls_center, text="⏭", bootstyle=SECONDARY, 
             command=callbacks['next'], width=4).pack(side="left", padx=5)

    repeat_btn = tb.Button(controls_center, text="🔁", bootstyle=SECONDARY, 
                          command=callbacks['toggle_repeat'], width=3)
    repeat_btn.pack(side="left", padx=5)

    # Right side: Additional features + volume
    control_right = tb.Frame(control_bar)
    control_right.pack(side="right", padx=20)

    tb.Button(control_right, text="📂 Load", bootstyle=PRIMARY, 
             command=callbacks['load'], width=6).pack(side="left", padx=5)
    tb.Button(control_right, text="📝 Lyrics", bootstyle=SECONDARY, 
             command=callbacks['toggle_lyrics'], width=8).pack(side="left", padx=5)
    tb.Button(control_right, text="📋 Playlist", bootstyle=SECONDARY, 
             command=callbacks['toggle_playlist'], width=10).pack(side="left", padx=5)

    volume_frame = tb.Frame(control_right)
    volume_frame.pack(side="left", padx=10)
    tb.Label(volume_frame, text="🔊", foreground="white").pack(side="left")
    volume_slider = tb.Scale(
        volume_frame,
        from_=0,
        to=1,
        orient=HORIZONTAL,
        command=callbacks['set_volume'],
        bootstyle=PRIMARY,
        length=100,
    )
    volume_slider.pack(side="left", padx=5)

    return mini_art_label, track_name_label, shuffle_btn, repeat_btn


def create_lyrics_panel(main_container):
    """Create the lyrics panel (hidden by default)."""
    lyrics_frame = tb.Frame(main_container, bootstyle="dark")
    lyrics_text = tb.Label(lyrics_frame, text="", font=("Segoe UI", 11), 
                          justify="center", foreground="#ccc")
    lyrics_text.pack(pady=20)
    return lyrics_frame, lyrics_text


def create_playlist_panel(main_container):
    """Create the playlist panel (hidden by default)."""
    playlist_panel = tb.Frame(main_container, bootstyle="dark")
    playlist_label = tb.Label(playlist_panel, text="Playlist", 
                             font=("Segoe UI", 14, "bold"), foreground="white")
    playlist_label.pack(pady=10)

    playlist_box = tk.Listbox(playlist_panel, width=50, height=10, 
                             bg=PLAYLIST_BG, fg="white", 
                             selectbackground=PLAYLIST_SELECT)
    playlist_box.pack(pady=10)

    load_btn = tb.Button(playlist_panel, text="📂 Load Music", 
                       bootstyle=PRIMARY, command=lambda: None)  # Will be set later
    load_btn.pack(pady=10)

    return playlist_panel, playlist_box, load_btn
