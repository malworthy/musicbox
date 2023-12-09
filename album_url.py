import sqlite3
import urllib.parse
import json

# This script will generate an auto play url for all albums in collection.
con = sqlite3.connect("musiclibrary.db")
cur = con.cursor()

f = open("config.json")
config = json.load(f)
f.close()

cur.execute("select distinct album from library")
rows = cur.fetchall()
for row in rows:
    album = urllib.parse.quote(row[0])
    print(f"http://{config['host']}:{config['port']}/autoplay/{album}")
