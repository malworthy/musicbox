# pip install music-tag

import music_tag
import glob
import sqlite3
import json

con = sqlite3.connect("musiclibrary.db")
cur = con.cursor()
try:
    cur.execute("create table library(id INTEGER PRIMARY KEY, filename text, tracktitle text, artist text, album text, albumartist text, tracknumber text)")
except:
    pass

print("Starting")
data = []
f = open("config.json")
config = json.load(f)
f.close()

files = glob.glob(f"{config['library']}**/*.mp3", recursive=True)
print("Retreived files")

for file in files:
    try:
        print(file)
        tags = music_tag.load_file(file)
        data.append( (file, str(tags["tracktitle"]), str(tags["artist"]), str(tags["album"]), str(tags["albumartist"]),int(tags["tracknumber"])) )
    except:
        print("Error, could not add this file")

cur.execute("delete from library")
cur.executemany("insert into library(filename, tracktitle, artist, album, albumartist, tracknumber) values(?,?,?,?,?,?)", data)
con.commit()

for row in cur.execute("select * from library"):
    print(row)