import sqlite3
import json

con = sqlite3.connect("musiclibrary.db")
cur = con.cursor()

x = input("> ")
sql = "select distinct album from library where album like ?"
res =cur.execute(sql, (x,))
print(res.fetchall())