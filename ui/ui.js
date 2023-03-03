ready(start);

function start() {
  updateStatus();
  setInterval(() => updateStatus(), 1000 * 10);
}

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
  const response = await fetch(`/${endpoint}`, options);
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
  document.getElementById("content").innerHTML = "";
  for (const song of songs) {
    const listItem = document.createElement("li");
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${i++}. ${song.tracktitle} ${fmtMSS(song.length)}</h4>
    <p>${song.artist} - ${song.album}</p>`;

    const divButtons = document.createElement("div");
    divButtons.appendChild(addButton("Play", () => playOneSong(song.id)));
    divButtons.appendChild(addButton("Add", () => queueSong(song.id)));

    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
}

function addButton(text, clickEvent) {
  let button = document.createElement("button");
  button.textContent = text;
  button.onclick = clickEvent;
  return button;
}

async function doCommand(command) {
  if (command == ":clear") await doAjax("DELETE", "all");
  else if (command.startsWith(":mix ")) {
    var name = command.substring(5);
    await doAjax("POST", `mix/${name}`);
  } else if (command.startsWith(":delmix ")) {
    var name = command.substring(8);
    await doAjax("DELETE", `mix/${name}`);
  } else if (command.startsWith(":rand ")) {
    var num = parseInt(command.substring(6));
    if (num > 0) await doAjax("POST", `rand/${num}`);
  } else if (command.startsWith(":hist")) {
    await getHistory();
  }
  document.getElementById("search").value = "";
}

async function processCommand() {
  const command = document.getElementById("search").value;
  if (command.length > 0 && command[0] == ":") await doCommand(command);
  else await getAlbums();

  await updateStatus();
}

async function getAlbums() {
  const search = document.getElementById("search").value;
  const albums = await doAjax("GET", `search?search=${search}`);

  document.getElementById("content").innerHTML = "";
  for (const album of albums) {
    const listItem = document.createElement("li");
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${album.artist}</h4><p><a href="#" onclick="getAlbum('${encodeURIComponent(
      album.album
    ).replace(/'/g, "%27")}')"> ${album.album}</a></p>`;

    const divButtons = document.createElement("div");
    divButtons.appendChild(addButton("Play", () => playAlbum(album.album, album.artist)));
    divButtons.appendChild(addButton("Add", () => queueAlbum(album.album, album.artist)));

    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
}

function fmtMSS(s) {
  return (s - (s %= 60)) / 60 + (9 < s ? ":" : ":0") + s;
}

async function removeFromQueue(id, row) {
  const result = await doAjax("DELETE", `${id}`);
  updateQueueStatus(result.queueCount);
  row.parentNode.removeChild(row);
}

async function playOneSong(id) {
  await doAjax("POST", `play/${id}`);
  updateStatus();
}

async function getQueue() {
  const queue = await doAjax("GET", "queue");
  let i = 1;
  document.getElementById("content").innerHTML = "";

  for (const song of queue) {
    const listItem = document.createElement("li");
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${i++}. ${song.tracktitle} ${fmtMSS(song.length)}</h4>
    <p>${song.artist} - ${song.album}</p>`;

    const divButtons = document.createElement("div");
    divButtons.appendChild(addButton("Del", () => removeFromQueue(song.queueId, listItem)));

    listItem.appendChild(divText);
    listItem.appendChild(divButtons);
    document.getElementById("content").appendChild(listItem);
  }
  updateQueueStatus(i - 1);
}

async function getHistory() {
  const hist = await doAjax("GET", "history");
  document.getElementById("content").innerHTML = "";

  for (const song of hist) {
    const listItem = document.createElement("li");
    const divText = document.createElement("div");
    divText.innerHTML = `<h4>${song.tracktitle} </h4>
    <p>Played on: ${song.dateplayed}</p>
    <p>${song.artist} - ${song.album}</p>`;

    listItem.appendChild(divText);
    document.getElementById("content").appendChild(listItem);
  }
}
