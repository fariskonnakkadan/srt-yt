#!/usr/bin/env python3
"""Download SRT subtitles for a YouTube video."""
import argparse
import json
import re
import sys
from urllib.parse import urlparse, parse_qs, urlencode
from urllib.request import urlopen

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import SRTFormatter


def extract_video_id(url: str) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    if host in {"youtu.be"}:
        return parsed.path.lstrip("/")
    if "youtube.com" in host:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [""])[0]
        m = re.match(r"^/(embed|shorts|v|live)/([^/?#]+)", parsed.path)
        if m:
            return m.group(2)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url):
        return url
    raise ValueError(f"Cannot extract video id from: {url}")


def fetch_title(video_id: str) -> str:
    q = urlencode({"url": f"https://www.youtube.com/watch?v={video_id}", "format": "json"})
    with urlopen(f"https://www.youtube.com/oembed?{q}", timeout=10) as r:
        return json.load(r)["title"]


def sanitize_filename(title: str) -> str:
    # strip illegal path chars, collapse whitespace to underscore
    cleaned = re.sub(r'[\\/:*?"<>|]+', "", title)
    cleaned = re.sub(r"\s+", "_", cleaned).strip("._")
    return cleaned or "video"


def fetch_srt(video_id: str, languages: list[str]) -> str:
    api = YouTubeTranscriptApi()
    transcripts = api.list(video_id)
    try:
        transcript = transcripts.find_manually_created_transcript(languages)
    except Exception:
        try:
            transcript = transcripts.find_generated_transcript(languages)
        except Exception:
            transcript = next(iter(transcripts))
    fetched = transcript.fetch()
    return SRTFormatter().format_transcript(fetched)


def main() -> int:
    ap = argparse.ArgumentParser(description="Download SRT subtitles from YouTube.")
    ap.add_argument("--url", required=True, help="YouTube video URL or 11-char ID")
    ap.add_argument("-o", "--output", help="Output .srt path (default: <video_title>.srt)")
    ap.add_argument("-l", "--lang", default="en",
                    help="Comma-separated language codes (default: en)")
    args = ap.parse_args()

    try:
        vid = extract_video_id(args.url)
        srt = fetch_srt(vid, [c.strip() for c in args.lang.split(",") if c.strip()])
        title = fetch_title(vid)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    out = args.output or f"{sanitize_filename(title)}.srt"
    with open(out, "w", encoding="utf-8") as f:
        f.write(srt)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
