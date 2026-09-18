import os
import re
import yt_dlp

def get_valid_directory():
    """Prompts the user for a download folder and ensures it exists."""
    while True:
        directory = input("\nEnter target directory to save MP3 (Leave blank for current folder): ").strip()
        
        if not directory:
            return "."  # Current directory
            
        # Clean up path and expand user home directory symbols like ~
        directory = os.path.abspath(os.path.expanduser(directory))
        
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"📁 Created folder: {directory}")
            return directory
        except Exception as e:
            print(f"❌ Invalid directory or permission denied. Error: {e}. Please try again.")

def get_valid_bitrate():
    """Prompts the user for a bitrate and validates the input."""
    print("\nSelect your desired MP3 quality (bitrate):")
    print("1. 128 kbps (Standard quality / smaller file)")
    print("2. 192 kbps (High quality - Recommended)")
    print("3. 256 kbps (Very high quality)")
    print("4. 320 kbps (Highest quality / larger file)")
    print("5. Custom bitrate")
    
    while True:
        choice = input("Enter choice (1-5) or directly enter a value (e.g., 256): ").strip()
        
        if choice == '1':
            return '128'
        elif choice == '2':
            return '192'
        elif choice == '3':
            return '256'
        elif choice == '4':
            return '320'
        elif choice == '5':
            custom = input("Enter custom bitrate in kbps (e.g., 160): ").strip()
            if custom.isdigit():
                return custom
        elif choice.isdigit():
            return choice
            
        print("❌ Invalid input. Please enter a number between 1-5 or a valid numeric bitrate.")

def sanitize_folder_name(name):
    """Strips characters that are unsafe for folder/file names across OSes."""
    name = re.sub(r'[\\/:*?"<>|]', '', name).strip()
    return name or "Untitled Playlist"

def clean_metadata_modifier(info_dict):
    """
    Extracted data hook: Parses out Artist and Title metadata.
    If the artist's name appears inside the track title, it trims it out.
    """
    # Fallback to channel name if explicit track artist metadata doesn't exist
    artist = info_dict.get('artist') or info_dict.get('uploader') or "Unknown Artist"
    title = info_dict.get('track') or info_dict.get('title') or "Unknown Title"
    
    artist = artist.strip()
    title = title.strip()
    
    if artist and title:
        # Check if the artist name exists inside the title (case-insensitive)
        if artist.lower() in title.lower():
            # Match variations like "Artist - Title", "Artist-Title", "Artist: Title"
            pattern = re.compile(rf'\b{re.escape(artist)}\b\s*[\-\:]*\s*', re.IGNORECASE)
            cleaned_title = pattern.sub('', title).strip()
            
            if cleaned_title:
                title = cleaned_title

    # Inject parsed fields back into the options dictionary so yt-dlp uses them for naming & tagging
    info_dict['artist'] = artist
    info_dict['title'] = title
    return info_dict

def build_ydl_opts(bitrate, output_dir):
    """Builds the shared yt-dlp options dict for a given bitrate/output folder."""
    output_template = os.path.join(output_dir, '%(artist)s - %(title)s.%(ext)s')

    return {
        'format': 'bestaudio/best',
        'outtmpl': output_template,
        'writethumbnail': False,
        'modify_chapters': False,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': bitrate,
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            }
        ],
        'quiet': False,
        'ignoreerrors': True,
    }

def download_single_video(ydl, info):
    """Cleans metadata for one video's info dict and hands it to yt-dlp for processing."""
    cleaned_info = clean_metadata_modifier(info)
    ydl.process_info(cleaned_info)

def download_playlist(ydl, info, bitrate, base_output_dir):
    """
    Iterates through every track in a playlist, downloading and tagging each one.
    Creates a subfolder named after the playlist so tracks stay organized together.
    """
    entries = [e for e in info.get('entries', []) if e]  # Skip unavailable/private entries
    total = len(entries)

    if total == 0:
        print("⚠️ No downloadable entries were found in this playlist.")
        return

    playlist_title = sanitize_folder_name(info.get('title') or "Untitled Playlist")
    playlist_dir = os.path.join(base_output_dir, playlist_title)
    os.makedirs(playlist_dir, exist_ok=True)

    print(f"\n📃 Playlist detected: \"{playlist_title}\" ({total} track(s))")
    print(f"📁 Saving tracks to: {playlist_dir}")

    # Point this download session's output template at the playlist subfolder
    ydl.params['outtmpl']['default'] = os.path.join(playlist_dir, '%(artist)s - %(title)s.%(ext)s')

    success_count = 0
    for index, entry in enumerate(entries, start=1):
        entry_title = entry.get('title') or entry.get('id') or "Unknown"
        print(f"\n[{index}/{total}] Processing: {entry_title}")
        try:
            download_single_video(ydl, entry)
            success_count += 1
        except Exception as e:
            print(f"❌ Skipped \"{entry_title}\" due to an error: {e}")
            continue

    print(f"\n🎉 Playlist download complete! {success_count}/{total} track(s) saved to: {playlist_dir}")

def download_youtube_as_mp3(youtube_url, bitrate, output_dir):
    ydl_opts = build_ydl_opts(bitrate, output_dir)

    try:
        print(f"\nFetching metadata at {bitrate}kbps... Please wait.")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)

            if info is None:
                print("❌ Could not retrieve any information for that URL.")
                return

            if 'entries' in info:
                # A playlist URL returns a top-level dict with an 'entries' list
                download_playlist(ydl, info, bitrate, output_dir)
            else:
                print("Extracting audio and formatting metadata... Please wait.")
                download_single_video(ydl, info)
                print(f"🎉 Download complete! Saved to: {output_dir}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    url = input("Enter YouTube Video or Playlist URL: ").strip()
    if url:
        output_folder = get_valid_directory()
        kbps = get_valid_bitrate()
        download_youtube_as_mp3(url, kbps, output_folder)
    else:
        print("❌ URL cannot be empty.")
