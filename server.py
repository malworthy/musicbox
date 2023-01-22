#pip install bottle
#pip install bottle-cors-plugin
#pip install pygame
from bottle import route, post, run, request, app, static_file, delete
from bottle_cors_plugin import cors_plugin
import sqlite3
import json
import threading
import time
from pygame import mixer

con = sqlite3.connect("musiclibrary.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
try:
    cur.execute("drop table queue")
    cur.execute("create table queue(id INTEGER PRIMARY KEY, libraryid int, sortorder int, playing text, canplay int)")
except:
    pass

f = open("config.json")
config = json.load(f)
f.close()

def query(sql, params):
    res =cur.execute(sql, params)
    rows = res.fetchall()
    return [dict(row) for row in rows]

@route('/ui')
def ui():
    return static_file("ui.html","./")

@route('/js')
def ui():
    return static_file("ui.js","./")

@route('/css')
def ui():
    return static_file("ui.css","./")

@route('/search')
def search():
    x = request.query.search
    x = '%' + x + '%'
    #sql = "select distinct albumartist as artist, album from library where album like ? or artist like ? or albumartist like ? order by artist, album"
    sql = """
        select album, case when count(*) > 1 then 'Various' else max(albumartist) end artist 
        from (select distinct albumartist, album from library where album like ? or artist like ? or albumartist like ?) sq 
        group by album
        order by artist;
    """
    res =cur.execute(sql, (x,x,x))
    rows = res.fetchall()
    result = [dict(row) for row in rows]
    #return rows
    return json.dumps(result)

@route('/album')
def album():
    search = request.query.search
  
    sql =  sql = "select * from library where album = ? order by artist, album, cast(tracknumber as INT), filename"
    result = query(sql, (search,))

    return json.dumps(result)

@post('/add/<id>')
def add(id):
    sql = "insert into queue(libraryid) values(?)"
    result = cur.execute(sql, (id, ))
    con.commit()
    result = query("select count(*) as queueCount from queue",())
    return json.dumps(result[0])

@delete('/<id>')
def remove(id):
    sql = "delete from queue where id = ?"
    cur.execute(sql, (id, ))
    con.commit()
    result = query("select count(*) as queueCount from queue",())
    return json.dumps(result[0])

@delete('/all')
def remove():
    sql = "delete from queue"
    cur.execute(sql)
    con.commit()
    return """{ "queueCount" : 0 }"""


@route("/queue")
def queue():
    result = query("select q.id as queueId, l.* from queue q inner join library l on q.libraryid = l.id",())
    return json.dumps(result)

@route("/status")
def status():
    sql = """
        select l.*, 1 as playing, (select count(*) from queue) as queueCount 
        from queue q inner join library l on q.libraryid = l.id 
        where playing is not null
    """
    result = query(sql,())
    if len(result) == 1:
        return json.dumps(result[0])

    result = query("select count(*) as queueCount , 0 as playing from queue",())
    return json.dumps(result[0])

@post('/play')
def play():
    if mixer.music.get_busy() or is_playing():
        return """{"status" : "already playing"}"""

    cur.execute("update queue set canplay = 1")
    con.commit()
    thread = threading.Thread(target=playasync)
    thread.start()
    return """{"status" : "play started"}"""

@post('/stop')
def stop():
    cur.execute("update queue set canplay = 0")
    con.commit()
    mixer.music.stop()
    return """{"status" : "stopped"}"""

@post('/queuealbum')
def queuealbum():
    params = request.json
    cur.execute("insert into queue(libraryid) select id from library where album = ? order by cast(tracknumber as INT), filename", (params["album"],))
    con.commit()

    return """{"status" : "queued"}""" 

@post('/play/<id>')
def playsong(id):
    if mixer.music.get_busy() or is_playing():
        return """{"status" : "already playing"}"""
    cur.execute("delete from queue")
    add(id)
    return play()

@post('/playalbum')
def playalbum():
    if mixer.music.get_busy() or is_playing():
        return """{"status" : "already playing"}"""

    params = request.json
    cur.execute("delete from queue")
    cur.execute("insert into queue(libraryid) select id from library where album = ? order by cast(tracknumber as INT), filename", (params["album"],))
    con.commit()

    print(request.json)
    return play()

def is_playing():
    return False # for now just rely on is busy - but won't work in the 1 seconds between songs

def playasync():
    con2 = sqlite3.connect("musiclibrary.db")
    con2.row_factory = sqlite3.Row
    cur2 = con2.cursor()
    while True:
        result = cur2.execute("select q.id, l.filename from queue q inner join library l on q.libraryid = l.id where canplay = 1 order by q.id limit 1")
        rows = result.fetchall()
        if len(rows) == 0:
            return
        
        for row in rows:
            cur2.execute("update queue set playing = datetime('now') where id = ?",(row['id'],))
            con2.commit()
            print(f"playing song {row['filename']}")
            mixer.music.load(row['filename'])
            mixer.music.play()
            while mixer.music.get_busy():  # wait for music to finish playing
                time.sleep(1)

            print(f"finished playing song {row['filename']}")
            cur2.execute("delete from queue where id = ?",(row['id'],))
            con2.commit()
            print(f"delete song from playlist")

##### ENTRY POINT #####
app = app()
app.install(cors_plugin('*'))
mixer.init()
run(host='localhost', port=8080)