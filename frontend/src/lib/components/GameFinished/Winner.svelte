<script lang="ts">
    import { onMount, onDestroy } from "svelte";
  
    // Confetti settings
    const colors: string[] = [
      "#ff0000",
      "#00ff00",
      "#0000ff",
      "#ffff00",
      "#ff00ff",
      "#00ffff",
    ];
    let confettiInterval: number | undefined;
    let confetti: ConfettiPiece[] = [];
  
    // Confetti piece class
    class ConfettiPiece {
      x: number;
      y: number;
      size: number;
      color: string;
      speed: number;
      angle: number;
      rotation: number;
      opacity: number;
  
      constructor() {
        this.x = Math.random() * 100;
        this.y = -10;
        this.size = Math.random() * 5 + 5;
        this.color = colors[Math.floor(Math.random() * colors.length)];
        this.speed = Math.random() * 2 + 1;
        this.angle = Math.random() * 360;
        this.rotation = Math.random() * 5 - 2.5;
        this.opacity = 1;
      }
  
      update(): boolean {
        this.y += this.speed;
        this.x += Math.sin((this.angle * Math.PI) / 180) * 0.5;
        this.angle += this.rotation;
        this.opacity -= 0.005;
        return this.y < 110 && this.opacity > 0;
      }
    }
  
    // Props (optional)
    let message: string = "YOU WON!";
    let subMessage: string = "You've achieved an amazing victory!";
    let buttonText: string = "Start a new game";
  
    // Create confetti animation
    function startConfetti(): void {
      confettiInterval = window.setInterval(() => {
        // Add new confetti pieces
        for (let i = 0; i < 4; i++) {
          confetti = [...confetti, new ConfettiPiece()];
        }
  
        // Update existing pieces
        confetti = confetti.filter((piece) => piece.update());
      }, 50);
    }
  
    onMount(() => {
      startConfetti();
    });
  
    onDestroy(() => {
      if (confettiInterval) window.clearInterval(confettiInterval);
    });
  </script>
  
  <div
    class="relative flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-indigo-800 to-purple-900 overflow-hidden"
  >
    <!-- Confetti container -->
    <div class="absolute inset-0 pointer-events-none">
      {#each confetti as piece}
        <div
          class="absolute rounded-sm"
          style="
              left: {piece.x}%;
              top: {piece.y}%;
              width: {piece.size}px;
              height: {piece.size}px;
              background-color: {piece.color};
              transform: rotate({piece.angle}deg);
              opacity: {piece.opacity};
            "
        ></div>
      {/each}
    </div>
  
    <!-- Decorative elements -->
    <div class="absolute top-0 left-0 w-full h-full">
      <div
        class="absolute top-1/4 left-1/4 w-32 h-32 bg-yellow-500 rounded-full opacity-20 blur-3xl"
      ></div>
      <div
        class="absolute bottom-1/3 right-1/4 w-40 h-40 bg-purple-500 rounded-full opacity-20 blur-3xl"
      ></div>
    </div>
  
    <!-- Winner content - now with z-50 to ensure it's in front of everything -->
    <div class="z-50 text-center transform scale-in">
      <div
        class="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-500 mb-6 tracking-wider"
      >
        {message}
      </div>
  
      <div
        class="bg-white bg-opacity-20 backdrop-filter backdrop-blur-sm p-8 rounded-xl shadow-2xl mb-8 transform transition-transform"
      >
        <div class="text-2xl text-white font-bold mb-4">Congratulations!</div>
        <div class="text-white text-lg">{subMessage}</div>
      </div>
  
      <button
        class="bg-yellow-500 hover:bg-yellow-400 text-black font-bold py-3 px-8 rounded-full transform transition-transform hover:scale-110 shadow-lg"
        onclick="{() => window.location.reload()}"
      >
        {buttonText}
      </button>
    </div>
  </div>
  