# 👾 Pixel History Shorts (`pixel-history-shorts`)

> **16-Bit Retro Pixel Art Documentary Shorts Engine for Dramatic Historical Events & Mysteries.**

Pixel History Shorts generates atmospheric, high-retention short-form history videos using 16-bit pixel art scenes, Gemini Achird voiceover, and bold center stroke subtitles.

## 🌟 Featured Episode: The 1962 Alcatraz Escape
- **Format:** 1080x1920 (9:16 Vertical Full HD)
- **Visuals:** 16-bit retro pixel aesthetic with dynamic Ken Burns motion (zooms, pans, dramatic punches).
- **Audio:** Gemini TTS (`Achird` voice) with ambient ocean rain & sub-bass tension drone soundscape.
- **Subtitles:** Middle-centered (`Alignment=5`) bold contour stroke with keyword highlighting.

## 📁 Repository Structure
```
pixel-history-shorts/
├── build_pixel_short.py    # FFmpeg scene compositor & Ken Burns motion engine
├── generate_audio.py       # Gemini Achird TTS narration generator
├── script/
│   └── subtitles.json      # Timed phrase segments & highlight keywords
├── images/                 # 16-Bit retro pixel art storyboards (9:16 vertical)
└── audio/                  # Narration audio & ambient audio synthesis
```

## 🚀 Quick Start

### 1. Generate Voiceover
```bash
python3 generate_audio.py
```

### 2. Render Full Short Video
```bash
python3 build_pixel_short.py
```
Output will be compiled directly to `out/the_impossible_1962_alcatraz_escape.mp4`.
