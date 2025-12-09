import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

export default {
    // Products
    getProducts() {
        return apiClient.get('/products/');
    },
    getProduct(id) {
        return apiClient.get(`/products/${id}`);
    },
    createProduct(data) {
        return apiClient.post('/products/', data);
    },

    // Purchases
    getPurchases() {
        return apiClient.get('/purchases/');
    },
    createPurchase(data) {
        return apiClient.post('/purchases/', data);
    },

    // Sales
    getSalesOrders() {
        return apiClient.get('/sales/');
    },
    createSalesOrder(data) {
        return apiClient.post('/sales/', data);
    },
    uploadSalesOrder(formData) {
        return apiClient.post('/sales/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
    },
    deleteAllSalesOrders() {
        return apiClient.delete('/sales/all');
    },


    // Inventory Stats
    getInventoryStats() {
        return apiClient.get('/inventory/stats');
    },

    // Dashboard Stats (Combined)
    getDashboardStats() {
        return Promise.all([
            this.getSalesOrders(),
            this.getProducts(),
            this.getInventoryStats()
        ]);
    }
};
