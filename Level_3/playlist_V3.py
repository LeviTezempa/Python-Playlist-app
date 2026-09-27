import os
import tkinter as tk
from tkinter.constants import HORIZONTAL
from tkinter import END, filedialog
from PIL import Image, ImageTk
import io

import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import random

# -----------------------------
# GLOBAL VARIABLES
# -----------------------------
playlist = []
current_track_index = 0
is_paused = False
shuffle_mode = False
repeat_mode = False
stop_pressed = False
song_length = 0
album_arts = {}  # Cache for album art images
current_album_art = None  # Currently displayed album art

supported_extensions = (".mp3", ".wav", ".ogg")

# -----------------------------
# ALBUM ART EXTRACTION
# -----------------------------
def extract_album_art(file_path):
    """Extract album art from MP3 file metadata."""
    try:
        if file_path.lower().endswith(".mp3"):
            audio = ID3(file_path)
            for tag in audio.values():
                if tag.FrameID == 'APIC':
                    image_data = tag.data
                    image = Image.open(io.BytesIO(image_data))
                    image = image.resize((300, 300), Image.Resampling.LANCZOS)
                    return ImageTk.PhotoImage(image)
    except Exception:
        pass
    return None

def get_album_art(file_path, size=(300, 300)):
    """Get album art from cache or extract it. Returns placeholder if none found."""
    if file_path in album_arts:
        return album_arts[file_path]
    
    art = extract_album_art(file_path)
    if art:
        album_arts[file_path] = art
    else:
        # Create default gradient placeholder
        img = Image.new('RGB', size, (40, 40, 50))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse([size[0]//4, size[1]//4, size[0]*3//4, size[1]*3//4], fill=(60, 60, 80))
        art = ImageTk.PhotoImage(img)
        album_arts[file_path] = art
    return art

# -----------------------------
# LOAD MUSIC
# -----------------------------
def load_music():
    """Load music files from selected directory and update playlist."""
    global current_track_index, playlist, album_arts
    folder = filedialog.askdirectory()
    if folder:
        playlist = sorted(
            [
                os.path.join(folder, f)
                for f in os.listdir(folder)
                if f.lower().endswith(supported_extensions)
            ],
            key=str.lower,
        )
        current_track_index = 0
        album_arts = {}  # Clear album art cache
        playlist_box.delete(0, END)
        for song in playlist:
            playlist_box.insert(END, os.path.basename(song))
        update_carousel()

# -----------------------------
# TIME FORMAT
# -----------------------------
def format_time(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"

# -----------------------------
# PLAY MUSIC
# -----------------------------
def play_music():
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
    song_title.config(text=song_name.replace('.mp3', '').replace('.wav', '').replace('.ogg', ''))
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

    playlist_box.selection_clear(0, END)
    playlist_box.selection_set(current_track_index)
    playlist_box.activate(current_track_index)
    update_carousel()

# -----------------------------
# PAUSE MUSIC
# -----------------------------
def pause_music():
    global is_paused
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        is_paused = True

# -----------------------------
# STOP MUSIC
# -----------------------------
def stop_music():
    global is_paused, stop_pressed
    pygame.mixer.music.stop()
    is_paused = False
    stop_pressed = True

    progress_var.set(0)
    elapsed_label.config(text="00:00")
    remaining_label.config(text="-00:00")

# -----------------------------
# SHUFFLE / REPEAT
# -----------------------------
def toggle_shuffle():
    """Toggle shuffle mode and update button style."""
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    shuffle_btn.config(bootstyle=WARNING if shuffle_mode else SECONDARY)

def toggle_repeat():
    """Toggle repeat mode and update button style."""
    global repeat_mode
    repeat_mode = not repeat_mode
    repeat_btn.config(bootstyle=WARNING if repeat_mode else SECONDARY)

# -----------------------------
# NEXT / PREVIOUS
# -----------------------------
def next_song():
    """Play next track, handling shuffle and repeat modes."""
    global current_track_index, is_paused

    if not playlist:
        return

    if repeat_mode:
        is_paused = False
        play_music()
        return

    if shuffle_mode:
        current_track_index = random.randint(0, len(playlist) - 1)
        is_paused = False
        play_music()
        return

    current_track_index = (current_track_index + 1) % len(playlist)
    is_paused = False
    play_music()

def previous_song():
    """Play previous track in playlist."""
    global current_track_index, is_paused
    if not playlist:
        return
    current_track_index = (current_track_index - 1) % len(playlist)
    is_paused = False
    play_music()

# -----------------------------
# AUTO PLAY NEXT
# -----------------------------
def check_song_end():
    """Check if song ended and auto-play next track."""
    if playlist:
        if not pygame.mixer.music.get_busy() and not is_paused and not stop_pressed:
            next_song()
    root.after(1000, check_song_end)

# -----------------------------
# CAROUSEL UPDATE
# -----------------------------
def update_carousel():
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

# -----------------------------
# SEEK
# -----------------------------
def seek_music(percent):
    global song_length
    if song_length > 0:
        new_time = (percent / 100.0) * song_length
        pygame.mixer.music.play(start=new_time)

# -----------------------------
# PROGRESS UPDATE
# -----------------------------
def update_progress():
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

    root.after(500, update_progress)

# -----------------------------
# LYRICS PANEL
# -----------------------------
def toggle_lyrics():
    """Toggle lyrics panel visibility."""
    if lyrics_frame.winfo_ismapped():
        lyrics_frame.pack_forget()
    else:
        lyrics_frame.pack(fill="both", expand=True, padx=20, pady=10)
        lyrics_text.config(text="Lyrics feature\n\nNo lyrics available for this track.\n\nLyrics can be loaded from .lrc files or online databases.")

# -----------------------------
# PLAYLIST PANEL
# -----------------------------
def toggle_playlist_panel():
    """Toggle playlist panel visibility."""
    if playlist_panel.winfo_ismapped():
        playlist_panel.pack_forget()
    else:
        playlist_panel.pack(fill="both", expand=True, padx=20, pady=10)

# -----------------------------
# UI SETUP (ttkbootstrap)
# -----------------------------
pygame.mixer.init()
root = tb.Window(themename="superhero")
root.title("Python Music Player")
root.geometry("1200x800")
root.minsize(1000, 700)  # Minimum size to keep all features usable
root.configure(bg="#1a1a2e")

# MAIN CONTAINER
main_container = tb.Frame(root)
main_container.pack(fill="both", expand=True, padx=20, pady=20)

# ALBUM ART CAROUSEL SECTION
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

song_title = tb.Label(center_frame, text="No Track Selected", font=("Segoe UI", 18, "bold"), foreground="white")
song_title.pack(pady=5)

artist_label = tb.Label(center_frame, text="Load music to start", font=("Segoe UI", 12), foreground="#888")
artist_label.pack(pady=5)

# Right album art (next track)
right_art_label = tb.Label(carousel_frame, text="", font=("Arial", 12))
right_art_label.pack(side="right", padx=20)

# PROGRESS BAR SECTION
progress_frame = tb.Frame(main_container)
progress_frame.pack(fill="x", pady=10)

progress_var = tk.DoubleVar()
progress_bar = tb.Scale(
    progress_frame,
    from_=0,
    to=100,
    orient=HORIZONTAL,
    variable=progress_var,
    command=lambda v: seek_music(float(v)),
    bootstyle=INFO,
    length=800,
)
progress_bar.pack(fill="x", padx=20)

# Time labels
time_frame = tb.Frame(progress_frame)
time_frame.pack(fill="x", padx=20)

elapsed_label = tb.Label(time_frame, text="00:00", font=("Segoe UI", 10), foreground="#888")
elapsed_label.pack(side="left")

duration_label = tb.Label(time_frame, text="00:00", font=("Segoe UI", 10), foreground="#888")
duration_label.pack(side="left", expand=True)

remaining_label = tb.Label(time_frame, text="-00:00", font=("Segoe UI", 10), foreground="#888")
remaining_label.pack(side="right")

# CONTROL BAR (Modern design with rounded feel)
control_bar = tb.Frame(main_container, bootstyle="dark")
control_bar.pack(fill="x", pady=20, ipady=15)

# Left side: Mini album art + track info
control_left = tb.Frame(control_bar)
control_left.pack(side="left", padx=20)

mini_art_label = tb.Label(control_left, text="🎵", font=("Arial", 24))
mini_art_label.pack(side="left", padx=10)

track_info = tb.Frame(control_left)
track_info.pack(side="left")
tb.Label(track_info, text="Now Playing", font=("Segoe UI", 8, "bold"), foreground="#666").pack()
tb.Label(track_info, text="No track", font=("Segoe UI", 10), foreground="white").pack()

# Center: Playback controls
controls_center = tb.Frame(control_bar)
controls_center.pack(side="left", expand=True)

shuffle_btn = tb.Button(controls_center, text="🔀", bootstyle=SECONDARY, command=toggle_shuffle, width=3)
shuffle_btn.pack(side="left", padx=5)

tb.Button(controls_center, text="⏮", bootstyle=SECONDARY, command=previous_song, width=4).pack(side="left", padx=5)
tb.Button(controls_center, text="▶", bootstyle=SUCCESS, command=play_music, width=5).pack(side="left", padx=5)
tb.Button(controls_center, text="⏸", bootstyle=INFO, command=pause_music, width=4).pack(side="left", padx=5)
tb.Button(controls_center, text="⏭", bootstyle=SECONDARY, command=next_song, width=4).pack(side="left", padx=5)

repeat_btn = tb.Button(controls_center, text="🔁", bootstyle=SECONDARY, command=toggle_repeat, width=3)
repeat_btn.pack(side="left", padx=5)

# Right side: Additional features + volume
control_right = tb.Frame(control_bar)
control_right.pack(side="right", padx=20)

tb.Button(control_right, text="📂 Load", bootstyle=PRIMARY, command=load_music, width=6).pack(side="left", padx=5)
tb.Button(control_right, text="📝 Lyrics", bootstyle=SECONDARY, command=toggle_lyrics, width=8).pack(side="left", padx=5)
tb.Button(control_right, text="📋 Playlist", bootstyle=SECONDARY, command=toggle_playlist_panel, width=10).pack(side="left", padx=5)

volume_frame = tb.Frame(control_right)
volume_frame.pack(side="left", padx=10)
tb.Label(volume_frame, text="🔊", foreground="white").pack(side="left")
volume_slider = tb.Scale(
    volume_frame,
    from_=0,
    to=1,
    orient=HORIZONTAL,
    command=lambda v: pygame.mixer.music.set_volume(float(v)),
    bootstyle=PRIMARY,
    length=100,
)
volume_slider.pack(side="left", padx=5)

# HIDDEN PANELS
# Lyrics panel
lyrics_frame = tb.Frame(main_container, bootstyle="dark")
lyrics_text = tb.Label(lyrics_frame, text="", font=("Segoe UI", 11), justify="center", foreground="#ccc")
lyrics_text.pack(pady=20)

# Playlist panel
playlist_panel = tb.Frame(main_container, bootstyle="dark")
playlist_label = tb.Label(playlist_panel, text="Playlist", font=("Segoe UI", 14, "bold"), foreground="white")
playlist_label.pack(pady=10)

playlist_box = tk.Listbox(playlist_panel, width=50, height=10, bg="#2a2a4e", fg="white", selectbackground="#4a4a8e")
playlist_box.pack(pady=10)

load_btn = tb.Button(playlist_panel, text="📂 Load Music", bootstyle=PRIMARY, command=load_music)
load_btn.pack(pady=10)

# -----------------------------
# START LOOPS
# -----------------------------
check_song_end()
update_progress()

root.mainloop()
