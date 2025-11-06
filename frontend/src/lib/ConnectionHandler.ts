import AWN from "awesome-notifications";
import { gameboard, moveHistory, shownScreen } from "./stores/GameStore";

export default class ConnectionHandler {
  private static instance: ConnectionHandler;
  private socket: WebSocket;
  private algorithms: string[] = [];
  private algorithmsReadyResolve: ((algorithms: string[]) => void) | null =
    null;
  private algorithmsReadyPromise: Promise<string[]> | null = null;

  private constructor() {
    const wsUrl = import.meta.env.WEBSOCKET_URL || "ws://localhost:8000";

    this.socket = new WebSocket(wsUrl);

    this.socket.onopen = () => {
      console.log(`WebSocket connection established: ${wsUrl}`);
    };

    this.socket.onmessage = this.onMessage.bind(this);

    this.socket.onerror = (event) => {
      new AWN().alert("WebSocket error occurred.", {
        position: "bottom-right",
      });
      console.error("WebSocket error:", event);
    };

    this.socket.onclose = (event) => {
      if (!event.wasClean) {
        new AWN().alert(`WebSocket closed unexpectedly: ${event.reason}`, {
          position: "bottom-right",
        });
        console.warn("WebSocket closed unexpectedly:", event);
      } else {
        console.log("WebSocket connection closed cleanly.");
      }
    };

    window.addEventListener("beforeunload", () => {
      if (this.socket.readyState === WebSocket.OPEN) {
        console.log("Closing WebSocket connection.");
        this.socket.close();
      }
    });

    // Initialize the promise that resolves when algorithms are available
    this.initAlgorithmsPromise();
  }

  public static getInstance(): ConnectionHandler {
    if (!ConnectionHandler.instance) {
      ConnectionHandler.instance = new ConnectionHandler();
    }
    return ConnectionHandler.instance;
  }

  private initAlgorithmsPromise(): void {
    this.algorithmsReadyPromise = new Promise<string[]>((resolve) => {
      this.algorithmsReadyResolve = resolve;

      if (this.algorithms.length > 0) {
        resolve(this.algorithms);
      }
    });
  }

  public getAlgorithms(): Promise<string[]> {
    return this.algorithmsReadyPromise!;
  }

  public startGame(algorithm: string, difficulty: number): void {
    if (this.socket.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify({ algorithm, difficulty }));
    } else {
      new AWN().alert("Cannot start game: WebSocket connection is not open.", {
        position: "bottom-right",
      });
      console.error(
        "WebSocket is not open. ReadyState:",
        this.socket.readyState
      );
    }
  }

  private showEndScreen(winner: number): void {
    if (winner === 0) {
      shownScreen.set("draw");
    } else if (winner === 1) {
      shownScreen.set("winner");
    } else {
      shownScreen.set("looser");
    }
  }

  private onMessage(event: MessageEvent): void {
    try {
      const data = JSON.parse(event.data);

      if (data.error) {
        new AWN().alert(data.error, { position: "bottom-right" });
        return;
      }

      switch (data.status) {
        case "connection_established":
          this.algorithms = data.algorithms;
          if (this.algorithmsReadyResolve) {
            this.algorithmsReadyResolve(this.algorithms);
          }
          break;

        case "human_move":
          gameboard.set(JSON.parse(data.board));
          moveHistory.update((history) => [
            { player: 1, column: data.position },
            ...history,
          ]);
          break;

        case "computer_move":
          gameboard.set(JSON.parse(data.board));
          moveHistory.update((history) => [
            { player: 2, column: data.position },
            ...history,
          ]);
          break;

        case "end":
          gameboard.set(JSON.parse(data.board));
          this.showEndScreen(data.winner);
          break;

        default:
          console.warn("Received unknown status from server:", data.status);
      }
    } catch (error) {
      new AWN().alert("Received malformed data from server.", {
        position: "bottom-right",
      });
      console.error("Malformed data:", event.data);
    }
  }
}
