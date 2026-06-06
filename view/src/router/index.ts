import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { title: '儀表板' },
        },
        // Monthly Report
        {
          path: 'monthly-report/cash-flow',
          name: 'CashFlow',
          component: () => import('@/views/monthly-report/CashFlowView.vue'),
          meta: { title: '月度帳務', breadcrumb: ['月度帳務'] },
        },
        // Year Report
        {
          path: 'year-report/balance-sheet',
          name: 'BalanceSheet',
          component: () => import('@/views/year-report/BalanceSheetView.vue'),
          meta: { title: '資產負債表', breadcrumb: ['財務報表', '資產負債表'] },
        },
        {
          path: 'year-report/income-statement',
          name: 'IncomeStatement',
          component: () => import('@/views/year-report/IncomeStatementView.vue'),
          meta: { title: '損益表', breadcrumb: ['財務報表', '損益表'] },
        },
        {
          path: 'year-report/cash-flow-statement',
          name: 'CashFlowStatement',
          component: () => import('@/views/year-report/CashFlowStatementView.vue'),
          meta: { title: '現金流量表', breadcrumb: ['財務報表', '現金流量表'] },
        },
        {
          path: 'year-report/spending',
          name: 'Spending',
          component: () => import('@/views/year-report/SpendingView.vue'),
          meta: { title: '年度支出', breadcrumb: ['財務報表', '年度支出'] },
        },
        {
          path: 'year-report/assets',
          name: 'Assets',
          component: () => import('@/views/year-report/AssetView.vue'),
          meta: { title: '資產概覽', breadcrumb: ['財務報表', '資產概覽'] },
        },
        // Other Assets & Liabilities
        {
          path: 'other-assets',
          name: 'OtherAssets',
          component: () => import('@/views/other-assets/OtherAssetsView.vue'),
          meta: { title: '資產負債管理' },
        },
        // Settings
        {
          path: 'setting/menu',
          name: 'SettingMenu',
          component: () => import('@/views/setting/MenuSettingView.vue'),
          meta: { title: '選單設定', breadcrumb: ['設定', '選單'] },
        },
        {
          path: 'setting/budget',
          name: 'SettingBudget',
          component: () => import('@/views/setting/BudgetSettingView.vue'),
          meta: { title: '預算設定', breadcrumb: ['設定', '預算'] },
        },
        {
          path: 'setting/remind',
          name: 'SettingRemind',
          component: () => import('@/views/setting/RemindSettingView.vue'),
          meta: { title: '提醒設定', breadcrumb: ['設定', '提醒'] },
        },
        // Utilities
        {
          path: 'utilities/import',
          name: 'UtilitiesImport',
          component: () => import('@/views/utilities/ImportView.vue'),
          meta: { title: '資料匯入', breadcrumb: ['工具', '資料匯入'] },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

// Update document title on route change
router.afterEach((to) => {
  const title = to.meta?.title as string
  document.title = title ? `${title} — Balance Sheet` : 'Balance Sheet'
})

export default router
