<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-3xl font-bold text-slate-800">採購管理</h2>
        <p class="text-slate-500 mt-1">記錄進貨批次、成本與匯率資訊。</p>
      </div>
      <button class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg text-sm font-medium shadow-lg shadow-blue-500/30 transition-all transform hover:-translate-y-0.5">
        + 新增採購批次
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div class="glass-card p-6 flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-slate-500">本月採購金額 (JPY)</p>
          <h3 class="text-2xl font-bold text-slate-800 mt-1">¥ 1,240,000</h3>
        </div>
        <div class="p-3 bg-purple-100 rounded-xl text-purple-600 text-xl">💴</div>
      </div>
      <div class="glass-card p-6 flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-slate-500">平均匯率</p>
          <h3 class="text-2xl font-bold text-slate-800 mt-1">0.2145</h3>
        </div>
        <div class="p-3 bg-blue-100 rounded-xl text-blue-600 text-xl">📈</div>
      </div>
      <div class="glass-card p-6 flex items-center justify-between">
        <div>
          <p class="text-sm font-medium text-slate-500">預估運費成本</p>
          <h3 class="text-2xl font-bold text-slate-800 mt-1">$ 45,200</h3>
        </div>
        <div class="p-3 bg-orange-100 rounded-xl text-orange-600 text-xl">🚢</div>
      </div>
    </div>

    <!-- Batches List -->
    <div class="glass-card">
      <div class="border-b border-slate-200 p-4">
        <h3 class="font-bold text-lg text-slate-700">近期採購紀錄</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left">
          <thead class="bg-slate-50">
            <tr>
              <th class="p-4 font-semibold text-slate-600">批次日期</th>
              <th class="p-4 font-semibold text-slate-600">來源</th>
              <th class="p-4 font-semibold text-slate-600">總金額 (JPY)</th>
              <th class="p-4 font-semibold text-slate-600">匯率</th>
              <th class="p-4 font-semibold text-slate-600">運費 (TWD)</th>
              <th class="p-4 font-semibold text-slate-600">狀態</th>
              <th class="p-4 font-semibold text-slate-600">詳細</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100">
            <tr v-for="batch in batches" :key="batch.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="p-4 text-slate-700">{{ batch.date }}</td>
              <td class="p-4 text-slate-700">{{ batch.source }}</td>
              <td class="p-4 text-slate-700 font-mono">¥ {{ batch.total_jpy.toLocaleString() }}</td>
              <td class="p-4 text-slate-500 font-mono">{{ batch.rate }}</td>
              <td class="p-4 text-slate-700 font-medium">$ {{ batch.shipping_fee.toLocaleString() }}</td>
              <td class="p-4">
                <span class="px-2 py-1 rounded text-xs font-bold bg-green-100 text-green-700">已入庫</span>
              </td>
              <td class="p-4">
                <button class="text-blue-500 hover:text-blue-700 font-medium text-sm">查看內容</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '../api';

const batches = ref([]);
const loading = ref(false);

const fetchBatches = async () => {
    loading.value = true;
    try {
        const response = await api.getPurchases();
        batches.value = response.data.map(batch => ({
            id: batch.id,
            date: batch.purchase_date,
            source: batch.source,
            total_jpy: batch.total_jpy,
            rate: batch.exchange_rate,
            shipping_fee: batch.total_shipping_twd
        }));
    } catch (error) {
        console.error('Failed to fetch purchase batches:', error);
    } finally {
        loading.value = false;
    }
};

onMounted(() => {
    fetchBatches();
});
</script>

