<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-3xl font-bold text-slate-800">庫存管理</h2>
        <p class="text-slate-500 mt-1">管理您的商品庫存與成本資訊。</p>
      </div>
      <div class="flex gap-4">
        <button @click="handleReset" class="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg text-sm font-medium shadow-lg shadow-red-500/30 transition-all transform hover:-translate-y-0.5">
          <TrashIcon class="w-4 h-4" />
          重置系統
        </button>
        <button class="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium shadow-lg shadow-blue-500/30 transition-all transform hover:-translate-y-0.5">
          <PlusIcon class="w-4 h-4" />
          新增商品
        </button>
      </div>
    </div>

    <!-- Filters & Search -->
    <div class="glass-card p-4 flex gap-4">
      <div class="relative flex-1">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">
          <MagnifyingGlassIcon class="w-5 h-5" />
        </span>
        <input 
          type="text" 
          placeholder="搜尋商品名稱或 SKU..." 
          class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50"
        >
      </div>
      <select class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50">
        <option>所有類別</option>
        <option>電子產品</option>
        <option>服飾</option>
      </select>
      <select class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50">
        <option>庫存狀態</option>
        <option>充足</option>
        <option>低庫存</option>
        <option>缺貨</option>
      </select>
    </div>

    <!-- Inventory Table -->
    <div class="glass-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="p-4 font-semibold text-slate-600">商品名稱</th>
              <th class="p-4 font-semibold text-slate-600">SKU</th>
              <th class="p-4 font-semibold text-slate-600">庫存數量</th>
              <th class="p-4 font-semibold text-slate-600">平均成本 (TWD)</th>
              <th class="p-4 font-semibold text-slate-600">重量 (g)</th>
              <th class="p-4 font-semibold text-slate-600">狀態</th>
              <th class="p-4 font-semibold text-slate-600 w-24">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="item in products" :key="item.id" class="hover:bg-slate-50/50 transition-colors group">
              <td class="p-4">
                <div class="font-medium text-slate-800">{{ item.name }}</div>
              </td>
              <td class="p-4 text-slate-500 font-mono text-sm">{{ item.sku }}</td>
              <td class="p-4">
                <span :class="getStockColor(item.current_qty)" class="px-2 py-1 rounded-md text-sm font-bold bg-opacity-20">
                  {{ item.current_qty }}
                </span>
              </td>
              <td class="p-4 text-slate-700 font-medium">${{ item.avg_cost_twd.toFixed(2) }}</td>
              <td class="p-4 text-slate-500">{{ item.weight_g }}g</td>
              <td class="p-4">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getStatusBadge(item.current_qty)">
                  {{ getStatusText(item.current_qty) }}
                </span>
              </td>
              <td class="p-4">
                <div class="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button class="text-blue-500 hover:text-blue-700">
                    <PencilSquareIcon class="w-5 h-5" />
                  </button>
                  <button class="text-red-500 hover:text-red-700">
                    <TrashIcon class="w-5 h-5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- Pagination -->
      <div class="p-4 border-t border-slate-100 flex justify-between items-center text-sm text-slate-500">
        <span>顯示 1 至 10 筆，共 {{ products.length }} 筆</span>
        <div class="flex space-x-1">
          <button class="px-3 py-1 border border-slate-200 rounded hover:bg-slate-50 disabled:opacity-50">‹</button>
          <button class="px-3 py-1 bg-blue-50 text-blue-600 border border-blue-200 rounded font-bold">1</button>
          <button class="px-3 py-1 border border-slate-200 rounded hover:bg-slate-50">2</button>
          <button class="px-3 py-1 border border-slate-200 rounded hover:bg-slate-50">›</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { 
  TrashIcon, 
  PlusIcon, 
  MagnifyingGlassIcon, 
  PencilSquareIcon 
} from '@heroicons/vue/24/outline';
import api from '../api';


const products = ref([]);
const loading = ref(false);

const fetchProducts = async () => {
  loading.value = true;
  try {
    const response = await api.getProducts();
    products.value = response.data;
  } catch (error) {
    console.error('Failed to fetch products:', error);
  } finally {
    loading.value = false;
  }
};

const handleReset = async () => {
  if (confirm('警告：此操作將刪除所有「商品」、「訂單」與「採購」資料，且無法復原！\n\n確定要重置系統嗎？')) {
    try {
      await api.resetInventory();
      alert('系統已重置！');
      await fetchProducts();
    } catch (error) {
      console.error('Reset failed:', error);
      alert('重置失敗，請檢查後端連線。');
    }
  }
};

onMounted(() => {
  fetchProducts();
});

const getStockColor = (qty) => {
  if (qty === 0) return 'text-red-600 bg-red-100';
  if (qty < 10) return 'text-orange-600 bg-orange-100';
  return 'text-green-600 bg-green-100';
};

const getStatusBadge = (qty) => {
  if (qty === 0) return 'bg-red-100 text-red-800';
  if (qty < 10) return 'bg-orange-100 text-orange-800';
  return 'bg-green-100 text-green-800';
};

const getStatusText = (qty) => {
  if (qty === 0) return '缺貨';
  if (qty < 10) return '低庫存';
  return '充足';
};
</script>

