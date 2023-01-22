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

const doAjax = async (verb, endpoint, data = null) => {
  const options = {
    method: verb,
    headers: {
      "Content-type": "application/json; charset=UTF-8",
    },
  };
  if (data != null) options.body = JSON.stringify(data);
  const response = await fetch(`${baseUrl}/${endpoint}`, options); 
  if (response.ok) {
    return await response.json(); 
  } else {
    return null;
  }
};

async function updateStatus() {
  const statusDiv = document.getElementById("status");
  const playBtn = document.getElementById("play");

  const songDetails = await doAjax("GET", "status");
  if (songDetails.playing === 1) {
    statusDiv.innerHTML = `<p>Now playing: ${songDetails.tracktitle} by ${songDetails.artist}</p>`;
    playBtn.innerHTML = "Stop";
    playBtn.onclick = () => stopPlay();
  } else {
    statusDiv.innerHTML = "<p>Not Playing</p>";
    playBtn.innerHTML = "Play";
    playBtn.onclick = () => play();
  }
  updateQueueStatus(songDetails.queueCount);
}

async function stopPlay() {
  await doAjax("POST", "stop");
  const statusDiv = document.getElementById("status");
  const playBtn = document.getElementById("play");
  statusDiv.innerHTML = "<p>Not Playing</p>";
  playBtn.innerHTML = "Play";
  playBtn.onclick = () => play();
}

async function play() {
  await doAjax("POST", "play");
  updateStatus();
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

async function playAlbum(album, artist) {
  await doAjax("POST", "playalbum", { album: album, artist: artist });
  updateStatus();
}

async function queueAlbum(album, artist) {
  await doAjax("POST", "queuealbum", { album: album, artist: artist });
  updateStatus();
}

function updateQueueStatus(count) {
  document.getElementById("queue").innerHTML = `Queue (${count})`;
}

async function queueSong(id) {
  const result = await doAjax("POST", `add/${id}`);
  updateQueueStatus(result.queueCount);
}

async function getAlbum(name) {
  name = decodeURIComponent(name);
  var songs = await doAjax("GET", `album?search=${encodeURIComponent(name)}`);
  if (songs === null) return;
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
    addButton(newRow, "Play", () => playOneSong(song.id));
    addButton(newRow, "Add", () => queueSong(song.id));
  }
}

function addButton(row, text, clickEvent) {
  let newCell = row.insertCell(-1);
  let button = document.createElement("button");
  button.textContent = text;
  button.onclick = clickEvent;
  newCell.appendChild(button);
}

async function getAlbums() {
  const search = document.getElementById("search").value;
  const albums = await doAjax("GET", `search?search=${search}`);
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
      `${album.artist}`,
      `<a href="#" onclick="getAlbum('${encodeURIComponent(album.album).replace(/'/g, "%27")}')"> ${album.album}</a>`,
    ]);
    addButton(newRow, "Play", () => playAlbum(album.album, album.artist));
    addButton(newRow, "Add", () => queueAlbum(album.album, album.artist));
  }
}

function fmtMSS(s) {
  return (s - (s %= 60)) / 60 + (9 < s ? ":" : ":0") + s;
}

async function removeFromQueue(id, row) {
  const result = await doAjax("DELETE",`${id}`);
  updateQueueStatus(result.queueCount);
  row.innerHTML = "";
}

async function playOneSong(id) {
  await doAjax("POST", `play/${id}`);
  updateStatus();
}

async function getQueue() {
  document.getElementById("tablehead").innerHTML = `<tr class="bright">
    <td>#</td>
    <td>Song</td>
    <td>Artist</td>
    <td>Album</td>
    <td>Length</td>
    </tr>`;
  const queue = await doAjax("GET", "queue");
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
    addButton(newRow, "Del", () => removeFromQueue(song.queueId, newRow));
  }
  updateQueueStatus(i-1);
}
