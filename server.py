from bottle import route, post, run, template, request
import sqlite3
import json
import subprocess
#import asyncio
import threading

con = sqlite3.connect("musiclibrary.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
try:
    cur.execute("drop table queue")
    cur.execute("create table queue(id INTEGER PRIMARY KEY, libraryid int, sortorder int, playing text)")
except:
    pass

f = open("config.json")
config = json.load(f)
f.close()

def query(sql, params):
    res =cur.execute(sql, params)
    rows = res.fetchall()
    return [dict(row) for row in rows]

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
    result = query("select * from queue",())
    return template('{{rows}}', rows=json.dumps(result))

@post('/play')
def play():
    thread = threading.Thread(target=playasync)
    thread.start()
    return "playing"

def playasync():
    con2 = sqlite3.connect("musiclibrary.db")
    con2.row_factory = sqlite3.Row
    cur2 = con2.cursor()
    while True:
        player = [config["player"]] + config["playerparams"] 
        result = cur2.execute("select q.id, l.filename from queue q inner join library l on q.libraryid = l.id order by q.id limit 1")
        rows = result.fetchall()
        if len(rows) == 0:
            return
        
        for row in rows:
            cur2.execute("update queue set playing = datetime('now') where id = ?",(row['id'],))
            con2.commit()
            print(f"playing song {row['filename']}")
            result = subprocess.run(player + [row['filename']], capture_output=True)
            print(f"finished playing song {row['filename']}")
            cur2.execute("delete from queue where id = ?",(row['id'],))
            con2.commit()
            print(f"delete song from playlist")


run(host='localhost', port=8080)