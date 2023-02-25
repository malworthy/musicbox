from bottle import route, post, run, request, app, static_file, delete
from bottle_cors_plugin import cors_plugin
import sqlite3
import json
import threading
import time
from pygame import mixer
import pygame


def query(sql, params):
    res = cur.execute(sql, params)
    rows = res.fetchall()
    return [dict(row) for row in rows]


@route('/ui')
def ui():
    return static_file("ui.html", "./ui/")


@route('/ui/<file>')
def ui2(file):
    return static_file(file, "./ui/")


@route('/search')
def search():
    x = f"%{request.query.search}%"
    print(x)
    sql = """
        select album, case when count(*) > 1 then 'Various' else max(albumartist) end artist 
        from (select distinct albumartist, album from library where album like ? or artist like ? or albumartist like ?) sq 
        group by album
        order by artist;
    """
    result = query(sql, (x, x, x))
    return json.dumps(result)


@route('/album')
def album():
    search = request.query.search
    sql = "select * from library where album = ? order by artist, album, cast(tracknumber as INT), filename"
    result = query(sql, (search,))

    return json.dumps(result)


@post('/add/<id>')
def add(id):
    sql = "insert into queue(libraryid, canplay) values(?, 1)"
    result = cur.execute(sql, (id, ))
    con.commit()
    result = query("select count(*) as queueCount from queue", ())
    return json.dumps(result[0])


@delete('/<id>')
def remove(id):
    sql = "delete from queue where id = ?"
    cur.execute(sql, (id, ))
    con.commit()
    result = query("select count(*) as queueCount from queue", ())
    return json.dumps(result[0])


@delete('/all')
def remove():
    sql = "delete from queue"
    cur.execute(sql)
    con.commit()
    return """{ "queueCount" : 0 }"""


@route("/queue")
def queue():
    result = query(
        "select q.id as queueId, l.* from queue q inner join library l on q.libraryid = l.id", ())
    return json.dumps(result)


@route("/status")
def status():
    sql = """
        select l.*, 1 as playing, (select count(*) from queue) as queueCount 
        from queue q inner join library l on q.libraryid = l.id 
        where playing is not null
    """
    result = query(sql, ())
    if len(result) == 1:
        return json.dumps(result[0])

    result = query(
        "select count(*) as queueCount , 0 as playing from queue", ())
    return json.dumps(result[0])


@post('/play')
def play():
    if mixer.music.get_busy():
        return """{"status" : "already playing"}"""

    con.execute("update queue set canplay = 1")
    con.commit()

    next_song = get_next_song(con)

    con.execute(
        "update queue set playing = datetime('now') where id = ?", (next_song['id'],))
    con.commit()
    thread = threading.Thread(target=playasync, args=(next_song,))
    thread.start()
    return """{"status" : "play started"}"""


@post('/stop')
def stop():
    cur.execute("update queue set canplay = 0")
    cur.execute("delete from queue where playing is not null")
    con.commit()
    mixer.music.stop()
    return """{"status" : "stopped"}"""


@post('/queuealbum')
def queuealbum():
    params = request.json
    cur.execute(
        "insert into queue(libraryid, canplay) select id, 1 from library where album = ? order by cast(tracknumber as INT), filename", (params["album"],))
    con.commit()

    return """{"status" : "queued"}"""


@post('/play/<id>')
def playsong(id):
    if mixer.music.get_busy():
        return """{"status" : "already playing"}"""
    cur.execute("delete from queue")
    add(id)
    return play()


@post('/playalbum')
def playalbum():
    if mixer.music.get_busy():
        return """{"status" : "already playing"}"""

    params = request.json
    cur.execute("delete from queue")
    cur.execute(
        "insert into queue(libraryid) select id from library where album = ? order by cast(tracknumber as INT), filename", (params["album"],))
    con.commit()

    return play()


@post('/rand/<num>')
def random_queue(num):
    cur.execute("delete from queue")
    cur.execute(
        f"insert into queue(libraryid)  select id from library order by random() limit {num}", ())
    con.commit()
    return """{"status" : "success"}"""


@post('/mix/<name>')
def create_mixtape(name):
    sql = """
        insert into library(filename, tracktitle, artist, album, albumartist, tracknumber, length, year)
        select l.filename, l.tracktitle,l.artist, ? as album, 'mixtape' as albumartist, q.id, l.length, l.year 
        from queue q inner join library l on q.libraryid = l.id;
    """
    cur.execute(
        "delete from library where albumartist = 'mixtape' and album = ?", (name,))
    cur.execute(sql, (name,))
    con.commit()
    return """{"status" : "success"}"""


@delete('/mix/<name>')
def delete_mixtape(name):
    cur.execute(
        "delete from library where albumartist = 'mixtape' and album = ?", (name,))
    con.commit()
    return """{"status" : "success"}"""


def is_playing():
    return False  # for now just rely on is busy - but won't work in the 1 seconds between songs


def get_next_song(db_conn):
    get_song_sql = """select q.id, l.filename, l.id as libraryid 
            from queue q inner join library l on q.libraryid = l.id 
            where canplay = 1 and playing is null order by q.id limit 1"""
    curs = db_conn.execute(get_song_sql)
    return curs.fetchone()


def playasync(row):
    con2 = sqlite3.connect("musiclibrary.db")
    con2.row_factory = sqlite3.Row
    cur2 = con2.cursor()

    # row = get_next_song(con2)
    if row == None:
        return

    filename = row['filename']
    id = row['id']
    mixer.music.load(row['filename'])
    print(f"Playing song {filename}")
    mixer.music.play()
    mixer.music.set_endevent(1)

    songs_in_queue = True
    while songs_in_queue:

        row = get_next_song(con2)
        if row != None:
            mixer.music.queue(row['filename'])
        else:
            print("no more songs in queue")
            songs_in_queue = False

        wait = True
        while wait:
            print(" -- in wait loop --")
            time.sleep(1)
            for event in pygame.event.get():
                if event.type == 1:
                    wait = False

        print(f"finished playing song {filename} and deleting from queue")
        cur2.execute("delete from queue where id = ?", (id,))
        con2.commit()

        if songs_in_queue == False:
            row = get_next_song(con2)
            if row != None:
                print(
                    "a song was added to the queue after the last song started playing")
                mixer.music.load(row['filename'])
                mixer.music.play()
                mixer.music.set_endevent(1)
                songs_in_queue = True
            else:
                print("at the end of the queue - exiting play loop")
                return

        filename = row['filename']
        id = row['id']
        con2.execute(
            "update queue set playing = datetime('now') where id = ?", (id,))
        con2.commit()


##### ENTRY POINT #####
con = sqlite3.connect("musiclibrary.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

f = open("config.json")

config = json.load(f)
f.close()

app = app()
app.install(cors_plugin('*'))
pygame.init()
mixer.init()
run(host=config["host"], port=config["port"])
