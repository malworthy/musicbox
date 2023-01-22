# musicbox

A lightweight music server for playing local files, with a retro user interface.  Like mopidy but without the streaming.

Written in python and vanilla.js.

***Still in development - not ready for general use just yet***

## installing/running

Install the following python dependencies:

- pip install bottle
- pip install bottle-cors-plugin
- pip install pygame

Create a config.json file:
```
{
    "library" : "[Enter the path to your music collection here]",
}
```

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

NOTE: replace 'localhost' with ip address of server you are running off.   

