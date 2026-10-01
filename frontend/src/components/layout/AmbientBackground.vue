<template>
  <!-- Decorative only: warm light drifting behind the page, plus film grain. -->
  <div class="ambient" aria-hidden="true">
    <div class="glow glow-a"></div>
    <div class="glow glow-b"></div>
    <div class="grain"></div>
  </div>
</template>

<style scoped>
.ambient {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;
  background: #0e0c0a;
}

.glow {
  position: absolute;
  width: 70vmax;
  height: 70vmax;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.35;
  will-change: transform;
}

.glow-a {
  top: -30vmax;
  right: -20vmax;
  background: radial-gradient(circle, rgba(230, 161, 90, 0.55), transparent 65%);
  animation: drift-a 26s ease-in-out infinite alternate;
}

.glow-b {
  bottom: -35vmax;
  left: -25vmax;
  background: radial-gradient(circle, rgba(210, 96, 63, 0.35), transparent 65%);
  animation: drift-b 32s ease-in-out infinite alternate;
}

.grain {
  position: absolute;
  inset: -50%;
  opacity: 0.06;
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='160' height='160'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/></filter><rect width='100%' height='100%' filter='url(%23n)'/></svg>");
}

@keyframes drift-a {
  to { transform: translate(-12vmax, 10vmax) scale(1.1); }
}

@keyframes drift-b {
  to { transform: translate(10vmax, -8vmax) scale(1.15); }
}

@media (prefers-reduced-motion: reduce) {
  .glow { animation: none; }
}
</style>
