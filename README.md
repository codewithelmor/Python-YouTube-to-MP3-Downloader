# YouTube to MP3 Downloader

A simple, lightweight Python script to download audio from YouTube **videos or entire playlists** and automatically convert them into **MP3** files at your preferred quality using `yt-dlp` and `FFmpeg`.

## Features
* **Smart Audio Conversion**: Downloads only the core audio stream to save bandwidth, converting directly into high-fidelity MP3 files.
* **Playlist Support**: Paste a playlist URL (e.g. `https://www.youtube.com/playlist?list=...`) and the script automatically detects it, downloads every track, and organizes them into a subfolder named after the playlist. Unavailable/private tracks are skipped automatically, and one failed track won't stop the rest of the playlist.
* **Standardized Filenames**: Automatically saves your songs in a clean, uniform file pattern: **`<artist> - <title>.mp3`**.
* **Dynamic Bitrate Configuration**: Choose between 128, 192, 256, 320 kbps, or specific custom audio bitrate profiles.
* **Target Output Folders**: Choose any folder path (creates missing folders automatically) or default straight to your current working workspace folder.
* **Automated & Clean Tagging**: Extracts track title and channel info into metadata tags. If the artist's name is duplicated inside the title (e.g. *"Artist - Song Title"*), the script automatically scrubs the artist's name out of the title tag to prevent messy naming redundancy.

## Prerequisites

This project requires **FFmpeg** to handle audio conversion and write the ID3 metadata tags. It must be installed on your system and added to your system's PATH.

* **macOS**: `brew install ffmpeg`
* **Linux (Ubuntu/Debian)**: `sudo apt update && sudo apt install ffmpeg`
* **Windows**: Download the binaries from the official [FFmpeg site](https://ffmpeg.org) and add the `bin` folder to your System Environment Variables (PATH).

---

## Setup Instructions

Follow these steps to set up a virtual environment and run the script.

### 1. Clone or Create the Project
Navigate to your project directory:
```bash
cd path/to/your/project
```

### 2. Create a Virtual Environment
Create an isolated environment to prevent library conflicts.

* **macOS / Linux:**
  ```bash
  python3 -m venv venv
  ```
* **Windows:**
  ```cmd
  python -m venv venv
  ```

### 3. Activate the Virtual Environment
You must activate the environment before installing dependencies or running the script.

* **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
* **Windows (Command Prompt):**
  ```cmd
  venv\Scripts\activate.bat
  ```
* **Windows (PowerShell):**
  ```powershell
  venv\Scripts\Activate.ps1
  ```
  *(Note: If you get a script execution error in PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first).*

### 4. Install Dependencies
Install the required packages from the `requirements.txt` file:
```bash
pip install -r requirements.txt
```

---

## Usage

1. Run the Python script:
   ```bash
   python main.py
   ```
2. Paste your target **YouTube video or playlist URL** when prompted. Both single-video links and playlist links (e.g. `https://www.youtube.com/playlist?list=OLAK5uy_kD_cajzJAuFc9OmcuFljLwkx5d875IGK4`) are supported.
3. Provide a **Target Directory** (e.g., `downloads`, `~/Music/YouTube`, or leave it blank to save it right next to the script).
   * For a single video, the MP3 is saved directly into this folder.
   * For a playlist, a subfolder named after the playlist title is created inside this folder, and every track is saved there.
4. Choose your desired **audio quality/bitrate** (e.g., 128, 192, 256, 320 kbps).
5. The script downloads the stream(s), fixes duplicate metadata elements, writes clean ID3 tags, and outputs the final track(s) matching the custom `<artist> - <title>.mp3` formatting rule.
   * When a playlist URL is used, progress is printed per track (e.g. `[3/12] Processing: ...`), and any track that fails to download is skipped so the rest of the playlist still completes.

---

## Troubleshooting

* **"FFmpeg not found" Error:** Ensure FFmpeg is properly installed and that your terminal can run the `ffmpeg` command globally. Restart your terminal/IDE after installing FFmpeg.
* **Download Fails / HTTP Errors:** YouTube frequently changes its layout. If downloads stop working, update `yt-dlp` to the latest version inside your activated virtual environment:
  ```bash
  pip install --upgrade yt-dlp
  ```
* **Playlist Only Partially Downloads:** Some videos in a playlist may be private, deleted, or region-locked. These are skipped automatically and reported in the console; the rest of the playlist will still finish.

## Deactivation
When you are done working on the project, you can exit the virtual environment by typing:
```bash
deactivate
```
