import os
import sys
import json
import wave
import subprocess
from datetime import timedelta
from pathlib import Path

BASE_DIR = Path("/Users/vinaybt/Downloads/history-pixel-shorts")
IMAGES_DIR = BASE_DIR / "images"
AUDIO_DIR = BASE_DIR / "audio"
TEMP_DIR = BASE_DIR / "temp"
OUT_DIR = BASE_DIR / "out"
SCRIPT_DIR = BASE_DIR / "script"

TEMP_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)

def format_ass_time(seconds):
    td = timedelta(seconds=seconds)
    hours = int(td.total_seconds() // 3600)
    minutes = int((td.total_seconds() % 3600) // 60)
    secs = int(td.total_seconds() % 60)
    centis = int(round((td.total_seconds() - int(td.total_seconds())) * 100))
    if centis >= 100:
        centis = 99
    return f"{hours}:{minutes:02d}:{secs:02d}.{centis:02d}"

def generate_ass_subtitles(subtitles_json_path, output_ass_path):
    with open(subtitles_json_path, "r", encoding="utf-8") as f:
        items = json.load(f)

    # Alignment 5 = Middle Center (exact center of 1080x1920 screen)
    # Outline 10 = Bold stroke contour
    ass_template = """[Script Info]
Title: Alcatraz Pixel Shorts Subtitles
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: None
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: CenterBold,Arial Black,74,&H00FFFFFF,&H000000FF,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,10,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    events = []
    for item in items:
        start_str = format_ass_time(item["start"])
        end_str = format_ass_time(item["end"])
        raw_text = item["text"].upper()
        highlight_word = item.get("highlight", "").upper()

        if highlight_word and highlight_word in raw_text:
            # Highlight with electric golden yellow
            colored_word = f"{{\\c&H0000E5FF&}}{highlight_word}{{\\c&H00FFFFFF&}}"
            styled_text = raw_text.replace(highlight_word, colored_word, 1)
        else:
            styled_text = raw_text

        events.append(f"Dialogue: 0,{start_str},{end_str},CenterBold,,0,0,0,,{styled_text}")

    full_ass = ass_template + "\n".join(events) + "\n"
    with open(output_ass_path, "w", encoding="utf-8") as f:
        f.write(full_ass)
    print(f"Subtitles written to: {output_ass_path}")

def render_scene_clip(image_path, duration, output_path, motion_type="zoom_in"):
    fps = 30
    total_frames = int(duration * fps)
    
    # Scale & Ken Burns pan/zoom
    if motion_type == "zoom_in":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:1920,setsar=1,"
            f"zoompan=z='min(zoom+0.0016,1.16)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )
    elif motion_type == "zoom_out":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:1920,setsar=1,"
            f"zoompan=z='if(lte(zoom,1.0),1.16,max(1.001,zoom-0.0016))':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )
    elif motion_type == "pan_up":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:1920,setsar=1,"
            f"zoompan=z='1.12':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{total_frames})':s=1080x1920:fps={fps}"
        )
    elif motion_type == "pan_down":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:1920,setsar=1,"
            f"zoompan=z='1.12':d={total_frames}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{total_frames})':s=1080x1920:fps={fps}"
        )
    elif motion_type == "dramatic_punch":
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:1920,setsar=1,"
            f"zoompan=z='min(zoom+0.0030,1.22)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )
    else:
        vf = (
            f"scale=1080:1920:force_original_aspect_ratio=increase:flags=bicubic,crop=1080:1920,setsar=1,"
            f"zoompan=z='min(zoom+0.0015,1.15)':d={total_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={fps}"
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-vf", vf,
        "-t", f"{duration:.3f}",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-pix_fmt", "yuv420p",
        str(output_path)
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg failed for {image_path}: {res.stderr[:300]}")

def build_video():
    total_duration = 40.80
    scenes = [
        {"img": "scene_01.jpg", "start": 0.00,  "end": 8.70,  "motion": "zoom_in"},
        {"img": "scene_02.jpg", "start": 8.70,  "end": 16.10, "motion": "dramatic_punch"},
        {"img": "scene_03.jpg", "start": 16.10, "end": 23.00, "motion": "pan_down"},
        {"img": "scene_04.jpg", "start": 23.00, "end": 27.20, "motion": "pan_up"},
        {"img": "scene_05.jpg", "start": 27.20, "end": 31.10, "motion": "zoom_in"},
        {"img": "scene_06.jpg", "start": 31.10, "end": 36.70, "motion": "dramatic_punch"},
        {"img": "scene_07.jpg", "start": 36.70, "end": total_duration, "motion": "zoom_out"}
    ]

    print("\n--- Step 1: Rendering Motion Clips ---")
    clip_paths = []
    for i, sc in enumerate(scenes, 1):
        img_file = IMAGES_DIR / sc["img"]
        duration = sc["end"] - sc["start"]
        clip_out = TEMP_DIR / f"clip_{i:02d}.mp4"
        print(f"  Rendering Scene {i:02d} ({duration:.2f}s, motion: {sc['motion']})...")
        render_scene_clip(img_file, duration, clip_out, motion_type=sc["motion"])
        clip_paths.append(clip_out)

    concat_list_file = TEMP_DIR / "concat_list.txt"
    with open(concat_list_file, "w") as f:
        for p in clip_paths:
            f.write(f"file '{p.absolute()}'\n")

    raw_video = TEMP_DIR / "raw_concatenated.mp4"
    print("\n--- Step 2: Concatenating Scene Clips ---")
    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", str(concat_list_file),
        "-c", "copy",
        str(raw_video)
    ]
    subprocess.run(concat_cmd, check=True, stdout=subprocess.DEVNULL)

    print("\n--- Step 3: Generating Center Bold ASS Subtitles ---")
    ass_file = TEMP_DIR / "subtitles_center_bold.ass"
    generate_ass_subtitles(SCRIPT_DIR / "subtitles.json", ass_file)

    print("\n--- Step 4: Final Compositing (Video + Audio + Center Subtitles) ---")
    audio_path = AUDIO_DIR / "mixed_voiceover.wav"
    final_output = OUT_DIR / "the_impossible_1962_alcatraz_escape.mp4"

    merge_cmd = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(audio_path),
        "-vf", f"ass={ass_file}",
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(final_output)
    ]
    subprocess.run(merge_cmd, check=True)

    print(f"\n🎉 Video Successfully Generated!")
    print(f"Output File: {final_output}")
    print(f"Duration: {total_duration:.2f}s | Resolution: 1080x1920 (9:16 Vertical)")
    return final_output

if __name__ == "__main__":
    build_video()
