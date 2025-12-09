<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <div>
        <h2 class="text-3xl font-bold text-slate-800">上傳銷售訂單</h2>
        <p class="text-slate-500 mt-1">匯入您的買貨便 Excel 檔案以更新庫存。</p>
      </div>
    </div>

    <div class="glass-card p-10 max-w-2xl mx-auto text-center">
      <div 
        class="border-2 border-dashed border-slate-300 rounded-2xl p-12 transition-all duration-300 bg-white/40 cursor-pointer hover:border-blue-500 hover:bg-blue-50/50 group"
        :class="{ 'border-blue-500 bg-blue-50/50': isDragging }"
        @dragover.prevent 
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
        @dragenter="isDragging = true"
        @dragleave="isDragging = false"
      >
        <div class="mb-4 text-blue-500 group-hover:scale-110 transition-transform duration-300">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
          </svg>
        </div>
        
        <p v-if="!file" class="text-lg font-medium text-slate-600">
          點擊或拖曳檔案至此區域上傳
        </p>
        <div v-else class="flex items-center justify-center space-x-2 bg-blue-100 p-2 rounded-lg inline-block">
          <span class="text-2xl">📄</span>
          <span class="font-bold text-slate-700">{{ file.name }}</span>
        </div>
        
        <input 
          type="file" 
          ref="fileInput" 
          @change="handleFileChange" 
          accept=".xlsx, .xls" 
          class="hidden" 
        />
      </div>

      <div class="mt-8 flex justify-center">
        <button 
          class="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-lg font-bold rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-xl hover:-translate-y-1 transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
          @click="uploadFile" 
          :disabled="!file || uploading"
        >
          <span v-if="uploading" class="flex items-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            處理中...
          </span>
          <span v-else>匯入訂單</span>
        </button>
      </div>

      <div v-if="message" class="mt-6 p-4 rounded-xl text-sm font-medium" :class="status === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">
        {{ message }}
      </div>
    </div>

    <!-- Results Summary -->
    <div v-if="resultSummary" class="glass-card p-8 mt-8">
      <h3 class="text-xl font-bold text-slate-800 mb-6 text-center">匯入結果統計</h3>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <!-- Created Orders -->
        <div class="bg-green-50 p-6 rounded-2xl border border-green-100 text-center">
          <div class="text-3xl font-bold text-green-600 mb-2">{{ resultSummary.created_orders }}</div>
          <div class="text-sm font-medium text-green-800">新增訂單</div>
        </div>
        
        <!-- Skipped Orders -->
        <div class="bg-amber-50 p-6 rounded-2xl border border-amber-100 text-center">
          <div class="text-3xl font-bold text-amber-600 mb-2">{{ resultSummary.skipped_orders }}</div>
          <div class="text-sm font-medium text-amber-800">重複跳過</div>
        </div>

        <!-- Created Products -->
        <div class="bg-blue-50 p-6 rounded-2xl border border-blue-100 text-center">
          <div class="text-3xl font-bold text-blue-600 mb-2">{{ resultSummary.created_products }}</div>
          <div class="text-sm font-medium text-blue-800">新增商品</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api';

const file = ref(null);
const fileInput = ref(null);
const uploading = ref(false);
const message = ref('');
const status = ref('');
const resultSummary = ref(null);
const isDragging = ref(false);

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileChange = (event) => {
  const selectedFile = event.target.files[0];
  if (selectedFile) {
    file.value = selectedFile;
    message.value = '';
    resultSummary.value = null;
  }
};

const handleDrop = (event) => {
  isDragging.value = false;
  const droppedFile = event.dataTransfer.files[0];
  if (droppedFile && (droppedFile.name.endsWith('.xlsx') || droppedFile.name.endsWith('.xls'))) {
    file.value = droppedFile;
    message.value = '';
    resultSummary.value = null;
  } else {
    message.value = '請上傳有效的 Excel 檔案。';
    status.value = 'error';
  }
};

const uploadFile = async () => {
  if (!file.value) return;

  uploading.value = true;
  message.value = '';
  resultSummary.value = null;

  const formData = new FormData();
  formData.append('file', file.value);

  try {
    const response = await api.uploadSalesOrder(formData);

    // Adapted to the user's expected format, though backend might just return list
    // Check if response data has status or if it is the list directly
    if (response.data.status === 'success') {
      const res = response.data.result;
      message.value = '匯入完成！';
      status.value = 'success';
      resultSummary.value = res;
    } else if (Array.isArray(response.data)) {
        // Fallback if backend returns list of orders (as per current backend code)
        message.value = `成功解析 ${response.data.length} 筆訂單！`;
        status.value = 'success';
        // Mock summary since backend doesn't provide it yet
        resultSummary.value = {
            created_orders: response.data.length,
            skipped_orders: 0,
            created_products: 0
        };
    }
  } catch (error) {
    console.error(error);
    message.value = error.response?.data?.detail || '上傳失敗。';
    status.value = 'error';
  } finally {
    uploading.value = false;
  }
};
</script>
