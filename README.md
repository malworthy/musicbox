# musicbox

A lightweight music server for playing local files, with a retro user interface.  Like mopidy but without the streaming. Perfect for running on a raspberry pi.

Written in python and vanilla.js.

***Still in development - not ready for general use just yet***

## installing/running

Install the following python dependencies:
```
pip install bottle
pip install bottle-cors-plugin
pip install pygame
pip install music-tag
```

You may also need install some additional libraries (command for debian based systems):
```
sudo apt-get install libsdl2-mixer-2.0-0 libsdl2-image-2.0-0 libsdl2-2.0-0
```

Clone the repository:
```
git clone https://github.com/malworthy/musicbox.git
```
Create a config.json file:  
```
{
    "library" : "/path/to/library/",
    "host" : "localhost",
    "port" : 8080
}
```
- Change "library" to point to your music library.
- Change "host" to "0.0.0.0" to allow remote connections to the server.
- Change "port" if need the server to run on a different port.


Update database with library:
```
python update_library.py
```

Run the server:
```
python server.py
```

Browse to UI:
http://localhost:8080/ui

NOTE: replace 'localhost' with the address of server you are running off.   

One the library has been updated, you can run the following to add any new songs:
```
python update_library.py --add
```

