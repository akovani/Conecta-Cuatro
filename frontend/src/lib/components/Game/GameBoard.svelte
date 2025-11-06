<script lang="ts">
  import { gameboard } from "$lib/stores/GameStore";
  import { fly } from "svelte/transition";
</script>

<div class="flex-1 flex items-center justify-center p-4 w-full h-full">
  <div class="bg-blue-600 p-2 sm:p-3 md:p-4 rounded-xl sm:rounded-2xl shadow-2xl max-w-full">
    <div class="grid grid-cols-7 gap-1 sm:gap-2">
      {#each $gameboard as row, rowIndex}
        {#each row as cell, cellIndex}
          <div 
            class="w-12 h-12 md:w-16 md:h-16 lg:w-20 lg:h-20 xl:w-24 xl:h-24 rounded-full bg-gray-700 flex items-center justify-center"
          >
            {#if cell === 1}
              <!-- Yellow disc for Player 1 -->
              <div in:fly={{ y: -200, duration: 500 }} class="w-10 h-10 md:w-14 md:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20 rounded-full bg-blue-500"></div>
            {:else if cell === 2}
              <!-- Red disc for Player 2 -->
              <div in:fly={{ y: -200, duration: 500 }} class="w-10 h-10 md:w-14 md:h-14 lg:w-16 lg:h-16 xl:w-20 xl:h-20 rounded-full bg-red-500"></div>
            {/if}
          </div>
        {/each}
      {/each}
    </div>
  </div>
</div>
