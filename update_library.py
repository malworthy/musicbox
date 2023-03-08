# pip install music-tag

import music_tag
import glob
import sqlite3
import json
import sys
import os


def get_files(ext):
    print("Retreiving files")

    return glob.glob(f"{config['library']}**/*.{ext}", recursive=True)


def extract_tags(ext):
    data = []
    default_ext = config["extensions"][0]
    print("Extracting tags")

    for file in get_files(ext):
        try:
            if is_file_in_library(file) == False:
                print(file)
                tags = music_tag.load_file(file)
                album = str(tags["album"])
                if ext != default_ext:
                    album += f" ({ext})"
                data.append((file, str(tags["tracktitle"]), str(tags["artist"]),
                             album, str(tags["albumartist"]), int(tags["tracknumber"]), int(tags["#length"]), str(tags["year"])))
        except:
            song = os.path.basename(file)
            artist = "Unknown Artist"
            album = "Unknown Album"
            track_number = 0
            length = 0
            data.append((file, song, artist, album,
                        artist, track_number, length, 0))
            print("Error, could not extract tags from this file")
    add_to_database(data)


def is_file_in_library(filename):
    cur.execute("select count(*) from library where filename = ?", (filename,))
    result = cur.fetchone()
    return result[0] > 0


def remove_orphans():
    print("Removing orphans")
    cur.execute("select id, filename from library")
    rows = cur.fetchall()
    for row in rows:
        id = row[0]
        filename = row[1]
        if not os.path.isfile(filename):
            print(
                f"Removing file '{filename}' from library as it no longer exists")
            cur.execute("delete from library where id = ?", (id,))
            con.commit()


def update_cover_art():
    print("updating/adding cover art")
    cur.execute("select id, filename from library where coverart is null")
    rows = cur.fetchall()
    for row in rows:
        id = row[0]
        path = os.path.dirname(row[1])
        coverart = ""
        for ext in ["jpg", "png"]:
            files = glob.glob(f"{path}**/*.{ext}", recursive=False)
            if len(files) > 0:
                coverart = files[0]
                break
        if coverart != "":
            print(f"coverart '{coverart}' found")
            con.execute(
                "update library set coverart = ? where id = ?", (coverart, id))
            con.commit()


def add_to_database(data):
    print("Inserting records into database")

    cur.executemany(
        "insert into library(filename, tracktitle, artist, album, albumartist, tracknumber, length, year) values(?,?,?,?,?,?,?,?)", data)
    cur.execute("update library set albumartist = artist where albumartist = ''")
    con.commit()


def schema_upgrade(sql):
    try:
        cur.execute(sql)
    except:
        pass

## main entry point ##


con = sqlite3.connect("musiclibrary.db")
cur = con.cursor()
schema_upgrade("create table library(id INTEGER PRIMARY KEY, filename text, tracktitle text, artist text, album text, albumartist text, tracknumber int, length int)")
schema_upgrade(
    "create table queue(id INTEGER PRIMARY KEY, libraryid int, sortorder int, playing text, canplay int)")
schema_upgrade("alter table library add year text")
schema_upgrade(
    "create table history(id INTEGER PRIMARY KEY, libraryid int, dateplayed text)")
schema_upgrade("alter table library add coverart text")

f = open("config.json")
config = json.load(f)
f.close()

# for ext in config["extensions"]:
#    print(f" ----- Importing {ext} files ----- ")
#    extract_tags(ext)

# remove_orphans()
update_cover_art()

print("finished")
