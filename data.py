import sqlite3


def create_connection():
    connection = sqlite3.connect("musiclibrary.db")
    connection.row_factory = sqlite3.Row

    return connection


def get_next_song(db_conn):
    get_song_sql = """select q.id, l.filename, l.id as libraryid 
            from queue q inner join library l on q.libraryid = l.id 
            where canplay = 1 and playing is null order by q.id limit 1"""
    curs = db_conn.execute(get_song_sql)
    return curs.fetchone()


def setplaying(id, db_conn):
    db_conn.execute(
        "update queue set playing = datetime('now') where id = ?", (id,))

    sql = """insert into history(libraryid, dateplayed) 
             select libraryid, playing 
             from queue 
             where playing is not null"""
    db_conn.execute(sql)
    db_conn.commit()
