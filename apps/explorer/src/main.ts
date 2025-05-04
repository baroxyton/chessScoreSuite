// main.js
// import Chessboard2 from "@chrisoakman/chessboard2";
// import "@chrisoakman/chessboard2/dist/chessboard2.min.css";
import { Chessboard2 } from "chessboard2";
import { Chess } from "chess.js";
import "../node_modules/@chrisoakman/chessboard2/dist/chessboard2.min.css";

const API_URL = " http://0.0.0.0:5554";

let rating = document.querySelector("#rating").value;
let color = document.querySelector("#color").value;

async function get_moves_fen(fen: string) {
  const response = await fetch(`${API_URL}/fen/${fen}/${rating}/moves`);
  const data = await response.json();
  console.log(data);
  return data;
}

let defaultBoard = new Chess();
let positions = [];

function onDragStart(source, piece) {
  return true;
}

function onMovePlayed(event) {
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
  get_moves_fen(btoa(defaultBoard.fen()));

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
