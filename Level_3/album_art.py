"""
Album art extraction and caching functionality.
"""

import io
from PIL import Image, ImageTk
from mutagen.id3 import ID3
from config import album_arts


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
    # Check cache first
    cache_key = f"{file_path}_{size[0]}x{size[1]}"
    if cache_key in album_arts:
        return album_arts[cache_key]
    
    art = extract_album_art(file_path)
    if art:
        album_arts[cache_key] = art
    else:
        # Create default gradient placeholder
        img = Image.new('RGB', size, (40, 40, 50))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        draw.ellipse([size[0]//4, size[1]//4, size[0]*3//4, size[1]*3//4], fill=(60, 60, 80))
        art = ImageTk.PhotoImage(img)
        album_arts[cache_key] = art
    return art


def clear_album_art_cache():
    """Clear the album art cache."""
    global album_arts
    album_arts.clear()
