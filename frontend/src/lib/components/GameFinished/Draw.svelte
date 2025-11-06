<script lang="ts">
  import { onMount, onDestroy } from "svelte";

  // Particle settings
  let animationInterval: number | undefined;
  let particles: Particle[] = [];

  // Particle class for floating elements
  class Particle {
    x: number;
    y: number;
    size: number;
    opacity: number;
    speed: number;
    direction: number;
    rotation: number;
    rotationSpeed: number;
    color: string;

    constructor() {
      this.x = Math.random() * 100;
      this.y = Math.random() * 100;
      this.size = Math.random() * 10 + 5;
      this.opacity = Math.random() * 0.6 + 0.2;
      this.speed = Math.random() * 0.5 + 0.2;
      this.direction = Math.random() * Math.PI * 2;
      this.rotation = Math.random() * 360;
      this.rotationSpeed = (Math.random() - 0.5) * 2;

      // Gold and purple color scheme for draw
      const colors = [
        "rgba(218, 165, 32, 0.8)", // Gold
        "rgba(147, 112, 219, 0.8)", // Purple
        "rgba(255, 215, 0, 0.8)", // Brighter gold
        "rgba(128, 0, 128, 0.8)", // Deeper purple
      ];
      this.color = colors[Math.floor(Math.random() * colors.length)];
    }

    update(): boolean {
      // Move in the current direction
      this.x += Math.cos(this.direction) * this.speed;
      this.y += Math.sin(this.direction) * this.speed;
      this.rotation += this.rotationSpeed;

      // Bounce off edges
      if (this.x < 0 || this.x > 100) {
        this.direction = Math.PI - this.direction;
      }
      if (this.y < 0 || this.y > 100) {
        this.direction = -this.direction;
      }

      // Keep particles alive
      return true;
    }
  }

  // Props (optional)
  export let message: string = "IT'S A DRAW";
  export let subMessage: string = "Both sides played well!";
  export let buttonText: string = "Play Again";

  // Create animation
  function startAnimation(): void {
    // Initialize with particles
    for (let i = 0; i < 40; i++) {
      particles = [...particles, new Particle()];
    }

    animationInterval = window.setInterval(() => {
      // Add new particles occasionally
      if (Math.random() > 0.7) {
        particles = [...particles, new Particle()];
      }

      // Update existing particles
      particles = particles.filter((particle) => particle.update());

      // Limit total particles
      if (particles.length > 60) {
        particles = particles.slice(0, 60);
      }
    }, 50);
  }

  onMount(() => {
    startAnimation();
  });

  onDestroy(() => {
    if (animationInterval) window.clearInterval(animationInterval);
  });
</script>

<div
  class="relative flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-purple-900 via-gray-800 to-amber-900 overflow-hidden"
>
  <!-- Particles container -->
  <div class="absolute inset-0 pointer-events-none">
    {#each particles as particle}
      <div
        class="absolute rounded-full"
        style="
            left: {particle.x}%;
            top: {particle.y}%;
            width: {particle.size}px;
            height: {particle.size}px;
            background-color: {particle.color};
            opacity: {particle.opacity};
            transform: rotate({particle.rotation}deg);
            box-shadow: 0 0 5px {particle.color};
          "
      ></div>
    {/each}
  </div>

  <!-- Draw content -->
  <div class="z-50 text-center transform">
    <div
      class="text-6xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-amber-300 via-purple-300 to-amber-300 mb-6 tracking-wider"
    >
      {message}
    </div>

    <div
      class="bg-gray-800 bg-opacity-50 backdrop-filter backdrop-blur-sm p-8 rounded-xl shadow-xl mb-8 transform transition-transform border border-purple-500 border-opacity-30"
    >
      <div class="text-2xl text-amber-200 font-bold mb-4">Game Tied</div>
      <div class="text-gray-200 text-lg">{subMessage}</div>
    </div>

    <button
      class="bg-gradient-to-r from-purple-600 to-amber-600 hover:from-purple-500 hover:to-amber-500 text-white font-bold py-3 px-8 rounded-full transform transition-transform hover:scale-110 shadow-lg"
      onclick={() => (window.location.reload())}
    >
      {buttonText}
    </button>
  </div>

  <!-- Balanced glow at bottom -->
  <div class="absolute bottom-0 w-full h-24 flex justify-center">
    <div
      class="w-1/3 h-full bg-purple-500 opacity-20 blur-xl rounded-full"
    ></div>
    <div
      class="w-1/3 h-full bg-amber-500 opacity-20 blur-xl rounded-full"
    ></div>
  </div>
</div>
