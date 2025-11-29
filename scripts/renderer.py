from pathlib import Path
import subprocess
from typing import List, Tuple

# Folder where we'll save the final clips
CLIPS = Path(__file__).resolve().parents[1] / "clips"

def render_vertical_clip(
        video_path,
        start: float,
        duration: float,
        out_path : Path | None = None
) -> Path:
    """
    Cut a vertical clip from the video using ffmpeg.

    video_path -> source video (string or Path)
    start -> start time in seconds
    duration -> length of the clip in seconds
    out_path -> optional output path, defaults to clips/clip_<start>.mp4
    """

    # Makse sure clips folder exists
    CLIPS.mkdir(parents=True, exist_ok=True)

    video_path = Path(video_path)

    # Default output file if none is provided
    if out_path is None:
        safe_start = int(start)
        out_path = CLIPS / f"clips_{safe_start}.mp4"
    else:
        out_path = Path(out_path)

    cmd = [
        "ffmpeg",
        "-y",                     # overwrite output if it exists   # overwrite
        "-ss", f"{start:.3f}",    # seek to start time              # start seek
        "-i", str(video_path),    # input video file                # input video path
        "-t", f"{duration:.3f}",   # clip duration                   # time duration
        "-vf", "crop = in_h*9/16:in_h,scale = 1080:1920",           # video filter chain
        "-c:v", "libx264",                                          # video codec (H.264(AVC) - supports all devices, browers, platforms. Quality vs file size good)
        "-preset", "fast",                                          # preset - encoder speed/quality tradeoff
        "-c:a", "aac",                                              # audio codec (aac - Advanced Audio Coding. Widely supported)
        str(out_path)                                               # output file path
    ]

    print("Running:", " ".join(cmd))

    result = subprocess.run(cmd)

    if result.returncode !=0:
        raise RuntimeError("ffmpeg failed to render clip")
    
    return out_path

def render_multiple_clips(
    video_path,
    segments: List[Tuple[float, float]],
    max_clips: int | None = None,
    clip_duration: float | None = None
) -> List[Path]:
    
    video_path = Path(video_path)
    outputs: List[Path] = []

    if max_clips is not None:
        segments = segments[:max_clips]

    for i, (start, end) in enumerate(segments, start = 1):
        if clip_duration is not None:
            duration = clip_duration
        else:
            duration = max(0.0, end - start)

        out_path = CLIPS / f"clip_{i}.mp4"
        print(f"Rendering clip {i}: start={start:.2f}, duration = {duration:.2f}")
        rendered = render_vertical_clip(video_path, start, duration, out_path=out_path)
        outputs.append(rendered)

    return outputs