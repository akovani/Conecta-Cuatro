<script lang="ts">
  // Import necessary modules
  import ShimmerButton from "$lib/components/AlgorithmSelector/ShimmerButton.svelte";
  import ConnectionHandler from "$lib/ConnectionHandler";

  let { selectAlgorithm } = $props();

  let selectedDifficulty = $state(1);
  let selectedAlgorithm = $state("");
  let showAdvanced = $state(false);

  let algorithmsPromise = getAlgorithms();

  /**
   * Get all the algorithms from the backend
   * @returns The list of algorithms
   */
  async function getAlgorithms() {
    const algorithms = await ConnectionHandler.getInstance().getAlgorithms();
    
    // Set the default algorithm to the first one
    if (selectedAlgorithm === "") {
      selectedAlgorithm = algorithms[0];
    }

    return algorithms;
  }

  function toggleAdvanced() {
    showAdvanced = !showAdvanced;
  }

  function handleAlgorithmSelect(algorithm: string) {
    selectedAlgorithm = algorithm;
  }

  function startGame() {
    // Use the default algorithm if none selected
    selectAlgorithm(selectedAlgorithm, selectedDifficulty);
  }
</script>

<div
  class="fixed inset-0 flex items-center justify-center bg-gray-900 z-10 min-w-screen h-screen"
>
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

  <div
    class="z-10 flex flex-col items-center gap-8 text-center p-12 md:p-16 rounded-2xl bg-gray-900 shadow-2xl border border-gray-800 max-w-4xl w-full"
  >
    {#await algorithmsPromise}
      <div class="text-5xl font-extrabold text-white">Loading...</div>
    {:then algorithms}
      <div class="flex flex-col items-center gap-4 w-full">
        <h2 class="text-4xl md:text-5xl font-extrabold text-white">
          Game Settings
        </h2>

        <!-- Difficulty range input 1-3 -->
        <div class="w-3/4 px-4 py-8">
          <h3 class="text-2xl font-bold text-white mb-4">Difficulty Level</h3>
          <input
            type="range"
            min="1"
            max="3"
            step="1"
            class="w-full accent-blue-500"
            bind:value={selectedDifficulty}
          />
          <!-- Labels -->
          <div class="flex justify-between text-lg text-white mt-2">
            <span>Easy</span>
            <span>Medium</span>
            <span>Hard</span>
          </div>
        </div>

        <!-- Algorithm selection with toggle -->
        <div class="w-3/4 px-4 mb-4">
          <button
            onclick={toggleAdvanced}
            class="w-full text-left text-2xl font-bold text-white pb-1 flex items-center justify-between"
          >
            <span>Algorithm Selection (Advanced)</span>
            <span
              class="transition-transform {showAdvanced ? 'rotate-180' : ''}"
              >▼</span
            >
          </button>

          <!-- Algorithm buttons -->
          <div
            class="transition-all duration-300 {showAdvanced
              ? 'opacity-100 max-h-40 mt-6'
              : 'opacity-0 max-h-0 mt-0 overflow-hidden'}"
          >
            <div class="flex flex-wrap justify-center gap-6 w-full">
              {#each algorithms as algorithm}
                <button
                  onclick={() => handleAlgorithmSelect(algorithm)}
                  class="relative px-6 py-3 rounded-lg font-medium transition-all duration-200 overflow-hidden group
                       {selectedAlgorithm === algorithm
                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'}"
                >
                  {#if selectedAlgorithm === algorithm}
                    <div
                      class="absolute inset-0 bg-blue-400 opacity-20 animate-pulse"
                    ></div>
                  {/if}
                  <div class="relative z-10">
                    {algorithm}
                  </div>
                </button>
              {/each}
            </div>
          </div>
        </div>

        <!-- Start Game Button -->
        <button
          onclick={startGame}
          class="mt-6 bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-12 rounded-full shadow-lg transition duration-200 text-xl animate-pulse shadow-green-500/30"
        >
          Start Game
        </button>
      </div>
    {/await}
  </div>
</div>
