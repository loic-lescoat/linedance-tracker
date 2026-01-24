"""
Create and populate database
"""

import os
import time

import re
from typing import Any, Dict, List, Tuple, Optional
import requests
from openai import OpenAI
from pydantic import BaseModel

import psycopg
import yt_dlp

STORAGE_DIR = os.environ["STORAGE_DIR"]
KEYWORDS_PATTERN = r"\[.+\]"
CHANNEL_URL = "https://www.youtube.com/@gabrielletenney"


def ori_title(vid: Dict[str, Any]) -> str:
    return vid["title"]


def get_title_desc(video_id: str) -> tuple[str, str]:
    """
    returns title and description
    """
    x = requests.get(
        f"https://www.googleapis.com/youtube/v3/videos?part=snippet&id={video_id}&key={os.environ['GOOGLE_YOUTUBE_API_KEY']}"
    )
    snippet = x.json()["items"][0]["snippet"]
    title = snippet["title"]
    description = snippet["description"]
    time.sleep(0.5)  # avoid querying too often
    return title, description


class DanceMetadata(BaseModel):
    dance_name: Optional[str]
    song_name: Optional[str]
    song_artist: Optional[str]
    counts: Optional[str]


def extract_dance_metadata(title: str, description: str) -> DanceMetadata:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = """
    You the following fields from the YouTube description provided by the user.
    
    Fields:
    - dance_name
    - song_name
    - song_artist
    - counts
    
    If a field is missing, return null.
    """  # NOTE: None instead of null?
    response = client.responses.parse(
        model="gpt-5-nano",  # model (positional)
        input=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": description},
        ],
        text_format=DanceMetadata,
    )
    metadata = response.output_parsed
    return metadata


def get_tutorial_videos(channel_url: str) -> List[Dict[str, Any]]:
    """
    Returns tutorial videos, i.e. filters out vlogs and more
    """

    # Options for yt-dlp
    YDL_OPTS = {
        "extract_flat": True,  # Extract video metadata without downloading
        "dump_single_json": True,  # Dump data in JSON format
        "skip_download": True,  # Do not download videos
    }

    with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
        info_dict = ydl.extract_info(CHANNEL_URL, download=False)
        videos = info_dict["entries"]

    vids = list(
        filter(
            lambda vid: ori_title(vid).startswith("Learn"),
            videos[0]["entries"],
        )
    )
    return vids


def extract_info(vid: Dict[str, Any]) -> Tuple[str, str, str]:
    """
    Extracts useful info
    """
    original_title = ori_title(vid)
    title = original_title.removeprefix("Learn ").split(" in")[0].strip('"')
    keyword_matches = re.search(KEYWORDS_PATTERN, original_title)
    if keyword_matches is not None:
        keywords = keyword_matches.group(0).strip("[]")
    else:
        keywords = ""
    url = vid["url"]
    return (title, keywords, url)


def in_db(url: str, cur: psycopg.Cursor) -> bool:
    """
    Return True iff url is present in dances table
    """
    match = cur.execute("select url from dances where url = %s", (url,)).fetchone()
    result = match is not None
    return result


def update(vid_raw: Dict[str, Any], cur: psycopg.Cursor) -> bool:
    """
    If not in db: add to db
    Assumes workflow:
        1. add to dances table
        2. add to dance_descriptions table

    Returns
    -------
    True iff added the video
    """
    url = vid_raw["url"]
    added = not in_db(url, cur)
    if added:
        name, keywords, _ = extract_info(vid_raw)
        cur.execute(
            "insert into dances (name, keywords, url) values (%s, %s, %s)",
            [name, keywords, url],
        )
        # id is generated always as identity -> we can read it this way
        new_id = cur.execute("select id from dances where url = %s", [url]).fetchone()[
            0
        ]
        title, description = get_title_desc(url.split("v=")[1])
        dance_metadata = extract_dance_metadata(title, description)

        # use fallback in case dance_name or song_name are missing from description
        data = [
            new_id,
            dance_metadata.dance_name or name,
            dance_metadata.song_name or keywords,
            dance_metadata.song_artist,
            dance_metadata.counts,
        ]
        cur.execute(
            """insert into dance_descriptions
            (id, dance_name, song_name, song_artist, counts)
            values (%s, %s, %s, %s, %s)""",
            data,
        )
    return added


def update_all(cur: psycopg.Cursor, vids_raw: List[Dict[str, Any]]) -> int:
    n_updated = 0
    for x in vids_raw:
        n_updated += update(x, cur)
    return n_updated


if __name__ == "__main__":
    conn = psycopg.connect(
        host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"]
    )

    cur = conn.cursor()

    vids_raw = get_tutorial_videos(CHANNEL_URL)
    for i, vid_raw in enumerate(vids_raw):
        cur.execute(
            "insert into dances (name, keywords, url) values (%s, %s, %s)",
            extract_info(vid_raw),
        )
    conn.commit()
    conn.close()
