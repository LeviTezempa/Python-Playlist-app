
import os
import pygame
from tkinter import END, Button, Frame, Listbox, Tk
from tkinter import filedialog


playlist = []  # List to hold the paths of the audio files
current_track_index = 0  # Index of the currently playing track
is_paused = False
supported_extensions = (".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac")

def load_music():
    """Load music files into the playlist"""
    global current_track_index, playlist
    folder = filedialog.askdirectory()
    if folder:
        playlist = sorted(
            [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(supported_extensions) #handles
            ],
            key=str.lower,
        )
        current_track_index = 0
        listbox.delete(0, END)
        for song in playlist:
            listbox.insert(END, os.path.basename(song))


def play_music():
    global is_paused
    if not playlist:
        return
    if is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
        return
    song = playlist[current_track_index]
    pygame.mixer.music.load(song)
    pygame.mixer.music.play()
    listbox.selection_clear(0, END)
    listbox.selection_set(current_track_index)
    listbox.activate(current_track_index)

def pause_music():
    global is_paused
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        is_paused = True

def next_song():
    global current_track_index, is_paused
    if not playlist:
        return
    current_track_index = (current_track_index + 1) % len(playlist)
    is_paused = False
    play_music()

def previous_song():
    global current_track_index, is_paused
    if not playlist:
        return
    current_track_index = (current_track_index - 1) % len(playlist)
    is_paused = False
    play_music()

pygame.mixer.init()
root = Tk()
root.title("Python Playlist App")

listbox = Listbox(root, width=50)
listbox.pack()

Button(root, text="Load Music", command=load_music).pack()
controls = Frame(root)
controls.pack(pady=8)
Button(controls, text="Play", command=play_music).pack(side="left", padx=5)
Button(controls, text="Pause", command=pause_music).pack(side="left", padx=5)
Button(controls, text="Next", command=next_song).pack(side="left", padx=5)
Button(controls, text="Previous", command=previous_song).pack(side="left", padx=5)

def close_app():
    pygame.mixer.quit()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", close_app)
root.mainloop()