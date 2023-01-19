#pip install bottle
#pip install bottle-cors-plugin
#pip install pygame
from bottle import route, post, run, template, request, app, static_file
from bottle_cors_plugin import cors_plugin
import sqlite3
import json
import subprocess
#import asyncio
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
    sql = "select distinct artist, album from library where album like ? or artist like ? order by artist, album"
    res =cur.execute(sql, (x,x))
    rows = res.fetchall()
    result = [dict(row) for row in rows]
    #return rows
    return template('{{rows}}', rows=json.dumps(result))

@route('/album')
def album():
    search = request.query.search
  
    sql =  sql = "select * from library where album = ? order by artist, album, cast(tracknumber as INT), filename"
    result = query(sql, (search,))
    
    return template('{{rows}}', rows=json.dumps(result))

@post('/add/<id>')
def add(id):
    sql = "insert into queue(libraryid) values(?)"
    result = cur.execute(sql, (id, ))
    con.commit()
    result = query("select * from queue",())
    return template('{{rows}}', rows=json.dumps(result))

@route("/queue")
def queue():
    result = query("select l.* from queue q inner join library l on q.libraryid = l.id",())
    return template('{{rows}}', rows=json.dumps(result))

@route("/playing")
def playing():
    result = query("select l.*, 1 as playing from queue q inner join library l on q.libraryid = l.id where playing is not null",())
    if len(result) == 1:
        return template('{{rows}}', rows=json.dumps(result[0]))
    return """{"playing" : 0}"""

@post('/play')
def play():
    cur.execute("update queue set canplay = 1")
    con.commit()
    thread = threading.Thread(target=playasync)
    thread.start()
    return "playing"

@post('/stop')
def stop():
    cur.execute("update queue set canplay = 0")
    con.commit()
    mixer.music.stop()
    return "stopped"

@post('/playalbum')
def playalbum():
    params = request.json
    cur.execute("delete from queue")
    cur.execute("insert into queue(libraryid) select id from library where album = ? and artist = ? order by cast(tracknumber as INT), filename", (params["album"], params["artist"]))
    con.commit()

    print(request.json)
    return play()

def playasync():
    con2 = sqlite3.connect("musiclibrary.db")
    con2.row_factory = sqlite3.Row
    cur2 = con2.cursor()
    while True:
        player = [config["player"]] + config["playerparams"] 
        result = cur2.execute("select q.id, l.filename from queue q inner join library l on q.libraryid = l.id where canplay = 1 order by q.id limit 1")
        rows = result.fetchall()
        if len(rows) == 0:
            return
        
        for row in rows:
            cur2.execute("update queue set playing = datetime('now') where id = ?",(row['id'],))
            con2.commit()
            print(f"playing song {row['filename']}")
            #result = subprocess.run(player + [row['filename']], capture_output=True)
            #mixer.init()
            mixer.music.load(row['filename'])
            mixer.music.play()
            while mixer.music.get_busy():  # wait for music to finish playing
                time.sleep(1)

            print(f"finished playing song {row['filename']}")
            cur2.execute("delete from queue where id = ?",(row['id'],))
            con2.commit()
            print(f"delete song from playlist")

app = app()
app.install(cors_plugin('*'))
mixer.init()
run(host='localhost', port=8080)