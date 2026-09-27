"""
Main entry point for the modern music player application.
"""

import pygame
import ttkbootstrap as tb
from config import BG_COLOR
from music_player import (
    play_music, pause_music, stop_music, toggle_shuffle, toggle_repeat,
    next_song, previous_song, seek_music, check_song_end, update_progress,
    load_music, update_carousel
)
from ui_components import (
    create_carousel, create_progress_section, create_control_bar,
    create_lyrics_panel, create_playlist_panel
)


def toggle_lyrics(lyrics_frame, lyrics_text):
    """Toggle lyrics panel visibility."""
    if lyrics_frame.winfo_ismapped():
        lyrics_frame.pack_forget()
    else:
        lyrics_frame.pack(fill="both", expand=True, padx=20, pady=10)
        lyrics_text.config(text="Lyrics feature\n\nNo lyrics available for this track.\n\nLyrics can be loaded from .lrc files or online databases.")


def toggle_playlist(playlist_panel):
    """Toggle playlist panel visibility."""
    if playlist_panel.winfo_ismapped():
        playlist_panel.pack_forget()
    else:
        playlist_panel.pack(fill="both", expand=True, padx=20, pady=10)


def set_volume(value):
    """Set the music volume."""
    pygame.mixer.music.set_volume(float(value))


def main():
    """Main application entry point."""
    # Initialize pygame mixer
    pygame.mixer.init()

    # Create main window
    root = tb.Window(themename="superhero")
    root.title("Python Music Player")
    root.geometry("1200x800")
    root.minsize(1000, 700)
    root.configure(bg=BG_COLOR)

    # Main container
    main_container = tb.Frame(root)
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    # Create UI components
    left_art_label, main_art_label, right_art_label, song_title, artist_label = create_carousel(main_container)
    progress_var, elapsed_label, duration_label, remaining_label = create_progress_section(
        main_container, lambda v: seek_music(float(v))
    )
    mini_art_label, track_name_label, shuffle_btn, repeat_btn = create_control_bar(
        main_container,
        callbacks={
            'toggle_shuffle': lambda: toggle_shuffle(shuffle_btn),
            'toggle_repeat': lambda: toggle_repeat(repeat_btn),
            'play': lambda: play_music(song_title, artist_label, main_art_label, 
                                       mini_art_label, duration_label, playlist_box),
            'pause': pause_music,
            'next': lambda: next_song(song_title, artist_label, main_art_label, 
                                      mini_art_label, duration_label, playlist_box),
            'previous': lambda: previous_song(song_title, artist_label, main_art_label, 
                                              mini_art_label, duration_label, playlist_box),
            'load': lambda: load_music(playlist_box),
            'toggle_lyrics': lambda: toggle_lyrics(lyrics_frame, lyrics_text),
            'toggle_playlist': lambda: toggle_playlist(playlist_panel),
            'set_volume': set_volume
        }
    )
    lyrics_frame, lyrics_text = create_lyrics_panel(main_container)
    playlist_panel, playlist_box, load_btn = create_playlist_panel(main_container)

    # Update the load button in playlist panel to use the same callback
    load_btn.config(command=lambda: load_music(playlist_box))

    # Update carousel with initial state
    update_carousel(left_art_label, right_art_label)

    # Start background loops
    check_song_end(root, song_title, artist_label, main_art_label, mini_art_label,
                   duration_label, playlist_box)
    update_progress(progress_var, elapsed_label, remaining_label, root)

    # Run main loop
    root.mainloop()


if __name__ == "__main__":
    main()
