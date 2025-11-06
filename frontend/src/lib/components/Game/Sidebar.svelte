<script lang="ts">
  import { moveHistory } from "$lib/stores/GameStore";
</script>

<div
  class="w-full lg:w-96 bg-gray-800 p-6 rounded-2xl shadow-2xl border border-gray-700 m-4 ml-4"
>
  <div class="mb-6">
    <h3 class="text-xl font-semibold mb-2 text-center">Current Player</h3>
    {#if $moveHistory.length % 2 === 0}
      <div class="flex items-center justify-center">
        <div
          class="w-12 h-12 md:w-16 md:h-16 lg:w-20 lg:h-20 xl:w-24 xl:h-24 rounded-full bg-gray-700 flex items-center justify-center"
        >
          <div
            class="w-10 h-10 md:w-14 md:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20 rounded-full bg-blue-500"
          ></div>
        </div>
      </div>
    {:else}
      <div class="flex items-center justify-center">
        <div
          class="w-12 h-12 md:w-16 md:h-16 lg:w-20 lg:h-20 xl:w-24 xl:h-24 rounded-full bg-gray-700 flex items-center justify-center"
        >
          <div
            class="w-10 h-10 md:w-14 md:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20 rounded-full bg-red-500"
          ></div>
        </div>
      </div>
    {/if}
  </div>

  <button
    class="w-full bg-blue-500 text-white py-3 px-6 rounded-lg mb-6 hover:bg-blue-600 transition-colors text-lg font-semibold"
    onclick={() => {
      window.location.reload();
    }}
  >
    New Game
  </button>

  <div>
    <div class="flex justify-between items-center mb-3">
      <h3 class="text-xl font-semibold">Move History</h3>
      <span class="text-sm text-gray-400 italic">Newest at top</span>
    </div>
    <div class="h-96 overflow-hidden relative">
      <div class="absolute inset-0 space-y-2 fade-mask">
        {#each $moveHistory as move}
          {#if move.player === 1}
            <!-- Player move - aligned to the right -->
            <div class="bg-blue-600 p-2 rounded-lg ml-auto max-w-3/4">
              <div class="flex items-center justify-between">
                <div class="text-lg font-semibold">
                  You
                </div>
              </div>
              <div class="text-sm text-gray-200">Column: {move.column}</div>
            </div>
          {:else}
            <!-- Computer move - aligned to the left -->
            <div class="bg-gray-700 p-2 rounded-lg mr-auto max-w-3/4">
              <div class="flex items-center justify-between">
                <div class="text-lg font-semibold">
                  Computer
                </div>
              </div>
              <div class="text-sm text-gray-400">Column: {move.column}</div>
            </div>
          {/if}
        {/each}
      </div>
    </div>
  </div>
</div>

<style>
  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.1);
    }
    100% {
      transform: scale(1);
    }
  }
  
  .max-w-3\/4 {
    max-width: 75%;
  }
  
  .fade-mask {
    mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 1) 70%, rgba(0, 0, 0, 0));
    -webkit-mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 1) 70%, rgba(0, 0, 0, 0));
    overflow-y: hidden;
  }
</style>