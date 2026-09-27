import os
import tkinter
from tkinter.constants import HORIZONTAL

from mutagen.mp3 import MP3
import pygame
from tkinter import END, Button, Frame, Listbox, Tk, Scale, Label
from tkinter import filedialog

playlist = []
current_track_index = 0
is_paused = False
shuffle_mode = False
repeat_mode = False
stop_pressed = False
song_length = 0  # seconds

supported_extensions = (".mp3", ".wav", ".ogg")


def load_music(): # Handles loading the music to our playlist
    global current_track_index, playlist
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
        listbox.delete(0, END)
        for song in playlist:
            listbox.insert(END, os.path.basename(song))


def format_time(seconds): # Handles formatting time
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"


def play_music(): # Handles playing the song
    global is_paused, song_length, stop_pressed

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

    # Update current song label
    current_song_label.config(text=os.path.basename(song)) # Displays the current song on the label

    # Get song length (MP3 only)
    try:
        if song.lower().endswith(".mp3"):
            audio = MP3(song)
            song_length = audio.info.length
        else:
            song_length = 0
    except Exception:
        song_length = 0

    duration_label.config(text=format_time(song_length))

    listbox.selection_clear(0, END)
    listbox.selection_set(current_track_index)
    listbox.activate(current_track_index)


def pause_music(): # Handles pausing the song
    global is_paused
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.pause()
        is_paused = True


def stop_music(): # Handles stopping the song
    global is_paused, stop_pressed
    pygame.mixer.music.stop()
    is_paused = False
    stop_pressed = True

    progress_var.set(0)
    elapsed_label.config(text="00:00")
    remaining_label.config(text="-00:00")


def toggle_shuffle(): # Handles toggling shuffle mode
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    print("Shuffle:", shuffle_mode)


def toggle_repeat(): # Handles toggling repeat mode
    global repeat_mode
    repeat_mode = not repeat_mode
    print("Repeat:", repeat_mode)


def next_song(): # Handles going to the next song
    global current_track_index, is_paused

    if not playlist:
        return

    if repeat_mode:
        is_paused = False
        play_music()
        return

    if shuffle_mode:
        import random
        current_track_index = random.randint(0, len(playlist) - 1)
        is_paused = False
        play_music()
        return

    current_track_index = (current_track_index + 1) % len(playlist)
    is_paused = False
    play_music()


def previous_song(): # Handles going to the previous song
    global current_track_index, is_paused
    if not playlist:
        return
    current_track_index = (current_track_index - 1) % len(playlist)
    is_paused = False
    play_music()


def check_song_end(): # Handles checking if the song has ended
    if playlist:
        if not pygame.mixer.music.get_busy() and not is_paused and not stop_pressed:
            next_song()
    root.after(1000, check_song_end)


def seek_music(position_percent): # Handles seeking the song
    global song_length
    if song_length > 0:
        new_time = (position_percent / 100.0) * song_length
        pygame.mixer.music.play(start=new_time)


def update_progress(): # Handles updating the progress bar
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


pygame.mixer.init()
root = Tk()
root.title("Python Playlist App")

# Current song label
current_song_label = Label(root, text="No song playing", font=("Arial", 12))
current_song_label.pack(pady=5)

listbox = Listbox(root, width=50)
listbox.pack()

volume_slider = Scale(
    root,
    from_=0,
    to=1,
    resolution=0.01,
    orient=HORIZONTAL,
    command=lambda v: pygame.mixer.music.set_volume(float(v)),
)
volume_slider.pack()

progress_var = tkinter.DoubleVar()
progress_bar = Scale(
    root,
    from_=0,
    to=100,
    orient=HORIZONTAL,
    variable=progress_var,
    command=lambda v: seek_music(float(v)),
    length=400,
)
progress_bar.pack()

time_frame = Frame(root)
time_frame.pack()

elapsed_label = Label(time_frame, text="00:00")
elapsed_label.pack(side="left", padx=10)

duration_label = Label(time_frame, text="00:00")
duration_label.pack(side="left", padx=10)

remaining_label = Label(time_frame, text="-00:00")
remaining_label.pack(side="left", padx=10)

Button(root, text="Load Music", command=load_music).pack()

controls = Frame(root)
controls.pack(pady=8)

Button(controls, text="Play", command=play_music).pack(side="left", padx=5)
Button(controls, text="Pause", command=pause_music).pack(side="left", padx=5)
Button(controls, text="Stop", command=stop_music).pack(side="left", padx=5)
Button(controls, text="Next", command=next_song).pack(side="left", padx=5)
Button(controls, text="Previous", command=previous_song).pack(side="left", padx=5)
Button(controls, text="Shuffle", command=toggle_shuffle).pack(side="left", padx=5)
Button(controls, text="Repeat", command=toggle_repeat).pack(side="left", padx=5)


def close_app():
    pygame.mixer.quit()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", close_app)

check_song_end()
update_progress()

root.mainloop()
