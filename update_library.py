# pip install music-tag

import music_tag
import glob
import sqlite3
import json

con = sqlite3.connect("musiclibrary.db")
cur = con.cursor()
try:
    cur.execute("create table library(id INTEGER PRIMARY KEY, filename text, tracktitle text, artist text, album text, albumartist text, tracknumber int, length int)")
except:
    pass

print("Retreiving files")
data = []
f = open("config.json")
config = json.load(f)
f.close()

files = glob.glob(f"{config['library']}**/*.mp3", recursive=True)
print("Extracting tags")

for file in files:
    try:
        print(file)        
        tags = music_tag.load_file(file)
        data.append( (file, str(tags["tracktitle"]), str(tags["artist"]), str(tags["album"]), str(tags["albumartist"]),int(tags["tracknumber"]),int(tags["#length"])) )
    except:
        print("Error, could not add this file")

print("Inserting records into database")
cur.execute("delete from library")
cur.executemany("insert into library(filename, tracktitle, artist, album, albumartist, tracknumber, length) values(?,?,?,?,?,?,?)", data)
cur.execute("update library set albumartist = artist where albumartist = ''")
con.commit()

print("finished")