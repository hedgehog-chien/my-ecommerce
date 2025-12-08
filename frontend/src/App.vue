<script setup>
import UploadOrder from './components/UploadOrder.vue'
</script>

<template>
  <div class="app-container">
    <header class="main-header">
      <div class="logo">📦 InventorySystem</div>
      <nav>
        <a href="#" class="active">Upload</a>
        <a href="#">Inventory</a>
        <a href="#">Settings</a>
      </nav>
    </header>
    
    <main>
      <UploadOrder />
    </main>
  </div>
</template>

<style>
/* Global Reset & Base Styles */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

body {
  background: #f0f2f5;
  color: #2c3e50;
}

.app-container {
  min-height: 100vh;
  background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 100%);
  display: flex;
  flex-direction: column;
}

.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 3rem;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.logo {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

nav a {
  text-decoration: none;
  color: #718096;
  margin-left: 2rem;
  font-weight: 500;
  transition: color 0.3s;
}

nav a:hover, nav a.active {
  color: #667eea;
}

main {
  flex: 1;
  padding: 3rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}
</style>
