import sqlite3
import yt_dlp
import sys

conn = sqlite3.connect("dance-progress.db")
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
    create table dance_progress (name varchar, url varchar, status int)
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

for vid in videos[0]["entries"]:
    title = vid["title"]
    if not title.startswith("Learn"):
        continue
    url = vid["url"]
    cur.execute("insert into dance_progress values (?, ?, 0)", (title, url))
conn.commit()
conn.close()
