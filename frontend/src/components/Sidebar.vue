<template>
  <aside class="w-64 h-screen bg-white/40 backdrop-blur-md border border-white/30 flex flex-col fixed left-0 top-0 z-50">
    <div class="px-6 py-8">
      <h1 class="text-2xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
        MyShop
      </h1>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 px-4 space-y-2">
      <router-link 
        v-for="item in navItems" 
        :key="item.path" 
        :to="item.path"
        class="flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 group"
        :class="$route.path === item.path ? 'bg-blue-50 text-blue-600 shadow-sm' : 'text-slate-500 hover:bg-white/50 hover:text-slate-700'"
      >
        <component :is="item.icon" class="w-6 h-6 transition-colors group-hover:text-blue-500" :class="$route.path === item.path ? 'text-blue-600' : 'text-slate-400'" />
        <span class="font-medium">{{ item.name }}</span>
      </router-link>
    </nav>

    <!-- User Profile -->
    <div class="p-4 m-4 bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl border border-blue-100">
      <div class="flex items-center space-x-3">
        <div class="w-10 h-10 rounded-full bg-blue-200 flex items-center justify-center text-blue-700 font-bold">
          JD
        </div>
        <div>
          <p class="text-sm font-bold text-slate-700">John Doe</p>
          <p class="text-xs text-slate-500">Admin</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { 
  ChartBarIcon, 
  ClipboardDocumentListIcon, 
  CubeIcon, 
  CloudArrowUpIcon, 
  ShoppingBagIcon, 
  Cog6ToothIcon 
} from '@heroicons/vue/24/outline';

const navItems = [
  { name: '儀表板', path: '/', icon: ChartBarIcon },
  { name: '訂單列表', path: '/orders', icon: ClipboardDocumentListIcon },
  { name: '庫存管理', path: '/inventory', icon: CubeIcon },
  { name: '上傳訂單', path: '/upload', icon: CloudArrowUpIcon },
  { name: '採購管理', path: '/purchase', icon: ShoppingBagIcon },
  { name: '設定', path: '/settings', icon: Cog6ToothIcon },
];
</script>
