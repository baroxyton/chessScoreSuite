// main.js
// import Chessboard2 from "@chrisoakman/chessboard2";
// import "@chrisoakman/chessboard2/dist/chessboard2.min.css";
import { Chessboard2 } from "chessboard2";
import { Chess } from "chess.js";
import "../node_modules/@chrisoakman/chessboard2/dist/chessboard2.min.css";

const API_URL = " http://0.0.0.0:5554";

let rating = document.querySelector("#rating").value;
let color = document.querySelector("#color").value;

let moves = [];

async function getMovesFen(fen: string) {
  const response = await fetch(`${API_URL}/fen/${fen}/${rating}/moves`);
  const data = await response.json();
  return data;
}

async function loadMoves() {
  const fen = btoa(defaultBoard.fen());
  const response = await fetch(`${API_URL}/fen/${fen}/${rating}/moves`);
  moves = await response.json();
}

function renderMoves() {
  const movesTable = document.querySelector("#moveTable");
  movesTable.innerHTML =
    "<tr><th>Move</th><th>Times Played</th><th>% Played</th><th>Average Winning Rate</th><th>Recursive Winning Rate</th></tr>";
  moves.forEach((move) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${move.moveSAN}</td>
      <td>${move.move_times_played}</td>
      <td>${move.move_times_played / 1000}</td>
      <td>${(color == "white" ? move.whiteWins : move.blackWins) / move.timesPlayed}</td>
      <td>${color == "white" ? move.recursiveScoreWhite : move.recursiveScoreBlack}</td>
    `;
    movesTable.appendChild(row);
  });
}

let defaultBoard = new Chess();
let positions = [];

function onDragStart(source, piece) {
  return true;
}

async function onMovePlayed(event) {
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
