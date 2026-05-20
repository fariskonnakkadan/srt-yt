# yt_srt

Download SRT subtitles from a YouTube video.

## Install
```
python3 -m venv .venv && .venv/bin/pip install youtube-transcript-api
```

## Usage
```
.venv/bin/python yt_srt.py --url "https://www.youtube.com/watch?v=VIDEO_ID"
```
Saves `<Video_Title>.srt` (spaces → underscores). Override with `-o file.srt`, pick language with `-l en,es`.
