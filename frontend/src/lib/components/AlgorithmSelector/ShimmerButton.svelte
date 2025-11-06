<script lang="ts">
  let { handleClick, buttonText } = $props();
</script>

<button 
  onclick={() => handleClick(buttonText)}
  class="relative inline-block py-3 px-6 border-none rounded-lg text-white bg-black cursor-pointer overflow-hidden font-medium text-xl transition-transform duration-200 ease-in-out hover:-translate-y-1 active:translate-y-1"
>
  {buttonText}
  <div class="shimmer-effect absolute top-0 left-[-150%] w-1/2 h-full bg-gradient-to-r from-transparent via-white/25 to-transparent skew-x-[-20deg]"></div>
</button>

<style>
  .shimmer-effect {
    animation: shimmer 3s infinite;
  }
  
  @keyframes shimmer {
    0% {
      left: -150%;
    }
    50%, 100% {
      left: 150%;
    }
  }
</style>