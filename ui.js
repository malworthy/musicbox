const baseUrl = "http://localhost:8080";
//const baseUrl = "http://192.168.1.72:8080"

function ajaxCall(verb, endpoint, callback)
{
  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      callback();
    }
  };
  httpRequest.open(verb, `${baseUrl}/${endpoint}`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  httpRequest.send();
}

function updateStatus() {
  const statusDiv = document.getElementById("status");

  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      const text = decodeHtml(httpRequest.responseText);
      const songDetails = JSON.parse(text);
      if (songDetails.playing === 1)
        statusDiv.innerHTML = `<p>Now playing: ${songDetails.tracktitle} by ${songDetails.artist}</p><button onclick="stopPlay()">Stop</button>`;
      else statusDiv.innerHTML = "<p>Not Playing</p>";
    }
  };
  httpRequest.open("GET", `${baseUrl}/playing`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  httpRequest.send();
}

function stopPlay() {
  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    const statusDiv = document.getElementById("status");
    statusDiv.innerHTML = "<p>Not Playing</p>";
  };
  httpRequest.open("POST", `${baseUrl}/stop`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  httpRequest.send();
}

function addRow(columns) {
  let tableRef = document.getElementById("albumsbody");
  let newRow = tableRef.insertRow(-1);

  for (const col of columns) {
    let newCell = newRow.insertCell(-1);
    newCell.innerHTML = col;
  }
  return newRow;
}

function playAlbum(album, artist) {
  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      updateStatus();
    }
  };
  httpRequest.open("POST", `${baseUrl}/playalbum`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  httpRequest.send(JSON.stringify({ album: album, artist: artist }));
}

function queueAlbum(album, artist) {
  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      updateStatus();
    }
  };
  httpRequest.open("POST", `${baseUrl}/queuealbum`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  httpRequest.send(JSON.stringify({ album: album, artist: artist }));
}

function queueSong(id) {
  alert(id);
}

function getAlbum(name) {
  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      const text = decodeHtml(httpRequest.responseText);
      const songs = JSON.parse(text);
      let i = 1;
      document.getElementById("tablehead").innerHTML = `<tr class="bright">
        <td>#</td>
        <td>Song</td>
        <td>Artist</td>
        <td>Album</td>
        <td>Length</td>
        </tr>`;
      document.getElementById("albumsbody").innerHTML = "";
      for (const song of songs) {
        const newRow = addRow([
          i++,
          song.tracktitle,
          song.artist,
          song.album,
          fmtMSS(song.length),
        ]);

        const newCell = newRow.insertCell(-1);
        const button = document.createElement("button");
        button.textContent = "Play";
        button.onclick = () => queueSong(album.id);
        newCell.appendChild(button);
      }
    }
  };
  httpRequest.open("GET", `${baseUrl}/album?search=${encodeURIComponent(name)}`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  httpRequest.send();
}

function addButton(row, text, clickEvent) {
  let newCell = row.insertCell(-1);
  let button = document.createElement("button");
  button.textContent = text;
  button.onclick = clickEvent;
  newCell.appendChild(button);
}

function getAlbums() {
  const search = document.getElementById("search").value;
  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      const text = decodeHtml(httpRequest.responseText);
      const albums = JSON.parse(text);
      let i = 1;
      document.getElementById("tablehead").innerHTML = `<tr class="bright">
              <td>#</td>
              <td>Artist</td>
              <td>Album</td>
              </tr>`;
      document.getElementById("albumsbody").innerHTML = "";
      for (const album of albums) {
        const newRow = addRow([
          i++,
          `<a href="#">${album.artist}`,
          `<a href="#" onclick="getAlbum('${album.album}')"> ${album.album}`,
        ]);
        addButton(newRow, "Play", () => playAlbum(album.album, album.artist));
        addButton(newRow, "Add", () => queueAlbum(album.album, album.artist));
      }
    }
  };
  httpRequest.open("GET", `${baseUrl}/search?search=${search}`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  httpRequest.send();
}

function fmtMSS(s) {
  return (s - (s %= 60)) / 60 + (9 < s ? ":" : ":0") + s;
}

function getQueue() {
  document.getElementById("tablehead").innerHTML = `<tr class="bright">
    <td>#</td>
    <td>Song</td>
    <td>Artist</td>
    <td>Album</td>
    <td>Length</td>
    </tr>`;
  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      const text = decodeHtml(httpRequest.responseText);
      const queue = JSON.parse(text);
      let i = 1;
      document.getElementById("albumsbody").innerHTML = "";
      for (const song of queue) {
        addRow([
          i++,
          song.tracktitle,
          song.artist,
          song.album,
          fmtMSS(song.length),
        ]);
        //console.log([album.artist, album.album]);
      }
    }
  };
  httpRequest.open("GET", `${baseUrl}/queue`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  httpRequest.send();
}

function decodeHtml(html) {
  let areaElement = document.createElement("textarea");
  areaElement.innerHTML = html;
  const decoded = areaElement.value;
  areaElement.remove();

  return decoded;
}
