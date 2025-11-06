import { writable } from "svelte/store";

let gameboard = writable([
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
  [0, 0, 0, 0, 0, 0, 0],
] as number[][]);

let moveHistory = writable([] as { player: number; column: number }[]);

let shownScreen = writable("select_algorithm" as "select_algorithm" | "game" | "winner" | "looser" | "draw");

export { gameboard, moveHistory, shownScreen };