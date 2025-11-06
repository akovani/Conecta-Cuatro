<script lang="ts">
  import GameBoard from "$lib/components/Game/GameBoard.svelte";
  import Sidebar from "$lib/components/Game/Sidebar.svelte";
  import ConnectionHandler from "$lib/ConnectionHandler";
  import { onMount } from "svelte";

  let { algorithm, difficulty } = $props();

  // Start the game using the algorithm provided in the URL query parameter.
  onMount(() => {
    ConnectionHandler.getInstance().startGame(algorithm, difficulty);
  });
</script>

<!-- Outer container with matching background and decorative elements -->
<div class="fixed inset-0 bg-gray-900">
  <!-- Background pattern -->
  <div class="absolute inset-0 opacity-10">
    <div
      class="absolute inset-0 bg-[radial-gradient(#ffffff_1px,transparent_1px)] bg-[size:20px_20px]"
    ></div>
  </div>
  <!-- Decorative blurred circles -->
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

  <!-- Main game content -->
  <div class="relative z-10 flex flex-col lg:flex-row h-screen text-white">
    <Sidebar />
    <GameBoard />
  </div>
</div>
