const baseUrl = "http://localhost:8080";
//const baseUrl = "http://192.168.1.72:8080"

ready(updateStatus);

function ready(fn) {
  if (document.readyState !== "loading") {
    fn();
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

//TODO: replace with fetch
function ajaxCall(verb, endpoint, callback, data = null) {
  const httpRequest = new XMLHttpRequest();
  httpRequest.onreadystatechange = () => {
    if (httpRequest.readyState === XMLHttpRequest.DONE) {
      callback(httpRequest);
    }
  };
  httpRequest.open(verb, `${baseUrl}/${endpoint}`, true);
  httpRequest.setRequestHeader(
    "Content-Type",
    "application/json;charset=UTF-8"
  );
  if (!data) httpRequest.send();
  else httpRequest.send(JSON.stringify(data));
}

function updateStatus() {
  const statusDiv = document.getElementById("status");
  const playBtn = document.getElementById("play");

  ajaxCall("GET", "playing", (httpRequest) => {
    const text = decodeHtml(httpRequest.responseText);
    const songDetails = JSON.parse(text);
    if (songDetails.playing === 1) {
      statusDiv.innerHTML = `<p>Now playing: ${songDetails.tracktitle} by ${songDetails.artist}</p>`;
      playBtn.innerHTML = "Stop";
      playBtn.onclick = () => stopPlay();
    } else {
      statusDiv.innerHTML = "<p>Not Playing</p>";
      playBtn.innerHTML = "Play";
      playBtn.onclick = () => play();
    }
  });
}

function stopPlay() {
  ajaxCall("POST", "stop", () => {
    const statusDiv = document.getElementById("status");
    const playBtn = document.getElementById("play");
    statusDiv.innerHTML = "<p>Not Playing</p>";
    playBtn.innerHTML = "Play";
    playBtn.onclick = () => play();
  });
}

function play() {
  ajaxCall("POST", "play", () => updateStatus());
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
  ajaxCall("POST", "playalbum", updateStatus, { album: album, artist: artist });
}

function queueAlbum(album, artist) {
  ajaxCall("POST", "queuealbum", updateStatus, {
    album: album,
    artist: artist,
  });
}

function queueSong(id) {
  alert(id);
}

function getAlbum(name) {
  ajaxCall("GET", `album?search=${encodeURIComponent(name)}`, (httpRequest) => {
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
      addButton(newRow, "Play", () => queueSong(album.id));
      addButton(newRow, "Add", () => queueSong(album.id));
    }
  });
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
  ajaxCall("GET", `search?search=${search}`, (httpRequest) => {
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
  });
}

function fmtMSS(s) {
  return (s - (s %= 60)) / 60 + (9 < s ? ":" : ":0") + s;
}

function removeFromQueue(id) {
  console.log("remove from queue called");
}

function getQueue() {
  document.getElementById("tablehead").innerHTML = `<tr class="bright">
    <td>#</td>
    <td>Song</td>
    <td>Artist</td>
    <td>Album</td>
    <td>Length</td>
    </tr>`;
  ajaxCall("GET", `queue`, (httpRequest) => {
    const text = decodeHtml(httpRequest.responseText);
    const queue = JSON.parse(text);
    let i = 1;
    document.getElementById("albumsbody").innerHTML = "";
    for (const song of queue) {
      const newRow = addRow([
        i++,
        song.tracktitle,
        song.artist,
        song.album,
        fmtMSS(song.length),
      ]);
      addButton(newRow, "Del", () => removeFromQueue(song.id));
    }
  });
}

function decodeHtml(html) {
  let areaElement = document.createElement("textarea");
  areaElement.innerHTML = html;
  const decoded = areaElement.value;
  areaElement.remove();

  return decoded;
}
