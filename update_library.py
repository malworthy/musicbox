# pip install music-tag

import music_tag
import glob
import sqlite3
import json
import sys

def get_files():
    print("Retreiving files")
    f = open("config.json")
    config = json.load(f)
    f.close()

    return glob.glob(f"{config['library']}**/*.mp3", recursive=True)

def extract_tags(full_refresh):
    data = []
    print("Extracting tags")

    for file in get_files():
        try:
            print(file)      
            if full_refresh or is_file_in_library(file) == False:  
                tags = music_tag.load_file(file)
                data.append( (file, str(tags["tracktitle"]), str(tags["artist"]), str(tags["album"]), str(tags["albumartist"]),int(tags["tracknumber"]),int(tags["#length"])) )
        except:
            print("Error, could not add this file")
    add_to_database(data, full_refresh)

def is_file_in_library(filename):
    cur.execute("select count(*) from library where filename = ?",(filename,))
    result = cur.fetchone()
    return result[0] > 0

def add_to_database(data, full_refresh):
    print("Inserting records into database")
    if full_refresh:
        cur.execute("delete from library")
    cur.executemany("insert into library(filename, tracktitle, artist, album, albumartist, tracknumber, length) values(?,?,?,?,?,?,?)", data)
    cur.execute("update library set albumartist = artist where albumartist = ''")
    con.commit()

## main entry point ##

con = sqlite3.connect("musiclibrary.db")
cur = con.cursor()
try:
    cur.execute("create table library(id INTEGER PRIMARY KEY, filename text, tracktitle text, artist text, album text, albumartist text, tracknumber int, length int)")
    cur.execute("create table queue(id INTEGER PRIMARY KEY, libraryid int, sortorder int, playing text, canplay int)")
except:
    pass

full_refresh = True
if len(sys.argv) > 1:
    full_refresh = sys.argv[1] == "-a" or sys.argv[1] == "--add"

extract_tags(full_refresh)
print("finished")