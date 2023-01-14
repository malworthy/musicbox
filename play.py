import sqlite3
import json
import subprocess
import sys

con = sqlite3.connect("musiclibrary.db")
cur = con.cursor()
f = open("config.json")
config = json.load(f)
f.close()

x = input("> ")
x = '%' + x + '%'
sql = "select distinct artist, album from library where album like ? or artist like ?"
res =cur.execute(sql, (x,x))
rows = res.fetchall()
count = 0
for row in rows:
    count += 1
    artist = row[0]
    album = row[1]
    print(f"{count}. {artist} - {album}")
n = input("> ")
i = int(n)-1
sql = "select * from library where album = ? and artist = ?"
res = cur.execute(sql,(rows[i][1], rows[i][0]))
rows = res.fetchall()
player = [config["player"]] + config["playerparams"] 
for row in rows:
    print(row[0])
    result = subprocess.run(player + [row[0]], capture_output=True)