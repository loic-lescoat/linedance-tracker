"""
Gets all video URLs and adds them to database if they don't exist
"""

import os
import psycopg
from scrape import update_all, get_tutorial_videos, CHANNEL_URL

conn = psycopg.connect(
    host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"]
)
cur = conn.cursor()

vids_raw = get_tutorial_videos(CHANNEL_URL)
n_updated = update_all(cur, vids_raw)
conn.commit()
conn.close()
print(f"Updated {n_updated} videos")
