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

def download_youtube_as_mp3(youtube_url, bitrate, output_dir):
    # Uses the cleaned metadata tags directly to generate the "<artist> - <title>.<ext>" filename format
    output_template = os.path.join(output_dir, '%(artist)s - %(title)s.%(ext)s')

    ydl_opts = {
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
    }

    try:
        print(f"\nExtracting audio and formatting metadata at {bitrate}kbps... Please wait.")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Fetch metadata details first
            info = ydl.extract_info(youtube_url, download=False)
            # Filter and clean track metadata before the download pipeline runs
            cleaned_info = clean_metadata_modifier(info)
            # Submit modified data back into the downloader engine
            ydl.process_info(cleaned_info)
            
        print(f"🎉 Download complete! Saved to: {output_dir}")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    url = input("Enter YouTube Video URL: ").strip()
    if url:
        output_folder = get_valid_directory()
        kbps = get_valid_bitrate()
        download_youtube_as_mp3(url, kbps, output_folder)
    else:
        print("❌ URL cannot be empty.")
