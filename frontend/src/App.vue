<template>
  <div id="app">
    <header>
      <h1>ペット健康免許証生成サービス</h1>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>

<style scoped>
header {
  background: linear-gradient(135deg, #ff9a56 0%, #ff6b35 100%);
  color: white;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

h1 {
  margin: 0;
  font-size: 1.5rem;
}

@media (max-width: 768px) {
  header {
    padding: 1rem;
  }

  h1 {
    font-size: 1.1rem;
  }
}

main {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}
</style>
