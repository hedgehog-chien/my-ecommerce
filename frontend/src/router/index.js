import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import UploadOrder from '../components/UploadOrder.vue'
import Inventory from '../views/Inventory.vue'
import Purchase from '../views/Purchase.vue'
import Settings from '../views/Settings.vue'

const routes = [
    {
        path: '/',
        name: 'Dashboard',
        component: Dashboard
    },
    {
        path: '/upload',
        name: 'Upload',
        component: UploadOrder
    },
    {
        path: '/inventory',
        name: 'Inventory',
        component: Inventory
    },
    {
        path: '/purchase',
        name: 'Purchase',
        component: Purchase
    },
    {
        path: '/orders',
        name: 'SalesOrders',
        component: () => import('../views/SalesOrders.vue')
    },
    {
        path: '/settings',
        name: 'Settings',
        component: Settings
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

export default router
