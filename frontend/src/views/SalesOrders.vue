<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-3xl font-bold text-slate-800">銷售訂單列表</h2>
        <p class="text-slate-500 mt-1">檢視所有已上傳的銷售訂單記錄。</p>
      </div>
      <div class="flex space-x-3">
         <button @click="handleDeleteAll" class="px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-lg text-sm font-medium transition-colors">
            全部刪除 (測試用)
         </button>
         <router-link to="/upload" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium shadow-lg shadow-blue-500/30 transition-all transform hover:-translate-y-0.5">
          + 上傳新訂單
        </router-link>
      </div>
    </div>

    <!-- Filters -->
    <div class="glass-card p-4 flex gap-4">
      <div class="relative flex-1">
        <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400">🔍</span>
        <input 
          type="text" 
          v-model="searchQuery"
          placeholder="搜尋訂單編號或客戶名稱..." 
          class="w-full pl-10 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500/50"
        >
      </div>
      <input 
        type="date" 
        class="px-4 py-2 bg-slate-50 border border-slate-200 rounded-lg text-slate-600 focus:outline-none focus:ring-2 focus:ring-blue-500/50"
      >
    </div>

    <!-- Orders Table -->
    <div class="glass-card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-slate-50 border-b border-slate-200">
            <tr>
              <th class="p-4 font-semibold text-slate-600">訂單編號</th>
              <th class="p-4 font-semibold text-slate-600">日期</th>
              <th class="p-4 font-semibold text-slate-600">客戶名稱</th>
              <th class="p-4 font-semibold text-slate-600">品項數</th>
              <th class="p-4 font-semibold text-slate-600">總金額 (預估)</th>
              <th class="p-4 font-semibold text-slate-600 w-24">詳情</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-if="loading">
                <td colspan="6" class="p-8 text-center text-slate-500">載入中...</td>
            </tr>
            <tr v-else-if="filteredOrders.length === 0">
                <td colspan="6" class="p-8 text-center text-slate-500">尚無訂單資料</td>
            </tr>
            <template v-for="order in filteredOrders" :key="order.id">
              <tr class="hover:bg-slate-50/50 transition-colors group cursor-pointer" @click="toggleExpand(order.id)">
                <td class="p-4 font-mono text-blue-600 font-medium">{{ order.platform_order_id }}</td>
                <td class="p-4 text-slate-600">{{ order.order_date }}</td>
                <td class="p-4 text-slate-700 font-medium">{{ order.customer_name }}</td>
                <td class="p-4 text-slate-600">{{ order.items.length }}</td>
                <td class="p-4 text-slate-700 font-bold">${{ calculateTotal(order.items).toLocaleString() }}</td>
                <td class="p-4">
                  <button class="text-slate-400 hover:text-blue-500 transition-colors">
                    {{ expandedOrderId === order.id ? '▲' : '▼' }}
                  </button>
                </td>
              </tr>
              <!-- Expanded Details Row -->
              <tr v-if="expandedOrderId === order.id" class="bg-blue-50/30">
                  <td colspan="6" class="p-0">
                      <div class="p-4 pl-12">
                          <table class="w-full text-sm">
                              <thead class="text-slate-500 border-b border-blue-100">
                                  <tr>
                                      <th class="pb-2">商品名稱</th>
                                      <th class="pb-2">數量</th>
                                      <th class="pb-2">單價</th>
                                      <th class="pb-2">小計</th>
                                  </tr>
                              </thead>
                              <tbody>
                                  <tr v-for="item in order.items" :key="item.id">
                                      <td class="py-2 text-slate-700">{{ item.product_name }}</td>
                                      <td class="py-2 text-slate-600">{{ item.quantity }}</td>
                                      <td class="py-2 text-slate-600">${{ item.unit_price }}</td>
                                      <td class="py-2 text-slate-600 font-medium">${{ item.total_price }}</td>
                                  </tr>
                              </tbody>
                          </table>
                      </div>
                  </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
      <!-- Pagination (Simple) -->
      <div class="p-4 border-t border-slate-100 flex justify-between items-center text-sm text-slate-500">
        <span>顯示 {{ filteredOrders.length }} 筆資料</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import api from '../api';

const orders = ref([]);
const loading = ref(false);
const searchQuery = ref('');
const expandedOrderId = ref(null);

const fetchOrders = async () => {
  loading.value = true;
  try {
    const response = await api.getSalesOrders();
    orders.value = response.data;
  } catch (error) {
    console.error('Failed to fetch orders:', error);
  } finally {
    loading.value = false;
  }
};

const handleDeleteAll = async () => {
    if (!confirm('確定要刪除所有訂單嗎？此操作無法復原。')) return;
    try {
        await api.deleteAllSalesOrders();
        await fetchOrders();
        alert('已清除所有訂單');
    } catch (error) {
        console.error(error);
        alert('刪除失敗');
    }
};

const calculateTotal = (items) => {
  return items.reduce((sum, item) => sum + (item.total_price || (item.quantity * item.unit_price)), 0);
};

const filteredOrders = computed(() => {
  if (!searchQuery.value) return orders.value;
  const lowerQuery = searchQuery.value.toLowerCase();
  return orders.value.filter(order => 
    order.platform_order_id.toLowerCase().includes(lowerQuery) ||
    (order.customer_name && order.customer_name.toLowerCase().includes(lowerQuery))
  );
});

const toggleExpand = (id) => {
    if (expandedOrderId.value === id) {
        expandedOrderId.value = null;
    } else {
        expandedOrderId.value = id;
    }
};

onMounted(() => {
  fetchOrders();
});
</script>
