from pathlib import Path
import subprocess

DOWNLOADS = Path(__file__).resolve().parents[1] / "downloads"

def download_youtube(url: str):

    """
    Downloads a YT video using yt-dlp and saves it to the downloads/ folder.
    Function: Returns the path of the downloaded .mp4 file
    """

    # Make sure the folder exists
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    # Output pattern: downloads/<videoid>.mp4
    output_template  = str(DOWNLOADS / "%(id)s.%(ext)s")

    # Command to run yt-dlp
    cmd = [
        "yt-dlp",
        "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
        "-o", output_template,
        url
    ]

    print("Running:", " ".join(cmd))

    # Execute the command
    result = subprocess.run(cmd)

    if result.returncode !=0:
        raise RuntimeError("Failed to download video. Check the URL or network connection.")
    
    # Find the most recent mp4 file from downloads/
    mp4_files = sorted(
        DOWNLOADS.glob("*.mp4"),
        key=lambda f: f.stat().st_mtime,
        reverse=True
    )

    if not mp4_files:
        raise FileNotFoundError("yt-dlp completed, but no MP4 file was found")
    
    return mp4_files[0]