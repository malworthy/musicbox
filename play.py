#pip install websockets
import asyncio
import websockets
import sqlite3
import json
import threading
import time
from pygame import mixer

con = sqlite3.connect("musiclibrary.db")
con.row_factory = sqlite3.Row
cur = con.cursor()

# create handler for each connection
async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, "localhost", 8081):
        await asyncio.Future()  # run forever

mixer.init()
asyncio.run(main())