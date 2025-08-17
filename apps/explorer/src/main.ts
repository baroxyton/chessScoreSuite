// main.js
// import Chessboard2 from "@chrisoakman/chessboard2";
// import "@chrisoakman/chessboard2/dist/chessboard2.min.css";
import { Chessboard2 } from "chessboard2";
import { Chess } from "chess.js";
import "../node_modules/@chrisoakman/chessboard2/dist/chessboard2.min.css";

const API_URL = "http://0.0.0.0:5554";

const ratingSelect = document.querySelector("#rating") as HTMLSelectElement;
const colorSelect = document.querySelector("#color") as HTMLSelectElement;

let rating = (ratingSelect?.value || "").trim();
let color = (colorSelect?.value || "white").trim();

ratingSelect?.addEventListener("change", async (event) => {
  rating = (event.target as HTMLSelectElement).value.trim();
  currentMove = null;
  await loadMoves();
  renderMoves();
});
colorSelect?.addEventListener("change", async (event) => {
  color = (event.target as HTMLSelectElement).value.trim();
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

function fenParam(): string {
  // URL-encode the base64 so it’s safe in a URL path segment
  return encodeURIComponent(btoa(defaultBoard.fen()));
}

async function loadMovesFen() {
  const response = await fetch(`${API_URL}/fen/${fenParam()}/${rating}/moves`);
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
    `${API_URL}/fen/${fenParam()}/${rating}/position`,
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

// ========================= Tabs + Blitz (new) =========================
/**
 * Blitz vs API engine: second board with clocks and skill selection.
 * Adjust ENGINE_MOVE_ENDPOINT to match your backend if needed.
 */

const explorerView = document.getElementById("explorerView");
const blitzView = document.getElementById("blitzView");
const tabExplorer = document.getElementById("tab-explorer");
const tabBlitz = document.getElementById("tab-blitz");

function showExplorer() {
  if (explorerView) explorerView.style.display = "";
  if (blitzView) blitzView.style.display = "none";
}
function showBlitz() {
  if (explorerView) explorerView.style.display = "none";
  if (blitzView) blitzView.style.display = "";
}
tabExplorer?.addEventListener("click", showExplorer);
tabBlitz?.addEventListener("click", showBlitz);

// ---- Blitz DOM ----
const blitzColorSel = document.getElementById("blitzColor") as HTMLSelectElement | null;
const blitzSkillSel = document.getElementById("blitzSkill") as HTMLSelectElement | null;
const blitzTimeSel = document.getElementById("blitzTime") as HTMLSelectElement | null;
const blitzStartBtn = document.getElementById("blitzStart");
const blitzResignBtn = document.getElementById("blitzResign");
const whiteClockEl = document.getElementById("whiteClock");
const blackClockEl = document.getElementById("blackClock");
const blitzStatusEl = document.getElementById("blitzStatus");

// ---- Blitz State ----
let blitzGame = new Chess();
let blitzBoard: any = null;
let blitzInProgress = false;
let blitzPlayerColor: "white" | "black" = "white";
let blitzSkill = 1;
let startTimeMs = 5 * 60 * 1000;
let whiteTimeMs = startTimeMs;
let blackTimeMs = startTimeMs;
let clockInterval: any = null;
// Count how many moves the engine has played in the current Blitz game
let engineMovesPlayed = 0;

// Minimum share of play to consider a move (2%)
const BLITZ_MIN_PLAY_RATE = 0.02;

// --- Helpers ---
function formatMs(ms: number) {
  ms = Math.max(0, ms);
  const totalSec = Math.floor(ms / 1000);
  const m = Math.floor(totalSec / 60)
    .toString()
    .padStart(2, "0");
  const s = (totalSec % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}
function updateClockUI() {
  if (whiteClockEl) whiteClockEl.textContent = formatMs(whiteTimeMs);
  if (blackClockEl) blackClockEl.textContent = formatMs(blackTimeMs);
}
function stopClocks() {
  if (clockInterval) clearInterval(clockInterval);
  clockInterval = null;
}
function startClocks() {
  stopClocks();
  clockInterval = setInterval(() => {
    if (!blitzInProgress) return;
    const turn = blitzGame.turn(); // 'w' or 'b'
    if (turn === "w") {
      whiteTimeMs -= 250;
      if (whiteTimeMs <= 0) {
        whiteTimeMs = 0;
        updateClockUI();
        endBlitz("Black wins on time.");
        return;
      }
    } else {
      blackTimeMs -= 250;
      if (blackTimeMs <= 0) {
        blackTimeMs = 0;
        updateClockUI();
        endBlitz("White wins on time.");
        return;
      }
    }
    updateClockUI();
  }, 250);
}
function setBlitzStatus(msg: string) {
  if (blitzStatusEl) blitzStatusEl.textContent = msg;
}

// Initialize blitz board once (when Blitz tab first opened)
function ensureBlitzBoard() {
  if (blitzBoard) return;
  const configBlitz = {
    PieceTheme: "img/chesspieces/wikipedia/{piece}.svg",
    draggable: true,
    position: "start",
    onDrop: onBlitzDrop,
    onDragStart: onBlitzDragStart,
  };
  blitzBoard = Chessboard2("blitzBoard", configBlitz);
}

function onBlitzDragStart(source: string, piece: string) {
  // Only allow dragging player's pieces when it's their turn and game is on
  if (!blitzInProgress) return false;
  const pieceIsWhite = piece.startsWith("w");
  const turnIsWhite = blitzGame.turn() === "w";
  const playerIsWhite = blitzPlayerColor === "white";
  if (turnIsWhite !== playerIsWhite) return false;
  if (playerIsWhite !== pieceIsWhite) return false;
  return true;
}

async function onBlitzDrop(event: any) {
  if (!blitzInProgress) return "snapback";

  // Reject moving when it's engine's turn
  const playerIsWhite = blitzPlayerColor === "white";
  if ((blitzGame.turn() === "w") !== playerIsWhite) return "snapback";

  let move;
  try {
    move = blitzGame.move({
      from: event.source,
      to: event.target,
      promotion: "q",
    });
  } catch {
    return "snapback";
  }
  if (!move) return "snapback";

  blitzBoard.position(blitzGame.fen());

  // Check for end of game after player's move
  if (handleEndIfOver()) return;

  // Engine turn
  await engineTurn();
}

function blitzFenParam(): string {
  return encodeURIComponent(btoa(blitzGame.fen()));
}

async function fetchBlitzMoves(skill: number): Promise<any[]> {
  const res = await fetch(`${API_URL}/fen/${blitzFenParam()}/${skill}/moves`);
  if (!res.ok) return [];
  return await res.json();
}

function pickBestBlitzMove(moves: any[], engineIsWhite: boolean): any | null {
  if (!moves || !moves.length) return null;

  // Compute total to derive play-rate
  const totalPlayed = moves.reduce(
    (sum: number, m: any) => sum + (m.move_times_played ?? 0),
    0,
  );

  // Only consider moves played at least 2% of the time.
  // If total is 0, keep all since we can’t compute ratios.
  const eligible =
    totalPlayed > 0
      ? moves.filter(
          (m: any) =>
            ((m.move_times_played ?? 0) / totalPlayed) >= BLITZ_MIN_PLAY_RATE,
        )
      : moves;

  if (!eligible.length) return null;

  const key = engineIsWhite ? "recursiveScoreWhite" : "recursiveScoreBlack";
  const score = (m: any) =>
    Number.isFinite(m?.[key]) ? Number(m[key]) : -Infinity;

  // Pick highest recursive score; tie-break by times played
  return eligible.reduce((best: any, m: any) => {
    if (best == null) return m;
    const sBest = score(best);
    const sM = score(m);
    if (sM > sBest) return m;
    if (sM === sBest) {
      const tbBest = best.move_times_played ?? 0;
      const tbM = m.move_times_played ?? 0;
      if (tbM > tbBest) return m;
    }
    return best;
  }, null);
}

// For the first two engine moves: pick the most common move by times played
function pickMostCommonBlitzMove(moves: any[]): any | null {
  if (!moves || !moves.length) return null;

  const totalPlayed = moves.reduce(
    (sum: number, m: any) => sum + (m.move_times_played ?? 0),
    0,
  );

  // Prefer moves with >= BLITZ_MIN_PLAY_RATE; if none, consider all
  const eligible =
    totalPlayed > 0
      ? moves.filter(
          (m: any) =>
            ((m.move_times_played ?? 0) / totalPlayed) >= BLITZ_MIN_PLAY_RATE,
        )
      : moves;

  const pool = eligible.length ? eligible : moves;

  return pool.reduce((best: any, m: any) => {
    if (best == null) return m;
    const a = best.move_times_played ?? 0;
    const b = m.move_times_played ?? 0;
    if (b > a) return m;
    return best;
  }, null);
}

async function engineTurn() {
  try {
    const engineIsWhite = blitzPlayerColor === "black";
    const moves = await fetchBlitzMoves(blitzSkill);

    // First two engine moves: play the most common move
    const best =
      engineMovesPlayed < 2
        ? pickMostCommonBlitzMove(moves)
        : pickBestBlitzMove(moves, engineIsWhite);

    if (!best) {
      endBlitz("No engine moves available (under 2% play rate).");
      return;
    }
    // Play SAN from API
    const engineMove = blitzGame.move(best.moveSAN);
    if (!engineMove) {
      setBlitzStatus("Engine provided illegal move.");
      endBlitz("Game stopped due to engine error.");
      return;
    }

    // Count this as an engine move only after it is successfully applied
    engineMovesPlayed++;

    blitzBoard.position(blitzGame.fen());
  } catch {
    setBlitzStatus("Failed to get engine move.");
    endBlitz("Game stopped due to engine error.");
    return;
  }

  handleEndIfOver();
}

function handleEndIfOver(): boolean {
  if (blitzGame.isGameOver()) {
    let msg = "Game over.";
    if (blitzGame.isCheckmate()) {
      msg = blitzGame.turn() === "w" ? "Black wins by checkmate." : "White wins by checkmate.";
    } else if (blitzGame.isDraw()) {
      msg = "Draw.";
    }
    endBlitz(msg);
    return true;
  }
  // Keep clocks running
  startClocks();
  setBlitzStatus(`${blitzGame.turn() === "w" ? "White" : "Black"} to move.`);
  return false;
}

function resetBlitzState() {
  blitzGame = new Chess();
  blitzBoard?.position(blitzGame.fen());
  whiteTimeMs = startTimeMs;
  blackTimeMs = startTimeMs;
  engineMovesPlayed = 0; // reset engine move counter at game start
  updateClockUI();
  setBlitzStatus("");
}

function endBlitz(reason: string) {
  blitzInProgress = false;
  stopClocks();
  setBlitzStatus(reason);
}

function startBlitzGame() {
  ensureBlitzBoard();

  // Read selections
  blitzPlayerColor = (blitzColorSel?.value as "white" | "black") || "white";
  blitzSkill = parseInt(blitzSkillSel?.value || "1", 10);
  startTimeMs = parseInt(blitzTimeSel?.value || `${5 * 60 * 1000}`, 10);
  whiteTimeMs = startTimeMs;
  blackTimeMs = startTimeMs;

  // Reset board/game
  resetBlitzState();
  blitzInProgress = true;

  // Set orientation
  try {
    // chessboard.js/2 supports orientation updates
    (blitzBoard as any)?.orientation?.(blitzPlayerColor);
  } catch {
    // ignore if not supported
  }
  blitzBoard.position(blitzGame.fen());
  updateClockUI();
  setBlitzStatus(`${blitzPlayerColor === "white" ? "White" : "Black"} to move.`);

  // If engine is White, let it move first
  if (blitzPlayerColor === "black") {
    startClocks();
    engineTurn();
  } else {
    startClocks();
  }
}

// Wire up Blitz controls
blitzStartBtn?.addEventListener("click", () => {
  startBlitzGame();
});
blitzResignBtn?.addEventListener("click", () => {
  if (!blitzInProgress) return;
  const winner = blitzPlayerColor === "white" ? "Black" : "White";
  endBlitz(`${winner} wins by resignation.`);
});

// Initialize clocks UI if Blitz tab exists
if (blitzView) {
  updateClockUI();
}

// Optional: default to Explorer view
showExplorer();
