from typing import List, Tuple

def build_candidates(
        peaks: List[float],
        clip_duration: float,
        video_duration: float,
        merge_margin: float = 1.0
) -> List[Tuple[float, float]]:
    
    """
    Convert loudness peaks into candidate (start, end) clip ranges.
    
    peaks           -> list of timestamps (in seconds) where audio is loud.
    clip_duration   -> desired length of each clip (seconds).
    video_duration  -> total length of the video (seconds).
    merge_margin    -> if two segments are closer than this (seconds), merge them.
    """

    half = clip_duration / 2.0

    raw_segments: List[Tuple[float, float]] = []
    # 1) Create a window around each peak
    for t in peaks:
        
        # try centering the clip around the peak
        
        start = t - half
        end = t + half
        
        #clamp to [0, video_duration]
        if start < 0:
            start = 0.0
            end = min(clip_duration, video_duration)
        if end > video_duration:
            end = video_duration
            start = max(0.0, end-clip_duration)
            
        raw_segments.append((start, end))

    # 2) Sort by start time
    raw_segments.sort(key=lambda seg: seg[0])

    # 3) Merge overlapping / very close segments
    merged: List[Tuple[float, float]] = []
    for start, end in raw_segments:
        if not merged:
            merged.append((start,end))
        else:
            prev_start, prev_end = merged[-1]
            # If this starts before or just after the previous one ends, merge
            if start <= prev_end + merge_margin:
                new_end = max(prev_end, end)
                merged[-1] = (prev_start, new_end)
            else:
                merged.append((start, end))

    return merged