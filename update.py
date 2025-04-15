"""
Gets all video URLs and adds them to database if they don't exist
"""

import sqlite3
from scrape import update_all, get_tutorial_videos, CHANNEL_URL

conn = sqlite3.Connection("storage/dance-progress.db")
cur = conn.cursor()

vids_raw = get_tutorial_videos(CHANNEL_URL)
update_all(cur, vids_raw)

conn.commit()
conn.close()
