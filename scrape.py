import sqlite3
import yt_dlp
import sys
import os

STORAGE_DIR = os.environ["STORAGE_DIR"]

conn = sqlite3.connect(os.path.join(STORAGE_DIR, "dance-progress.db"))
cur = conn.cursor()

if len(sys.argv) > 1 and sys.argv[1] == "--delete":
    cur.execute(
        """
        drop table dance_progress
        """
    )
    conn.commit()
    del cur


cur = conn.cursor()
cur.execute(
    """
    create table dance_progress (id int, name varchar, url varchar, status int)
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


cur = conn.cursor()

for i, vid in enumerate(videos[0]["entries"]):
    title = vid["title"]
    if not title.startswith("Learn"):
        continue
    title = title.lstrip("Learn ").split(" in")[0]
    url = vid["url"]
    cur.execute("insert into dance_progress values (?, ?, ?, 0)", (i, title, url))
conn.commit()
conn.close()
