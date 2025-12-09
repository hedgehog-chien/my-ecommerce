<script setup>
import Sidebar from './components/Sidebar.vue'
</script>

<template>
  <div class="flex min-h-screen">
    <Sidebar />
    <main class="flex-1 ml-64 p-8 overflow-x-hidden">
      <!-- Top header area could go here if needed, or be part of views -->
      <div class="max-w-7xl mx-auto">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
