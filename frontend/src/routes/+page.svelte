<script lang="ts">
  import AlgorithmSelector from "$lib/components/AlgorithmSelector/AlgorithmSelector.svelte";
  import Game from "$lib/components/Game/Game.svelte";
  import Draw from "$lib/components/GameFinished/Draw.svelte";
  import Looser from "$lib/components/GameFinished/Looser.svelte";
  import Winner from "$lib/components/GameFinished/Winner.svelte";
  import Tutorial from "$lib/components/Tutorial.svelte";
  import { shownScreen } from "$lib/stores/GameStore";

  let algorithm = $state("");
  let difficulty = $state(1);
  let showTutorial = $state(false);

  function selectAlgorithm(selectedAlgorithm: string, difficulty: number) {
    shownScreen.set("game");
    algorithm = selectedAlgorithm;
    difficulty = difficulty;
  }
</script>

{#if showTutorial}
  <div
    class="fixed inset-0 bg-gray-900 bg-opacity-90 z-50 flex items-center justify-center"
  >
    <Tutorial returnToGame={() => (showTutorial = false)} />
  </div>
{/if}

{#if $shownScreen === "select_algorithm"}
  <AlgorithmSelector {selectAlgorithm} />
{:else if $shownScreen === "game"}
  <Game {algorithm} {difficulty} />
{:else if $shownScreen === "winner"}
  <Winner />
{:else if $shownScreen === "looser"}
  <Looser />
{:else if $shownScreen === "draw"}
  <Draw />
{/if}

<!-- Help button -->
<button
  class="absolute top-4 right-4 z-50 flex items-center justify-center w-10 h-10 rounded-full bg-gray-800 hover:bg-gray-700 text-white border border-gray-700 transition-colors duration-200"
  aria-label="Help"
  onclick={() => (showTutorial = true)}
>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    width="24"
    height="24"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="2"
    stroke-linecap="round"
    stroke-linejoin="round"
  >
    <circle cx="12" cy="12" r="10"></circle>
    <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path>
    <line x1="12" y1="17" x2="12.01" y2="17"></line>
  </svg>
</button>
