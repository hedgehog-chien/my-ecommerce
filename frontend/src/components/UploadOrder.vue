<template>
  <div class="upload-container">
    <div class="glass-card">
      <h2 class="title">Upload Sales Orders</h2>
      <p class="subtitle">Import your Maihuobian Excel files to update inventory.</p>

      <div 
        class="drop-zone" 
        @dragover.prevent 
        @drop.prevent="handleDrop"
        @click="triggerFileInput"
        :class="{ 'is-dragging': isDragging }"
        @dragenter="isDragging = true"
        @dragleave="isDragging = false"
      >
        <div class="icon-wrapper">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        </div>
        <p v-if="!file">Click or Drag file to this area to upload</p>
        <p v-else class="file-name">{{ file.name }}</p>
        <input 
          type="file" 
          ref="fileInput" 
          @change="handleFileChange" 
          accept=".xlsx, .xls" 
          style="display: none" 
        />
      </div>

      <button 
        class="upload-btn" 
        @click="uploadFile" 
        :disabled="!file || uploading"
      >
        <span v-if="uploading">Processing...</span>
        <span v-else>Import Orders</span>
      </button>

      <div v-if="message" :class="['message', status]">
        {{ message }}
      </div>
    </div>

    <!-- Results Table -->
    <div v-if="parsedData.length > 0" class="results-container glass-card">
      <h3>Imported Data Preview</h3>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Order ID</th>
              <th>Product</th>
              <th>Quantity</th>
              <th>Price</th>
              <th>Customer</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in parsedData" :key="index">
              <td>{{ item.platform_order_id }}</td>
              <td>{{ item.product_name }}</td>
              <td>{{ item.quantity }}</td>
              <td>{{ item.unit_price }}</td>
              <td>{{ item.customer_name }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';

const file = ref(null);
const fileInput = ref(null);
const uploading = ref(false);
const message = ref('');
const status = ref('');
const parsedData = ref([]);
const isDragging = ref(false);

const triggerFileInput = () => {
  fileInput.value.click();
};

const handleFileChange = (event) => {
  const selectedFile = event.target.files[0];
  if (selectedFile) {
    file.value = selectedFile;
    message.value = '';
    parsedData.value = [];
  }
};

const handleDrop = (event) => {
  isDragging.value = false;
  const droppedFile = event.dataTransfer.files[0];
  if (droppedFile && (droppedFile.name.endsWith('.xlsx') || droppedFile.name.endsWith('.xls'))) {
    file.value = droppedFile;
    message.value = '';
    parsedData.value = [];
  } else {
    message.value = 'Please upload a valid Excel file.';
    status.value = 'error';
  }
};

const uploadFile = async () => {
  if (!file.value) return;

  uploading.value = true;
  message.value = '';
  parsedData.value = [];

  const formData = new FormData();
  formData.append('file', file.value);

  try {
    // Assuming backend is running on default port 8000
    const response = await axios.post('http://localhost:8000/api/orders/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });

    if (response.data.status === 'success') {
      message.value = `Successfully parsed ${response.data.parsed_count} orders!`;
      status.value = 'success';
      parsedData.value = response.data.data;
    }
  } catch (error) {
    console.error(error);
    message.value = error.response?.data?.detail || 'Failed to upload file.';
    status.value = 'error';
  } finally {
    uploading.value = false;
  }
};
</script>

<style scoped>
.upload-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.glass-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  padding: 2.5rem;
  width: 100%;
  box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
}

.title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  text-align: center;
}

.subtitle {
  color: #666;
  text-align: center;
  margin-bottom: 2rem;
}

.drop-zone {
  border: 2px dashed #a0aec0;
  border-radius: 12px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.5);
}

.drop-zone:hover, .drop-zone.is-dragging {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
}

.icon-wrapper {
  color: #667eea;
  margin-bottom: 1rem;
}

.file-name {
  font-weight: 600;
  color: #4a5568;
}

.upload-btn {
  width: 100%;
  margin-top: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.upload-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4);
}

.upload-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.message {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
}

.message.success {
  background: rgba(72, 187, 120, 0.2);
  color: #2f855a;
}

.message.error {
  background: rgba(245, 101, 101, 0.2);
  color: #c53030;
}

.results-container {
  margin-top: 2rem;
}

.table-wrapper {
  overflow-x: auto;
  margin-top: 1rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

th {
  font-weight: 600;
  color: #4a5568;
}

td {
  color: #2d3748;
}
</style>
