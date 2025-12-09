<template>
  <div class="space-y-6">
    <div>
      <h2 class="text-3xl font-bold text-slate-800">系統設定</h2>
      <p class="text-slate-500 mt-1">調整系統參數與個人化選項。</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- General Settings -->
      <div class="glass-card p-6">
        <h3 class="text-xl font-bold text-slate-700 mb-4 border-b border-slate-100 pb-2">一般設定</h3>
        <div class="space-y-4">
          <div class="flex justify-between items-center">
            <div>
              <p class="font-medium text-slate-700">預設幣別</p>
              <p class="text-xs text-slate-500">系統主要的計價貨幣</p>
            </div>
            <select class="form-select bg-slate-50 border border-slate-200 rounded-lg text-sm px-3 py-1">
              <option>TWD (新台幣)</option>
              <option>USD (美元)</option>
            </select>
          </div>
          <div class="flex justify-between items-center">
            <div>
              <p class="font-medium text-slate-700">啟用深色模式</p>
              <p class="text-xs text-slate-500">切換介面主題</p>
            </div>
            <button class="w-12 h-6 bg-slate-200 rounded-full relative transition-colors">
              <span class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm"></span>
            </button>
          </div>
        </div>
      </div>

      <!-- Account Settings -->
      <div class="glass-card p-6">
        <h3 class="text-xl font-bold text-slate-700 mb-4 border-b border-slate-100 pb-2">帳號設定</h3>
        <form class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">顯示名稱</label>
            <input type="text" value="管理員" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input type="email" value="admin@example.com" class="w-full px-3 py-2 bg-slate-50 border border-slate-200 rounded-lg">
          </div>
          <button class="w-full py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors">
            儲存變更
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
