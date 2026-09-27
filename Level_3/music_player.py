"""
Music player playback logic and controls.
"""

import os
import random
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from config import (
    playlist, current_track_index, is_paused, shuffle_mode, 
    repeat_mode, stop_pressed, song_length, current_album_art,
    SUPPORTED_EXTENSIONS
)
from album_art import get_album_art


def format_time(seconds):
    """Format seconds into MM:SS format."""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def load_music(playlist_box):
    """Load music files from selected directory and update playlist."""
    global current_track_index, playlist
    from tkinter import filedialog
    from tkinter.constants import END
    from album_art import clear_album_art_cache
    
    folder = filedialog.askdirectory()
    if folder:
        playlist = sorted(
            [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(SUPPORTED_EXTENSIONS)
            ],
            key=str.lower,
        )
        current_track_index = 0
        clear_album_art_cache()
        playlist_box.delete(0, END)
        for song in playlist:
            playlist_box.insert(END, os.path.basename(song))
        update_carousel()


def play_music(song_title_label, artist_label, main_art_label, mini_art_label, 
               duration_label, playlist_box):
    """Play current track with album art and metadata display."""
    global is_paused, song_length, stop_pressed, current_album_art

    if not playlist:
        return

    stop_pressed = False

    if is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
        return

    song = playlist[current_track_index]
    pygame.mixer.music.load(song)
    pygame.mixer.music.play()

    song_name = os.path.basename(song)
    song_title_label.config(text=song_name.replace('.mp3', '').replace('.wav', '').replace('.ogg', ''))
    artist_label.config(text="Unknown Artist")
    
    # Update album art displays
    current_album_art = get_album_art(song)
    main_art_label.config(image=current_album_art)
    mini_art_label.config(image=get_album_art(song, (60, 60)))

    try:
        if song.lower().endswith(".mp3"):
            audio = MP3(song)
            song_length = audio.info.length
            # Try to extract artist from metadata
            try:
                id3 = ID3(song)
                if 'TPE1' in id3:
                    artist_label.config(text=str(id3['TPE1']))
            except:
                pass
        else:
            song_length = 0
    except Exception:
        song_length = 0

    duration_label.config(text=format_time(song_length))

    from tkinter.constants import END
    playlist_box.selection_clear(0, END)
    playlist_box.selection_set(current_track_index)
    playlist_box.activate(current_track_index)
    update_carousel()


def pause_music():
    """Pause the currently playing music."""
    global is_paused
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        is_paused = True


def stop_music(progress_var, elapsed_label, remaining_label):
    """Stop the music and reset progress."""
    global is_paused, stop_pressed
    pygame.mixer.music.stop()
    is_paused = False
    stop_pressed = True

    progress_var.set(0)
    elapsed_label.config(text="00:00")
    remaining_label.config(text="-00:00")


def toggle_shuffle(shuffle_btn):
    """Toggle shuffle mode and update button style."""
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    from ttkbootstrap.constants import SECONDARY, WARNING
    shuffle_btn.config(bootstyle=WARNING if shuffle_mode else SECONDARY)


def toggle_repeat(repeat_btn):
    """Toggle repeat mode and update button style."""
    global repeat_mode
    repeat_mode = not repeat_mode
    from ttkbootstrap.constants import SECONDARY, WARNING
    repeat_btn.config(bootstyle=WARNING if repeat_mode else SECONDARY)


def next_song(song_title_label, artist_label, main_art_label, mini_art_label,
              duration_label, playlist_box):
    """Play next track, handling shuffle and repeat modes."""
    global current_track_index, is_paused

    if not playlist:
        return

    if repeat_mode:
        is_paused = False
        play_music(song_title_label, artist_label, main_art_label, mini_art_label,
                   duration_label, playlist_box)
        return

    if shuffle_mode:
        current_track_index = random.randint(0, len(playlist) - 1)
        is_paused = False
        play_music(song_title_label, artist_label, main_art_label, mini_art_label,
                   duration_label, playlist_box)
        return

    current_track_index = (current_track_index + 1) % len(playlist)
    is_paused = False
    play_music(song_title_label, artist_label, main_art_label, mini_art_label,
               duration_label, playlist_box)


def previous_song(song_title_label, artist_label, main_art_label, mini_art_label,
                  duration_label, playlist_box):
    """Play previous track in playlist."""
    global current_track_index, is_paused
    if not playlist:
        return
    current_track_index = (current_track_index - 1) % len(playlist)
    is_paused = False
    play_music(song_title_label, artist_label, main_art_label, mini_art_label,
               duration_label, playlist_box)


def check_song_end(root, song_title_label, artist_label, main_art_label, mini_art_label,
                   duration_label, playlist_box):
    """Check if song ended and auto-play next track."""
    if playlist:
        if not pygame.mixer.music.get_busy() and not is_paused and not stop_pressed:
            next_song(song_title_label, artist_label, main_art_label, mini_art_label,
                      duration_label, playlist_box)
    root.after(1000, check_song_end, root, song_title_label, artist_label, main_art_label,
               mini_art_label, duration_label, playlist_box)


def seek_music(percent):
    """Seek to a specific position in the current track."""
    global song_length
    if song_length > 0:
        new_time = (percent / 100.0) * song_length
        pygame.mixer.music.play(start=new_time)


def update_progress(progress_var, elapsed_label, remaining_label, root):
    """Update progress bar and time labels."""
    global song_length
    if pygame.mixer.music.get_busy():
        current_time = pygame.mixer.music.get_pos() / 1000.0

        elapsed_label.config(text=format_time(current_time))

        if song_length > 0:
            percent = (current_time / song_length) * 100.0
            progress_var.set(percent)

            remaining = song_length - current_time
            if remaining < 0:
                remaining = 0
            remaining_label.config(text=f"-{format_time(remaining)}")

    root.after(500, update_progress, progress_var, elapsed_label, remaining_label, root)


def update_carousel(left_art_label, right_art_label):
    """Update album art carousel with current, previous, and next tracks."""
    if not playlist:
        return
    
    # Get indices for carousel (current, next, previous)
    prev_idx = (current_track_index - 1) % len(playlist)
    next_idx = (current_track_index + 1) % len(playlist)
    
    # Update side arts
    if len(playlist) > 1:
        prev_art = get_album_art(playlist[prev_idx], (150, 150))
        left_art_label.config(image=prev_art)
        next_art = get_album_art(playlist[next_idx], (150, 150))
        right_art_label.config(image=next_art)
    else:
        left_art_label.config(image='')
        right_art_label.config(image='')
