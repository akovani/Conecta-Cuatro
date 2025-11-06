<script lang="ts">
  import { onMount } from "svelte";

  // Props to allow navigation back to the game
  let { returnToGame } = $props();

  // State for tutorial navigation
  let currentSection = $state(0);
  const totalSections = 5;

  // Tutorial content sections
  const tutorialSections = [
    {
      title: "Game Objective",
      content:
        "Connect Four of your marks in a row - vertically, horizontally, or diagonally - before the computer does. Play on a whiteboard where you draw your moves and the system automatically draws its responses.",
      icon: "fa-solid fa-bullseye",
    },
    {
      title: "Getting Started",
      content:
        "Select your difficulty level (1-3) using the control panel. Draw your X mark in any column of the grid. The camera will detect your move, and the system will draw an O mark for the computer's turn.",
      icon: "fa-solid fa-play",
    },
    {
      title: "Making Moves",
      content:
        "Simply draw your mark in your chosen column on the whiteboard grid. The camera will register your move, and the system will then draw the computer's move directly on the board. Take turns until someone wins or the grid fills up. Keep in mind that you are only allowed to draw on top of the existing marks, simulating gameplay on a real board where disks fall to the lowest available position in the column.",
      icon: "fas fa-pencil-alt",
    },
    {
      title: "Difficulty Levels",
      content:
        "Level 1: Perfect for beginners or casual play. Level 2: Provides a moderate challenge with some strategic play. Level 3: Highly competitive, plans several moves ahead. Each level increases how far ahead the computer looks when planning its strategy.",
      icon: "fas fa-trophy",
    },
    {
      title: "Advanced Options",
      content:
        "For experienced players: Choose between three algorithms for different playing styles. Minimax offers perfect play through exhaustive evaluation. Monte Carlo Tree Search provides more varied gameplay. Our Custom Model plays based on patterns from thousands of real games. Remember to clean the whiteboard after your game!",
      icon: "fas fa-cogs",
    },
  ];

  // Navigation functions
  function nextSection() {
    if (currentSection < totalSections - 1) {
      currentSection++;
    }
  }

  function prevSection() {
    if (currentSection > 0) {
      currentSection--;
    }
  }

  // Keyboard navigation
  function handleKeydown(event: { key: string }) {
    if (event.key === "ArrowRight") {
      nextSection();
    } else if (event.key === "ArrowLeft") {
      prevSection();
    }
  }

  onMount(() => {
    window.addEventListener("keydown", handleKeydown);
    return () => {
      window.removeEventListener("keydown", handleKeydown);
    };
  });
</script>

<div class="fixed inset-0 flex items-center justify-center bg-gray-900 z-50">
  <!-- Background pattern -->
  <div class="absolute inset-0 opacity-10">
    <div
      class="absolute inset-0 bg-[radial-gradient(#ffffff_1px,transparent_1px)] bg-[size:20px_20px]"
    ></div>
  </div>

  <!-- Decorative elements -->
  <div
    class="absolute top-0 left-0 w-full h-full overflow-hidden pointer-events-none"
  >
    <div
      class="absolute top-1/4 left-1/4 w-64 h-64 bg-gray-700 rounded-full opacity-20 blur-3xl"
    ></div>
    <div
      class="absolute bottom-1/3 right-1/4 w-64 h-64 bg-gray-600 rounded-full opacity-20 blur-3xl"
    ></div>
  </div>

  <!-- Return to game button -->
  <button
    class="absolute top-4 left-4 z-20 flex items-center justify-center px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 transition-colors duration-200"
    onclick={returnToGame}
  >
    <svg
      class="mr-2"
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M19 12H5M12 19l-7-7 7-7" />
    </svg>
    Back to Game
  </button>

  <div
    class="z-10 flex flex-col items-center gap-6 p-8 md:p-16 rounded-2xl bg-gray-900 shadow-2xl border border-gray-800 w-full max-w-4xl mx-4"
  >
    <h2 class="text-4xl md:text-5xl font-extrabold text-white mb-2">
      Game Tutorial
    </h2>

    <!-- Progress indicator -->
    <div class="flex space-x-2 mb-4">
      {#each Array(totalSections) as _, i}
        <div
          class="w-3 h-3 rounded-full transition-colors duration-300 {i ===
          currentSection
            ? 'bg-white'
            : 'bg-gray-600'}"
        ></div>
      {/each}
    </div>

    <!-- Tutorial content -->
    <div class="w-full transition-opacity duration-300">
      <div class="flex flex-col md:flex-row gap-8 items-center">
        <div class="md:w-1/2">
          <h3 class="text-2xl font-bold text-white mb-4">
            {tutorialSections[currentSection].title}
          </h3>
          <p class="text-gray-300 text-lg leading-relaxed">
            {tutorialSections[currentSection].content}
          </p>
        </div>
        <div class="md:w-1/2 flex justify-center">
          <i 
            class={tutorialSections[currentSection].icon + " text-9xl text-white"}
            aria-hidden="true"
          ></i>
        </div>
      </div>
    </div>

    <!-- Navigation buttons -->
    <div class="flex justify-between w-full mt-8">
      <button
        class="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        onclick={prevSection}
        disabled={currentSection === 0}
      >
        Previous
      </button>

      <div class="text-gray-400">
        {currentSection + 1} of {totalSections}
      </div>

      <button
        class="px-4 py-2 rounded-lg bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        onclick={nextSection}
        disabled={currentSection === totalSections - 1}
      >
        Next
      </button>
    </div>

    <!-- Skip to end button -->
    {#if currentSection < totalSections - 1}
      <button
        class="text-gray-400 hover:text-white text-sm mt-2 transition-colors duration-200"
        onclick={() => (currentSection = totalSections - 1)}
      >
        Skip to end
      </button>
    {/if}

    <!-- Return to game button (bottom) -->
    {#if currentSection === totalSections - 1}
      <button
        class="mt-4 px-6 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-medium transition-all duration-200 transform"
        onclick={returnToGame}
      >
        Start Playing
      </button>
    {/if}
  </div>
</div>
