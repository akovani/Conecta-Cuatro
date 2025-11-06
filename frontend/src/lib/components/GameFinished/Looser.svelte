<script lang="ts">
    import { onMount, onDestroy } from "svelte";
  
    // Rain drop settings
    let animationInterval: number | undefined;
    let raindrops: Raindrop[] = [];
  
    // Raindrop class for falling elements
    class Raindrop {
      x: number;
      y: number;
      length: number;
      opacity: number;
      speed: number;
  
      constructor() {
        this.x = Math.random() * 100;
        this.y = -20;
        this.length = Math.random() * 15 + 10;
        this.opacity = Math.random() * 0.4 + 0.1;
        this.speed = Math.random() * 2 + 1;
      }
  
      update(): boolean {
        this.y += this.speed;
        return this.y < 120;
      }
    }
  
    // Props (optional)
    let message: string = "YOU LOST";
    let subMessage: string = "Better luck next time...";
    let buttonText: string = "Try Again";
  
    // Create animation
    function startAnimation(): void {
      animationInterval = window.setInterval(() => {
        // Add new raindrops
        for (let i = 0; i < 3; i++) {
          raindrops = [...raindrops, new Raindrop()];
        }
  
        // Update existing raindrops
        raindrops = raindrops.filter((drop) => drop.update());
      }, 100);
    }
  
    onMount(() => {
      startAnimation();
    });
  
    onDestroy(() => {
      if (animationInterval) window.clearInterval(animationInterval);
    });
  </script>
  
  <div
    class="relative flex flex-col items-center justify-center min-h-screen bg-gradient-to-b from-gray-800 to-gray-900 overflow-hidden"
  >
    <!-- Rain container -->
    <div class="absolute inset-0 pointer-events-none">
      {#each raindrops as drop}
        <div
          class="absolute w-px rounded-none"
          style="
                left: {drop.x}%;
                top: {drop.y}%;
                height: {drop.length}px;
                background-color: rgba(150, 150, 210, {drop.opacity});
                box-shadow: 0 0 2px rgba(150, 150, 210, {drop.opacity});
              "
        ></div>
      {/each}
    </div>
  
    <!-- Clouds -->
    <div class="absolute top-0 w-full h-20 bg-gray-700 opacity-40 blur-md"></div>
  
    <!-- Lightning flash - occasional random flash -->
    <div
      class="absolute inset-0 bg-blue-100 opacity-0 pointer-events-none animate-[flash_8s_ease-in-out_infinite]"
    ></div>
  
    <!-- Loser content -->
    <div class="z-50 text-center transform">
      <div
        class="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-gray-300 via-gray-400 to-gray-300 mb-6 tracking-wider"
      >
        {message}
      </div>
  
      <div
        class="bg-black bg-opacity-30 backdrop-filter backdrop-blur-sm p-8 rounded-xl shadow-xl mb-8 transform transition-transform border border-gray-700"
      >
        <div class="text-2xl text-gray-300 font-bold mb-4">Game Over</div>
        <div class="text-gray-400 text-lg">{subMessage}</div>
      </div>
  
      <button
        class="bg-gray-600 hover:bg-gray-500 text-white font-bold py-3 px-8 rounded-full transform transition-transform hover:scale-110 shadow-lg"
        onclick={() => (window.location.reload())}
      >
        {buttonText}
      </button>
    </div>
  
    <!-- Puddle at bottom -->
    <div
      class="absolute bottom-0 w-full h-8 bg-gradient-to-t from-gray-600 to-transparent opacity-30"
    ></div>
  </div>
  
  <style>
    @keyframes flash {
      0%,
      95%,
      98% {
        opacity: 0;
      }
      96%,
      97% {
        opacity: 0.1;
      }
    }
  </style>
  