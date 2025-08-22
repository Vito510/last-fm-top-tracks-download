import json
import os
import tqdm
from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic

# The 100 most listened to songs will be downloaded. Export Last.fm data with https://lastfm.ghan.nl/export/
LAST_FM_EXPORT = "./recenttracks-Vito_510-1755212327.json"
START_INDEX = 0
END_INDEX = 100

ytmusic = YTMusic()
data = json.loads(open(LAST_FM_EXPORT, "r", encoding="utf-8").read())

if not os.path.exists("./downloads"):
    os.mkdir("./downloads")


def download(url: str, output_template: str = "%(title)s.%(ext)s"):
    ydl_opts = {
        "extract_flat": "discard_in_playlist",
        "format": "bestaudio",
        "fragment_retries": 10,
        "ignoreerrors": "only_download",
        "outtmpl": {"default": output_template, "pl_thumbnail": ""},
        "postprocessor_args": {
            "ffmpeg": [
                "-c:v",
                "mjpeg",
                "-vf",
                "crop='if(gt(ih,iw),iw,ih)':'if(gt(iw,ih),ih,iw)'",
            ]
        },
        "postprocessors": [
            {"format": "jpg", "key": "FFmpegThumbnailsConvertor", "when": "before_dl"},
            {
                "key": "FFmpegExtractAudio",
                "nopostoverwrites": False,
                "preferredcodec": "best",
                "preferredquality": "5",
            },
            {
                "add_chapters": True,
                "add_infojson": "if_exists",
                "add_metadata": True,
                "key": "FFmpegMetadata",
            },
            {"already_have_thumbnail": False, "key": "EmbedThumbnail"},
            {"key": "FFmpegConcat", "only_multi_video": True, "when": "playlist"},
        ],
        "retries": 10,
        "warn_when_outdated": True,
        "writethumbnail": True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


tracks = {}
for page in data:
    for track in page["track"]:
        name = track["name"]
        artist = track["artist"]["#text"]

        key = name + artist

        if key not in tracks:
            tracks[key] = {"name": name, "artist": artist, "count": 0}

        tracks[key]["count"] += 1


sorted_keys = sorted(tracks, key=lambda x: tracks[x]["count"], reverse=True)
to_download = sorted_keys[START_INDEX:END_INDEX]

i = START_INDEX
for key in tqdm.tqdm(to_download):
    track = tracks[key]
    resp = ytmusic.search(
        f'{track["artist"]} - {track["name"]}', filter="songs", limit=5
    )
    try:
        url = "https://music.youtube.com/watch?v=" + resp[0]["videoId"]
        download(url, output_template=f"./downloads/{i}.%(ext)s")
    except:
        print("SKIP", i)
        pass

    i += 1
