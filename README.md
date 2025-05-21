<div style="position: relative; width: 200px; height: 200px;">
  <img src="data/wichtigesbild.png" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);" />
  <img src="data/oof.jpg" style="
    position: absolute;
    top: 0;
    left: 50%;
    width: 50px;
    transform: translateX(-50%);
    animation: orbit 4s linear infinite;
  " />
</div>

<style>
@keyframes orbit {
  from { transform: rotate(0deg) translateX(100px) rotate(0deg); }
  to { transform: rotate(360deg) translateX(100px) rotate(-360deg); }
}
</style>

<!-- <img src="data/wichtigesbild.png" alt="Schmetterlings" width="600"/> -->