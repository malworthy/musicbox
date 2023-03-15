from bottle import route, post, run, request, app, static_file, delete
from bottle_cors_plugin import cors_plugin
import json
import threading
from pygame import mixer
import pygame
from player import playasync
from data import create_connection, get_next_song, reset_queue, setplaying
import os
import time


def query(sql, params):
    res = con.execute(sql, params)
    rows = res.fetchall()
    return [dict(row) for row in rows]


@route('/ui')
def ui():
    return static_file("ui.html", "./ui/")


@route('/ui/<file>')
def ui2(file):
    return static_file(file, "./ui/")


@route('/coverart/<id>')
def coverart(id):
    result = query(
        "select coverart from library where id = ? and coverart is not null", (id,))
    if len(result) > 0:
        path = os.path.dirname(result[0]["coverart"])
        filename = os.path.basename(result[0]["coverart"])
        return static_file(filename, path)


@route('/search')
def search():
    include_songs = len(request.query.search) > 1
    x = f"%{request.query.search}%"
    print(x)
    sql = """
        select album, case when count(*) > 1 then 'Various' else max(albumartist) end artist, null as tracktitle, 0 as id, 0 as length 
        from (select distinct albumartist, album from library where album like ? or artist like ? or albumartist like ?) sq 
        group by album       
    """

    if include_songs:
        sql += """
            union 
            select album, artist, tracktitle, id, length
            from library
            where tracktitle like ?"""

    sql += "order by tracktitle, artist;"

    if include_songs:
        result = query(sql, (x, x, x, x))
    else:
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
    result = con.execute(sql, (id, ))
    con.commit()
    result = query("select count(*) as queueCount from queue", ())
    return json.dumps(result[0])


@delete('/<id>')
def remove(id):
    sql = "delete from queue where id = ?"
    con.execute(sql, (id, ))
    con.commit()
    result = query("select count(*) as queueCount from queue", ())
    return json.dumps(result[0])


@delete('/all')
def remove():
    sql = "delete from queue"
    con.execute(sql)
    con.commit()
    return """{ "queueCount" : 0 }"""


@route("/queue")
def queue():
    result = query(
        "select q.id as queueId, l.* from queue q inner join library l on q.libraryid = l.id", ())
    return json.dumps(result)


@route("/history")
def history():
    sql = """
        select datetime(dateplayed,'localtime') as dateplayed, l.artist, l.tracktitle, l.album 
        from history h 
        inner join library l on l.id = h.libraryid 
        order by dateplayed desc;
    """
    return json.dumps(query(sql, ()))


@route("/status")
def status():
    sql = """
        select l.*, 1 as playing, (select count(*) from queue) as queueCount 
        from queue q inner join library l on q.libraryid = l.id 
        where playing is not null
    """
    result = query(sql, ())
    if len(result) >= 1:
        dict = result[0]
        dict['paused'] = not mixer.music.get_busy()

        return json.dumps(dict)

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
    if next_song == None:
        return """{"status" : "no songs in queue"}"""
    setplaying(next_song['id'], con)
    thread = threading.Thread(target=playasync, args=(next_song,))
    thread.start()
    return """{"status" : "play started", "id" : """ + f"{next_song['libraryid']}" + "}"


@post('/stop')
def stop():
    con.execute("update queue set canplay = 0")
    con.execute("delete from queue where playing is not null")
    con.commit()
    mixer.music.stop()
    return """{"status" : "stopped"}"""


@post('/skip')
def skip():
    stop()
    time.sleep(1)
    return play()


@post('/pause')
def pause():
    if mixer.music.get_busy():
        mixer.music.pause()
        return """{"paused" : true}"""
    else:
        mixer.music.unpause()
        return """{"paused" : false}"""


@post('/queuealbum')
def queuealbum():
    params = request.json
    con.execute(
        "insert into queue(libraryid, canplay) select id, 1 from library where album = ? order by cast(tracknumber as INT), filename", (params["album"],))
    con.commit()

    return """{"status" : "queued"}"""


@post('/play/<id>')
def playsong(id):
    if mixer.music.get_busy():
        return """{"status" : "already playing"}"""
    con.execute("delete from queue")
    add(id)
    return play()


@post('/playalbum')
def playalbum():
    if mixer.music.get_busy():
        return """{"status" : "already playing"}"""

    params = request.json
    con.execute("delete from queue")
    con.execute(
        "insert into queue(libraryid) select id from library where album = ? order by cast(tracknumber as INT), filename", (params["album"],))
    con.commit()

    return play()


@post('/rand/<num>')
def random_queue(num):
    con.execute("delete from queue")
    con.execute(
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
    con.execute(
        "delete from library where albumartist = 'mixtape' and album = ?", (name,))
    con.execute(sql, (name,))
    con.commit()
    return """{"status" : "success"}"""


@delete('/mix/<name>')
def delete_mixtape(name):
    con.execute(
        "delete from library where albumartist = 'mixtape' and album = ?", (name,))
    con.commit()
    return """{"status" : "success"}"""


##### ENTRY POINT #####
con = create_connection()

reset_queue(con)

f = open("config.json")
config = json.load(f)
f.close()

app = app()
app.install(cors_plugin('*'))
pygame.init()
mixer.init()

run(host=config["host"], port=config["port"])
