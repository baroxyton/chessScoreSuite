// main.js
// import Chessboard2 from "@chrisoakman/chessboard2";
// import "@chrisoakman/chessboard2/dist/chessboard2.min.css";
import { Chessboard2 } from "chessboard2";
import "../node_modules/@chrisoakman/chessboard2/dist/chessboard2.min.css";

const config = {
  PieceTheme: "img/chesspieces/wikipedia/{piece}.svg",
  position: "start",
};

const board = Chessboard2("board", config);
