"""
Create and populate database
"""

import os
import re
import sqlite3
from typing import Any, Dict, List, Tuple

import yt_dlp

STORAGE_DIR = os.environ["STORAGE_DIR"]
KEYWORDS_PATTERN = r"\[.+\]"
CHANNEL_URL = "https://www.youtube.com/@gabrielletenney"


def ori_title(vid: Dict[str, Any]) -> str:
    return vid["title"]


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


def create_tables(cur: sqlite3.Cursor) -> None:
    cur.execute(
        """
        create table dances (id int, name varchar, keywords varchar, url varchar)
        """
    )
    # row present iff username has status on id; else if absent, status is 0
    cur.execute(
        """
        create table progress (username varchar, id int, status int)
        """
    )

    # row says if username interested in id; else if absent, not interested
    cur.execute(
        """
        create table interest (username varchar, id int, interest int)
        """
    )


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


def in_db(url: str, cur: sqlite3.Cursor) -> bool:
    """
    Return True iff url is present in db
    """
    match = cur.execute("select url from dances where url = ?", (url,)).fetchone()
    result = match is not None
    return result


def update(vid_raw: Dict[str, Any], cur: sqlite3.Cursor) -> bool:
    """
    If not in db: add to db

    Returns
    -------
    True iff added the video
    """
    url = vid_raw["url"]
    added = not in_db(url, cur)
    if added:
        new_id = cur.execute("select max(id) from dances").fetchone()[0] + 1
        cur.execute(
            "insert into dances (id, name, keywords, url) values (?, ?, ?, ?)",
            (new_id, *extract_info(vid_raw)),
        )
    return added


def update_all(cur: sqlite3.Cursor, vids_raw: List[Dict[str, Any]]) -> int:
    n_updated = 0
    for x in vids_raw:
        n_updated += update(x, cur)
    return n_updated


if __name__ == "__main__":
    conn = sqlite3.connect(os.path.join(STORAGE_DIR, "dance-progress.db"))
    cur = conn.cursor()

    create_tables(cur)

    vids_raw = get_tutorial_videos(CHANNEL_URL)
    for i, vid_raw in enumerate(vids_raw):
        cur.execute(
            "insert into dances (id, name, keywords, url) values (?, ?, ?, ?)",
            (i, *extract_info(vid_raw)),
        )
    conn.commit()
    conn.close()
