<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand-zone">
        <RouterLink to="/biblioteca" class="brand-link">Archivo de Brumas</RouterLink>
        <p class="brand-note">Museo interactivo de biblioteca y cuentos</p>
      </div>
      <RouterLink to="/biblioteca" class="top-link">Biblioteca</RouterLink>
    </header>

    <main class="main-stage">
      <RouterView />
    </main>
  </div>
</template>
