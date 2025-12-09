<template>
  <div class="space-y-6">
    <!-- Header Section -->
    <div class="flex justify-between items-end">
      <div>
        <h2 class="text-3xl font-bold text-slate-800">儀表板</h2>
        <p class="text-slate-500 mt-1">庫存成效總覽。</p>
      </div>
      <div class="flex space-x-3">
        <button class="flex items-center gap-2 px-4 py-2 bg-white/50 hover:bg-white text-slate-600 rounded-lg text-sm font-medium transition-colors shadow-sm">
          <ArrowDownTrayIcon class="w-4 h-4" />
          匯出報表
        </button>
        <button class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium shadow-lg shadow-blue-500/30 transition-all transform hover:-translate-y-0.5">
          <PlusIcon class="w-4 h-4" />
          新增訂單
        </button>
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="(stat, index) in stats" :key="index" class="glass-card p-6 relative overflow-hidden group">
        <div class="absolute -right-6 -top-6 w-24 h-24 rounded-full opacity-10 transition-transform group-hover:scale-110" :class="stat.colorBg"></div>
        <div class="flex justify-between items-start">
          <div>
            <p class="text-sm font-medium text-slate-500">{{ stat.title }}</p>
            <h3 class="text-3xl font-bold text-slate-800 mt-2">{{ stat.value }}</h3>
            <p class="text-xs mt-2" :class="stat.trend > 0 ? 'text-green-500' : 'text-red-500'">
              較上月 {{ stat.trend > 0 ? '+' : '' }}{{ stat.trend }}%
            </p>
          </div>
          <div class="p-3 rounded-xl bg-opacity-10" :class="[stat.colorBg, stat.colorText]">
            <component :is="stat.icon" class="w-6 h-6" />
          </div>
        </div>
      </div>
    </div>

    <!-- Charts & Tables Row -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Chart Section -->
      <div class="lg:col-span-2 glass-card p-6 h-[400px] flex flex-col">
        <h3 class="font-bold text-lg text-slate-700 mb-6">銷售總覽</h3>
        <div class="flex-1 flex items-center justify-center border-2 border-dashed border-slate-200 rounded-xl bg-slate-50/50">
          <p class="text-slate-400 font-medium">圖表顯示區域</p>
          <!-- Chart library can be added here later -->
        </div>
      </div>

      <!-- Recent Activity -->
      <div class="glass-card p-6 h-[400px] overflow-hidden flex flex-col">
        <h3 class="font-bold text-lg text-slate-700 mb-4">最新訂單</h3>
        <div class="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
          <div v-for="order in recentOrders" :key="order.id" class="flex items-center p-3 rounded-lg hover:bg-slate-50 transition-colors border border-transparent hover:border-slate-100">
            <div class="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold text-xs">
              {{ order.platform_order_id.slice(-4) }}
            </div>
            <div class="ml-3 flex-1">
              <p class="text-sm font-semibold text-slate-800">{{ order.customer_name || '未知客戶' }}</p>
              <p class="text-xs text-slate-500">{{ order.order_date }}</p>
            </div>
            <!-- Total amount logic if available, otherwise just order ID -->
            <div class="text-sm font-bold text-slate-700">#{{ order.platform_order_id }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { 
  CurrencyDollarIcon, 
  ShoppingBagIcon, 
  TagIcon, 
  ExclamationTriangleIcon, 
  ArrowDownTrayIcon, 
  PlusIcon 
} from '@heroicons/vue/24/outline';
import api from '../api';

const stats = ref([
  { title: '總營收', value: '$0', trend: 0, icon: CurrencyDollarIcon, colorBg: 'bg-emerald-500', colorText: 'text-emerald-500' },
  { title: '總訂單數', value: '0', trend: 0, icon: ShoppingBagIcon, colorBg: 'bg-blue-500', colorText: 'text-blue-500' },
  { title: '上架商品', value: '0', trend: 0, icon: TagIcon, colorBg: 'bg-purple-500', colorText: 'text-purple-500' },
  { title: '低庫存警示', value: '0', trend: 0, icon: ExclamationTriangleIcon, colorBg: 'bg-orange-500', colorText: 'text-orange-500' },
]);

const recentOrders = ref([]);

const fetchData = async () => {
    try {
        const [ordersRes, productsRes] = await Promise.all([
            api.getSalesOrders(),
            api.getProducts()
        ]);

        const orders = ordersRes.data;
        const products = productsRes.data;

        // Calculate Stats
        const totalOrders = orders.length;
        const totalProducts = products.length;
        const lowStockCount = products.filter(p => p.current_qty < 10).length;

        // Update Stats Object
        // Revenue is hard to calculate without proper endpoints, keeping 0 or placeholder
        stats.value[1].value = totalOrders.toString();
        stats.value[2].value = totalProducts.toString();
        stats.value[3].value = lowStockCount.toString();

        // Recent Orders
        recentOrders.value = orders.slice(0, 10); // Last 10 orders

    } catch (error) {
        console.error("Failed to load dashboard data", error);
    }
};

onMounted(() => {
    fetchData();
});
</script>
