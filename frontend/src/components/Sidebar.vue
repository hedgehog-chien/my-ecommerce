<template>
  <aside class="w-64 h-screen bg-white/40 backdrop-blur-md border border-white/30 flex flex-col fixed left-0 top-0 z-50">
    <div class="p-8 flex items-center justify-center border-b border-white/20">
      <h1 class="text-2xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
        庫存管理系統
      </h1>
    </div>

    <nav class="flex-1 px-4 py-6 space-y-2">
      <router-link 
        v-for="item in navItems" 
        :key="item.path" 
        :to="item.path"
        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group"
        active-class="bg-blue-500/10 text-blue-600 shadow-sm"
        :class="[$route.path !== item.path ? 'text-slate-500 hover:bg-white/50 hover:text-blue-500' : '']"
      >
        <span class="text-xl group-hover:scale-110 transition-transform duration-300">{{ item.icon }}</span>
        <span class="font-medium">{{ item.name }}</span>
      </router-link>
    </nav>
    
    <div class="glass-container">
      <div 
        class="bg-white/70 backdrop-blur-md border border-white/40 shadow-lg rounded-2xl p-4 flex items-center space-x-3 cursor-pointer hover:shadow-md transition-shadow">
        <div class="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-400 to-purple-400 flex items-center justify-center text-white font-bold">
          管
        </div>
        <div>
          <p class="text-sm font-bold text-slate-700">管理員</p>
          <p class="text-xs text-slate-500">超級管理員</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
const navItems = [
  { name: '儀表板', path: '/', icon: '📊' },
  { name: '訂單列表', path: '/orders', icon: '📝' },
  { name: '庫存管理', path: '/inventory', icon: '📦' },
  { name: '上傳訂單', path: '/upload', icon: '☁️' },
  { name: '採購管理', path: '/purchase', icon: '🛍️' },
  { name: '設定', path: '/settings', icon: '⚙️' },
];
</script>
