"""
Ad-hoc script to copy all data from
one database into another
"""

# import sqlite3
import os

STORAGE_DIR = os.environ["STORAGE_DIR"]

SOURCE_DB = os.path.join(STORAGE_DIR, "dance-progress.db.old")
DESTINATION_DB = os.path.join(STORAGE_DIR, "dance-progress.db")

# rest of script is a 'next step'
