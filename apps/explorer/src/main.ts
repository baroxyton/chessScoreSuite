// main.js
// import Chessboard2 from "@chrisoakman/chessboard2";
// import "@chrisoakman/chessboard2/dist/chessboard2.min.css";
import { Chessboard2 } from "chessboard2";
import { Chess } from "chess.js";
import "../node_modules/@chrisoakman/chessboard2/dist/chessboard2.min.css";

const API_URL = " http://0.0.0.0:5554";

let rating = document.querySelector("#rating").value;
let color = document.querySelector("#color").value;

document.querySelector("#rating").addEventListener("change", async (event) => {
  rating = event.target.value;
  currentMove = null;
  await loadMoves();
  renderMoves();
});
document.querySelector("#color").addEventListener("change", async (event) => {
  color = event.target.value;
  await loadMoves();
  renderMoves();
});

let moves: any[] = [];
let currentMove: any = null;
let renderColumn = 0;

function sortMoves() {
  const column = renderColumn;
  if (column == 0) {
    moves.sort((a, b) => {
      return b.moveSAN.localeCompare(a.moveSAN);
    });
  }
  if (column == 1 || column == 2) {
    moves.sort((a, b) => {
      return b.move_times_played - a.move_times_played;
    });
  }
  if (column == 3) {
    moves.sort((a, b) => {
      return (
        (color == "white" ? b.whiteWins : b.blackWins) / b.timesPlayed -
        (color == "white" ? a.whiteWins : a.blackWins) / a.timesPlayed
      );
    });
  }
  if (column == 4) {
    moves.sort((a, b) => {
      return (
        (color == "white" ? b.recursiveScoreWhite : b.recursiveScoreBlack) -
        (color == "white" ? a.recursiveScoreWhite : a.recursiveScoreBlack)
      );
    });
  }
}

async function loadMovesFen() {
  const fen = btoa(defaultBoard.fen());
  const response = await fetch(`${API_URL}/fen/${fen}/${rating}/moves`);
  moves = await response.json();
}

async function loadMoves() {
  if (currentMove && currentMove.positionID) {
    const response = await fetch(
      `${API_URL}/position/${currentMove.positionID}/moves`,
    );
    moves = await response.json();
    if (!moves.length) {
      moves = [];
      return;
    }
    movesAddFen();
  } else {
    await loadMovesFen();
  }
}

async function fetchMoveFen() {
  const response = await fetch(
    `${API_URL}/fen/${btoa(defaultBoard.fen())}/${rating}/position`,
  );
  const data = await response.json();
  return data;
}

async function loadCurrentMove() {
  // check if current move is known
  let moveFound = moves.find((m) => m.fen == defaultBoard.fen());
  if (moveFound) {
    currentMove = moveFound;
  } else {
    currentMove = await fetchMoveFen();
  }
}

function movesAddFen() {
  moves.forEach((move) => {
    let boardClone = new Chess(defaultBoard.fen());
    boardClone.move(move.moveSAN);
    move.fen = boardClone.fen();
  });
}

function renderMoves() {
  // sort the moves
  sortMoves();
  const movesTable = document.querySelector("#moveTable");
  if (!movesTable) {
    console.log("ERROR: CANNOT FIND #moveTable");
    return;
  }
  function percent(value: number) {
    return (value * 100).toFixed(2) + "%";
  }
  movesTable.innerHTML =
    "<tr><th>Move</th><th>Times Played</th><th>% Played</th><th>Average Winning Rate</th><th>Recursive Winning Rate</th></tr>";
  // get the total number of moves Played
  let totalPlayed = 0;
  if (currentMove && currentMove.timesPlayed) {
    totalPlayed = currentMove.timesPlayed;
  } else {
    totalPlayed = moves.reduce((acc, move) => {
      return acc + move.move_times_played;
    }, 0);
  }
  moves.forEach((move) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${move.moveSAN}</td>
      <td>${move.move_times_played}</td>
      <td>${percent(move.move_times_played / totalPlayed)}</td>
      <td>${percent((color == "white" ? move.whiteWins : move.blackWins) / move.timesPlayed)}</td>
      <td>${percent(color == "white" ? move.recursiveScoreWhite : move.recursiveScoreBlack)}</td>
    `;
    movesTable.appendChild(row);
  });
  // add event listeners to the table headers
  const headers = movesTable.querySelectorAll("th");
  headers.forEach((header, index) => {
    header.addEventListener("click", () => {
      console.log(index);
      renderColumn = index;
      renderMoves();
    });
  });
}

let defaultBoard = new Chess();
let positions = [];

function onDragStart(source: number, piece: number) {
  return true;
}

async function onMovePlayed(event: any) {
  // get the move from the event
  let isError = false;
  let move;
  try {
    move = defaultBoard.move({
      from: event.source,
      to: event.target,
      promotion: "q", // always promote to a queen for example simplicity
    });
  } catch (error) {
    isError = true;
  }
  // illegal move
  if (isError) return "snapback";

  // make the move on the board
  board.position(defaultBoard.fen());

  await loadCurrentMove();

  await loadMoves();
  renderMoves();

  // save the move to the history
  positions.push(move);
}

const config = {
  PieceTheme: "img/chesspieces/wikipedia/{piece}.svg",
  draggable: true,
  position: "start",
  onDrop: onMovePlayed,
  onDragStart: onDragStart,
};

const board = Chessboard2("board", config);

async function init() {
  await loadCurrentMove();
  await loadMoves();
  renderMoves();
}
init();

const resetButton = document.querySelector("#reset");
if (resetButton) {
  resetButton.addEventListener("click", () => {
    defaultBoard.reset();
    board.position(defaultBoard.fen());
    positions = [];
    moves = [];
    currentMove = null;
    renderMoves();
  });
}
