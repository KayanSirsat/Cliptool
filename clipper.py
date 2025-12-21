from pathlib import Path
import argparse
import subprocess

from scripts.downloader import download_youtube
from scripts.analysis import load_audio, detect_rms_peaks
from scripts.segmenter import build_candidates
from scripts.renderer import render_multiple_clips

def get_video_duration(path: Path) -> float:
    """Use ffprobe to get video duration in seconds."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(path),
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed: {result.stderr[:200]}")
    return float(result.stdout.strip())

def main():
    parser = argparse.ArgumentParser(
        description="Auto-clipper: download video -> find loud moments -> render vertical clips."
    )
    parser.add_argument("source", help="Youtube URL or local video file path")
    parser.add_argument("--duration", type=float, default=25.0, help="Clip duration in seconds")
    parser.add_argument("--topk", type=int, default=6, help="How many loud peaks to consider")
    parser.add_argument("--max-clips", type=int, default=3, help="How many clips to actually render")
    parser.add_argument("--sr", type=int, default=22050, help="Audio sample rate for analysis")

    args = parser.parse_args()

    src = args.source

    # 1) Get video file (download if URL, else use local file)
    if src.lower().startswith("http"):
        print("[1/4] Downloading video...")
        video_path = download_youtube(src)
    else:
        video_path = Path(src)
        if not video_path.exists():
            raise FileNotFoundError(f"Local file not found: {video_path}")
        
    print("Video file:", video_path)

    # 2) Figure out total video duration
    print("[2/4] Getting video duration...")
    video_duration = get_video_duration(video_path)
    print(f"Video duration: {video_duration:.2f}s")

    # 3) Load audio and detect loud peaks
    print("[3/4] Analyzing audio for loud moments...")
    y, sr = load_audio(video_path, sr=args.sr)
    peaks = detect_rms_peaks(y, sr, topk=args.topk)
    print("Peaks (seconds):", [round(t,2) for t in peaks])

    # 4) Build candidat segments from peaks
    segments = build_candidates(
        peaks=peaks,
        clip_duration=args.duration,
        video_duration=video_duration
    )

    print("Candidate segments:", [(round(s, 2), round(e, 2)) for (s, e) in segments])

    if not segments:
        print("No segments found. Exiting.")
        return
    
    # 5) Render clips
    print("[4/4] Rendering clips...")
    outputs = render_multiple_clips(
        video_path=video_path,
        segments=segments,
        max_clips=args.max_clips,
        clip_duration=args.duration,
    )

    print("Done! Rendered clips:")
    for path in outputs:
        print(" -", path)


if __name__=="__main__":
    main()