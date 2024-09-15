import sqlite3
import yt_dlp
import os
import re

STORAGE_DIR = os.environ["STORAGE_DIR"]
KEYWORDS_PATTERN = r"\[.+\]"

conn = sqlite3.connect(os.path.join(STORAGE_DIR, "dance-progress.db"))
cur = conn.cursor()

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


# URL of the YouTube channel
channel_url = "https://www.youtube.com/@gabrielletenney"

# Options for yt-dlp
ydl_opts = {
    "extract_flat": True,  # Extract video metadata without downloading
    "dump_single_json": True,  # Dump data in JSON format
    "skip_download": True,  # Do not download videos
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info_dict = ydl.extract_info(channel_url, download=False)
    videos = info_dict["entries"]

for i, vid in enumerate(videos[0]["entries"]):
    original_title = vid["title"]
    if not original_title.startswith("Learn"):  # remove vlogs etc
        continue
    title = original_title.removeprefix("Learn ").split(" in")[0].strip('"')
    keyword_matches = re.search(KEYWORDS_PATTERN, original_title)
    if keyword_matches is not None:
        keywords = keyword_matches.group(0).strip("[]")
    else:
        keywords = ""
    url = vid["url"]
    cur.execute(
        "insert into dances (id, name, keywords, url) values (?, ?, ?, ?)",
        (i, title, keywords, url),
    )
conn.commit()
conn.close()
