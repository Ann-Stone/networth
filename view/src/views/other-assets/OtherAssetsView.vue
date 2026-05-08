<template>
  <div class="flex flex-col gap-8">
    <PageHeader title="資產負債管理" subtitle="股票 / 房產 / 保險 / 貸款 / 其他資產" />

    <el-tabs v-model="activeTab" class="other-assets-tabs">
      <!-- ─── Stocks ─────────────────────────────────────────── -->
      <el-tab-pane label="股票" name="stocks">
        <section class="flex flex-col gap-4">
          <SectionHeader title="股票持有">
            <template #actions>
              <el-select
                v-model="stocksAssetId"
                placeholder="選擇資產分類"
                style="width: 240px"
                :disabled="stockCategoryOptions.length === 0"
              >
                <el-option
                  v-for="cat in stockCategoryOptions"
                  :key="cat.asset_id"
                  :label="cat.asset_name"
                  :value="cat.asset_id"
                />
              </el-select>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                :disabled="!stocksAssetId"
                @click="openCreateStock"
              >
                新增
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.stocksLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!stocksAssetId"
            message="請先選擇資產分類"
          />
          <EmptyState
            v-else-if="store.stocks.length === 0"
            message="尚無股票持有資料"
          />
          <el-table
            v-else
            :data="store.stocks"
            stripe
            border
            style="width: 100%"
            @expand-change="onStockExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="px-6 py-4 flex flex-col gap-3">
                  <div class="flex items-center justify-between">
                    <span class="text-on-surface font-medium">交易明細</span>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateStockDetail(row)"
                    >
                      新增明細
                    </el-button>
                  </div>
                  <el-skeleton
                    v-if="stockDetailsLoadingByStock.get(row.stock_id)"
                    :rows="3"
                    animated
                  />
                  <EmptyState
                    v-else-if="(stockDetailsByStock.get(row.stock_id)?.length ?? 0) === 0"
                    message="尚無交易明細"
                  />
                  <el-table
                    v-else
                    :data="stockDetailsByStock.get(row.stock_id) ?? []"
                    border
                    size="small"
                  >
                    <el-table-column prop="excute_date" label="日期" width="110" />
                    <el-table-column prop="excute_type" label="類型" width="100" />
                    <el-table-column label="數量" width="120" align="right">
                      <template #default="{ row: d }">
                        {{ d.excute_amount }}
                      </template>
                    </el-table-column>
                    <el-table-column label="單價" width="160" align="right">
                      <template #default="{ row: d }">
                        <MoneyDisplay :amount="d.excute_price" size="sm" />
                      </template>
                    </el-table-column>
                    <el-table-column prop="account_name" label="結算帳戶" min-width="160" />
                    <el-table-column prop="memo" label="備註" min-width="120">
                      <template #default="{ row: d }">
                        <span>{{ d.memo ?? '' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="180" align="center">
                      <template #default="{ row: d }">
                        <el-button size="small" :icon="Edit" @click="openEditStockDetail(row, d)">
                          編輯
                        </el-button>
                        <el-button
                          size="small"
                          type="danger"
                          :icon="Delete"
                          @click="handleDeleteStockDetail(row, d)"
                        >
                          刪除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="stock_id" label="持有 ID" width="160" />
            <el-table-column prop="stock_code" label="代號" width="140" />
            <el-table-column prop="stock_name" label="名稱" min-width="200" />
            <el-table-column label="預計投入" width="200" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.expected_spend" size="sm" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" :icon="Edit" @click="openEditStock(row)">
                  編輯
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  :icon="Delete"
                  @click="handleDeleteStock(row)"
                >
                  刪除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Estates ────────────────────────────────────────── -->
      <el-tab-pane label="房產" name="estates">
        <section class="flex flex-col gap-4">
          <SectionHeader title="房產持有">
            <template #actions>
              <el-select
                v-model="estatesAssetId"
                placeholder="選擇資產分類"
                style="width: 240px"
                :disabled="estateCategoryOptions.length === 0"
              >
                <el-option
                  v-for="cat in estateCategoryOptions"
                  :key="cat.asset_id"
                  :label="cat.asset_name"
                  :value="cat.asset_id"
                />
              </el-select>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                :disabled="!estatesAssetId"
                @click="openCreateEstate"
              >
                新增
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.estatesLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!estatesAssetId"
            message="請先選擇資產分類"
          />
          <EmptyState
            v-else-if="store.estates.length === 0"
            message="尚無房產資料"
          />
          <el-table
            v-else
            :data="store.estates"
            stripe
            border
            style="width: 100%"
            @expand-change="onEstateExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="px-6 py-4 flex flex-col gap-3">
                  <div class="flex items-center justify-between">
                    <span class="text-on-surface font-medium">收支明細</span>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateEstateDetail(row)"
                    >
                      新增明細
                    </el-button>
                  </div>
                  <el-skeleton
                    v-if="estateDetailsLoadingByEstate.get(row.estate_id)"
                    :rows="3"
                    animated
                  />
                  <EmptyState
                    v-else-if="(estateDetailsByEstate.get(row.estate_id)?.length ?? 0) === 0"
                    message="尚無收支明細"
                  />
                  <el-table
                    v-else
                    :data="estateDetailsByEstate.get(row.estate_id) ?? []"
                    border
                    size="small"
                  >
                    <el-table-column prop="excute_date" label="日期" width="110" />
                    <el-table-column prop="estate_excute_type" label="類型" width="120" />
                    <el-table-column label="金額" width="180" align="right">
                      <template #default="{ row: d }">
                        <MoneyDisplay :amount="d.excute_price" size="sm" />
                      </template>
                    </el-table-column>
                    <el-table-column prop="memo" label="備註" min-width="160">
                      <template #default="{ row: d }">
                        <span>{{ d.memo ?? '' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="180" align="center">
                      <template #default="{ row: d }">
                        <el-button size="small" :icon="Edit" @click="openEditEstateDetail(row, d)">
                          編輯
                        </el-button>
                        <el-button
                          size="small"
                          type="danger"
                          :icon="Delete"
                          @click="handleDeleteEstateDetail(row, d)"
                        >
                          刪除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="estate_id" label="ID" width="140" />
            <el-table-column prop="estate_name" label="名稱" min-width="160" />
            <el-table-column prop="estate_type" label="類型" width="120" />
            <el-table-column prop="estate_address" label="地址" min-width="200" />
            <el-table-column prop="obtain_date" label="取得日期" width="120" />
            <el-table-column label="狀態" width="100">
              <template #default="{ row }">
                <StatusBadge :variant="estateStatusVariant(row.estate_status)">
                  {{ row.estate_status }}
                </StatusBadge>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" :icon="Edit" @click="openEditEstate(row)">
                  編輯
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  :icon="Delete"
                  @click="handleDeleteEstate(row)"
                >
                  刪除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Insurances ─────────────────────────────────────── -->
      <el-tab-pane label="保險" name="insurances">
        <section class="flex flex-col gap-4">
          <SectionHeader title="保險合約">
            <template #actions>
              <el-select
                v-model="insurancesAssetId"
                placeholder="選擇資產分類"
                style="width: 240px"
                :disabled="insuranceCategoryOptions.length === 0"
              >
                <el-option
                  v-for="cat in insuranceCategoryOptions"
                  :key="cat.asset_id"
                  :label="cat.asset_name"
                  :value="cat.asset_id"
                />
              </el-select>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                :disabled="!insurancesAssetId"
                @click="openCreateInsurance"
              >
                新增
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.insurancesLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!insurancesAssetId"
            message="請先選擇資產分類"
          />
          <EmptyState
            v-else-if="store.insurances.length === 0"
            message="尚無保險合約"
          />
          <el-table
            v-else
            :data="store.insurances"
            stripe
            border
            style="width: 100%"
            @expand-change="onInsuranceExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="px-6 py-4 flex flex-col gap-3">
                  <div class="flex items-center justify-between">
                    <span class="text-on-surface font-medium">繳費明細</span>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateInsuranceDetail(row)"
                    >
                      新增明細
                    </el-button>
                  </div>
                  <el-skeleton
                    v-if="insuranceDetailsLoadingByPolicy.get(row.insurance_id)"
                    :rows="3"
                    animated
                  />
                  <EmptyState
                    v-else-if="(insuranceDetailsByPolicy.get(row.insurance_id)?.length ?? 0) === 0"
                    message="尚無繳費明細"
                  />
                  <el-table
                    v-else
                    :data="insuranceDetailsByPolicy.get(row.insurance_id) ?? []"
                    border
                    size="small"
                  >
                    <el-table-column prop="excute_date" label="日期" width="110" />
                    <el-table-column prop="insurance_excute_type" label="類型" width="120" />
                    <el-table-column label="金額" width="180" align="right">
                      <template #default="{ row: d }">
                        <MoneyDisplay :amount="d.excute_price" size="sm" />
                      </template>
                    </el-table-column>
                    <el-table-column prop="memo" label="備註" min-width="160">
                      <template #default="{ row: d }">
                        <span>{{ d.memo ?? '' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="180" align="center">
                      <template #default="{ row: d }">
                        <el-button
                          size="small"
                          :icon="Edit"
                          @click="openEditInsuranceDetail(row, d)"
                        >
                          編輯
                        </el-button>
                        <el-button
                          size="small"
                          type="danger"
                          :icon="Delete"
                          @click="handleDeleteInsuranceDetail(row, d)"
                        >
                          刪除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="insurance_id" label="ID" width="140" />
            <el-table-column prop="insurance_name" label="名稱" min-width="200" />
            <el-table-column prop="pay_type" label="繳費頻率" width="120" />
            <el-table-column prop="pay_day" label="繳款日" width="90" align="right" />
            <el-table-column label="預計保費" width="180" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.expected_spend" size="sm" />
              </template>
            </el-table-column>
            <el-table-column prop="start_date" label="起始" width="110" />
            <el-table-column prop="end_date" label="終止" width="110" />
            <el-table-column label="已結案" width="90">
              <template #default="{ row }">
                <StatusBadge :value="row.has_closed" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" :icon="Edit" @click="openEditInsurance(row)">
                  編輯
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  :icon="Delete"
                  @click="handleDeleteInsurance(row)"
                >
                  刪除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Loans ──────────────────────────────────────────── -->
      <el-tab-pane label="貸款" name="loans">
        <section class="flex flex-col gap-4">
          <SectionHeader title="貸款負債">
            <template #actions>
              <el-button type="primary" :icon="Plus" size="small" @click="openCreateLoan">
                新增
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.loansLoading" :rows="4" animated />
          <EmptyState v-else-if="store.loans.length === 0" message="尚無貸款資料" />
          <el-table
            v-else
            :data="store.loans"
            stripe
            border
            style="width: 100%"
            @expand-change="onLoanExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <div class="px-6 py-4 flex flex-col gap-3">
                  <div class="flex items-center justify-between">
                    <span class="text-on-surface font-medium">還款明細</span>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateLoanDetail(row)"
                    >
                      新增明細
                    </el-button>
                  </div>
                  <el-skeleton
                    v-if="loanDetailsLoadingByLoan.get(row.loan_id)"
                    :rows="3"
                    animated
                  />
                  <EmptyState
                    v-else-if="(loanDetailsByLoan.get(row.loan_id)?.length ?? 0) === 0"
                    message="尚無還款明細"
                  />
                  <el-table
                    v-else
                    :data="loanDetailsByLoan.get(row.loan_id) ?? []"
                    border
                    size="small"
                  >
                    <el-table-column prop="excute_date" label="日期" width="110" />
                    <el-table-column prop="loan_excute_type" label="類型" width="120" />
                    <el-table-column label="金額" width="180" align="right">
                      <template #default="{ row: d }">
                        <MoneyDisplay :amount="d.excute_price" size="sm" />
                      </template>
                    </el-table-column>
                    <el-table-column prop="memo" label="備註" min-width="160">
                      <template #default="{ row: d }">
                        <span>{{ d.memo ?? '' }}</span>
                      </template>
                    </el-table-column>
                    <el-table-column label="操作" width="180" align="center">
                      <template #default="{ row: d }">
                        <el-button size="small" :icon="Edit" @click="openEditLoanDetail(row, d)">
                          編輯
                        </el-button>
                        <el-button
                          size="small"
                          type="danger"
                          :icon="Delete"
                          @click="handleDeleteLoanDetail(row, d)"
                        >
                          刪除
                        </el-button>
                      </template>
                    </el-table-column>
                  </el-table>
                </div>
              </template>
            </el-table-column>
            <el-table-column prop="loan_id" label="ID" width="120" />
            <el-table-column prop="loan_name" label="名稱" min-width="160" />
            <el-table-column prop="loan_type" label="類型" width="120" />
            <el-table-column prop="account_name" label="還款帳戶" min-width="140" />
            <el-table-column label="利率" width="100" align="right">
              <template #default="{ row }">
                {{ (row.interest_rate * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="period" label="期數" width="80" align="right" />
            <el-table-column label="本金" width="160" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.amount" size="sm" />
              </template>
            </el-table-column>
            <el-table-column label="已還" width="160" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.repayed" size="sm" />
              </template>
            </el-table-column>
            <el-table-column prop="apply_date" label="申貸日" width="110" />
            <el-table-column label="寬限到期" width="120">
              <template #default="{ row }">
                <span>{{ row.grace_expire_date ?? '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" :icon="Edit" @click="openEditLoan(row)">
                  編輯
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  :icon="Delete"
                  @click="handleDeleteLoan(row)"
                >
                  刪除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Other-Assets ───────────────────────────────────── -->
      <el-tab-pane label="其他資產" name="other">
        <section class="flex flex-col gap-4">
          <SectionHeader title="資產分類">
            <template #actions>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                @click="openCreateOtherAsset"
              >
                新增
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.otherAssetsLoading" :rows="4" animated />
          <EmptyState
            v-else-if="otherAssetsSorted.length === 0"
            message="尚無資產分類"
          />
          <el-table v-else :data="otherAssetsSorted" stripe border style="width: 100%">
            <el-table-column prop="asset_index" label="排序" width="80" align="right" />
            <el-table-column prop="asset_id" label="ID" width="160" />
            <el-table-column prop="asset_name" label="名稱" min-width="200" />
            <el-table-column prop="asset_type" label="類型" width="140" />
            <el-table-column prop="vesting_nation" label="歸屬地" width="120" />
            <el-table-column label="啟用" width="90">
              <template #default="{ row }">
                <StatusBadge :value="row.in_use" />
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" align="center">
              <template #default="{ row }">
                <el-button size="small" :icon="Edit" @click="openEditOtherAsset(row)">
                  編輯
                </el-button>
                <el-button
                  size="small"
                  type="danger"
                  :icon="Delete"
                  @click="handleDeleteOtherAsset(row)"
                >
                  刪除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>
    </el-tabs>

    <!-- ─── Stock Create / Edit Dialog ─────────────────────────────────────── -->
    <FormDialog
      v-model="stockDialogVisible"
      :title="stockFormMode === 'create' ? '新增股票持有' : '編輯股票持有'"
      :loading="stockSubmitting"
      width="520px"
      @submit="submitStock"
    >
      <el-form
        ref="stockFormRef"
        :model="stockForm"
        :rules="stockFormRules"
        label-width="110px"
      >
        <el-form-item label="持有 ID" prop="stock_id">
          <el-input
            v-model="stockForm.stock_id"
            placeholder="例如 STK-H-001"
            :disabled="stockFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="代號" prop="stock_code">
          <el-input v-model="stockForm.stock_code" placeholder="例如 AAPL" />
        </el-form-item>
        <el-form-item label="名稱" prop="stock_name">
          <el-input v-model="stockForm.stock_name" placeholder="例如 Apple Inc." />
        </el-form-item>
        <el-form-item label="資產分類">
          <el-input :model-value="stockForm.asset_id" disabled />
        </el-form-item>
        <el-form-item label="預計投入" prop="expected_spend">
          <el-input-number
            v-model="stockForm.expected_spend"
            :precision="2"
            :step="1000"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Stock Detail Create / Edit Dialog ──────────────────────────────── -->
    <FormDialog
      v-model="stockDetailDialogVisible"
      :title="stockDetailFormMode === 'create' ? '新增股票明細' : '編輯股票明細'"
      :loading="stockDetailSubmitting"
      width="560px"
      @submit="submitStockDetail"
    >
      <el-form
        ref="stockDetailFormRef"
        :model="stockDetailForm"
        :rules="stockDetailFormRules"
        label-width="110px"
      >
        <el-form-item label="持有 ID">
          <el-input :model-value="stockDetailForm.stock_id" disabled />
        </el-form-item>
        <el-form-item label="日期" prop="excute_date">
          <el-date-picker
            v-model="stockDetailFormDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="類型" prop="excute_type">
          <el-select v-model="stockDetailForm.excute_type" style="width: 100%">
            <el-option label="買入 (buy)" value="buy" />
            <el-option label="賣出 (sell)" value="sell" />
            <el-option label="股票股利 (stock)" value="stock" />
            <el-option label="現金股利 (cash)" value="cash" />
          </el-select>
        </el-form-item>
        <el-form-item label="數量" prop="excute_amount">
          <el-input-number
            v-model="stockDetailForm.excute_amount"
            :precision="2"
            :step="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="單價" prop="excute_price">
          <el-input-number
            v-model="stockDetailForm.excute_price"
            :precision="2"
            :step="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="帳戶 ID" prop="account_id">
          <el-input v-model="stockDetailForm.account_id" placeholder="例如 BANK-CHASE-01" />
        </el-form-item>
        <el-form-item label="帳戶名稱" prop="account_name">
          <el-input v-model="stockDetailForm.account_name" placeholder="例如 Chase Checking" />
        </el-form-item>
        <el-form-item label="備註">
          <el-input
            v-model="stockDetailForm.memo"
            type="textarea"
            :rows="2"
            placeholder="(可選)"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Estate Create / Edit Dialog ────────────────────────────────────── -->
    <FormDialog
      v-model="estateDialogVisible"
      :title="estateFormMode === 'create' ? '新增房產' : '編輯房產'"
      :loading="estateSubmitting"
      width="560px"
      @submit="submitEstate"
    >
      <el-form
        ref="estateFormRef"
        :model="estateForm"
        :rules="estateFormRules"
        label-width="110px"
      >
        <el-form-item label="房產 ID" prop="estate_id">
          <el-input
            v-model="estateForm.estate_id"
            placeholder="例如 EST-001"
            :disabled="estateFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="名稱" prop="estate_name">
          <el-input v-model="estateForm.estate_name" />
        </el-form-item>
        <el-form-item label="類型" prop="estate_type">
          <el-input v-model="estateForm.estate_type" placeholder="例如 residential" />
        </el-form-item>
        <el-form-item label="地址" prop="estate_address">
          <el-input v-model="estateForm.estate_address" />
        </el-form-item>
        <el-form-item label="資產分類">
          <el-input :model-value="estateForm.asset_id" disabled />
        </el-form-item>
        <el-form-item label="取得日期" prop="obtain_date">
          <el-date-picker
            v-model="estateFormObtainDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="狀態" prop="estate_status">
          <el-select v-model="estateForm.estate_status" style="width: 100%">
            <el-option label="閒置 (idle)" value="idle" />
            <el-option label="自住 (live)" value="live" />
            <el-option label="出租 (rent)" value="rent" />
            <el-option label="售出 (sold)" value="sold" />
          </el-select>
        </el-form-item>
        <el-form-item label="關聯貸款">
          <el-input v-model="estateLoanIdProxy" placeholder="(可選) 例如 LN-001" />
        </el-form-item>
        <el-form-item label="備註">
          <el-input v-model="estateMemoProxy" type="textarea" :rows="2" placeholder="(可選)" />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Insurance Create / Edit Dialog ─────────────────────────────────── -->
    <FormDialog
      v-model="insuranceDialogVisible"
      :title="insuranceFormMode === 'create' ? '新增保險合約' : '編輯保險合約'"
      :loading="insuranceSubmitting"
      width="560px"
      @submit="submitInsurance"
    >
      <el-form
        ref="insuranceFormRef"
        :model="insuranceForm"
        :rules="insuranceFormRules"
        label-width="110px"
      >
        <el-form-item label="保險 ID" prop="insurance_id">
          <el-input
            v-model="insuranceForm.insurance_id"
            placeholder="例如 INS-001"
            :disabled="insuranceFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="名稱" prop="insurance_name">
          <el-input v-model="insuranceForm.insurance_name" />
        </el-form-item>
        <el-form-item label="資產分類">
          <el-input :model-value="insuranceForm.asset_id" disabled />
        </el-form-item>
        <el-form-item label="繳費帳戶 ID" prop="in_account">
          <el-input v-model="insuranceForm.in_account" placeholder="例如 BANK-CHASE-01" />
        </el-form-item>
        <el-form-item label="領取帳戶 ID" prop="out_account">
          <el-input v-model="insuranceForm.out_account" />
        </el-form-item>
        <el-form-item label="起始日" prop="start_date">
          <el-date-picker
            v-model="insuranceFormStartDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="終止日" prop="end_date">
          <el-date-picker
            v-model="insuranceFormEndDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="繳費頻率" prop="pay_type">
          <el-input v-model="insuranceForm.pay_type" placeholder="例如 annual / monthly" />
        </el-form-item>
        <el-form-item label="繳款日" prop="pay_day">
          <el-input-number
            v-model="insuranceForm.pay_day"
            :min="1"
            :max="31"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="預計保費" prop="expected_spend">
          <el-input-number
            v-model="insuranceForm.expected_spend"
            :precision="2"
            :step="100"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="是否結案" prop="has_closed">
          <el-radio-group v-model="insuranceForm.has_closed">
            <el-radio value="N">未結案</el-radio>
            <el-radio value="Y">已結案</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Insurance Detail Create / Edit Dialog ──────────────────────────── -->
    <FormDialog
      v-model="insuranceDetailDialogVisible"
      :title="insuranceDetailFormMode === 'create' ? '新增繳費明細' : '編輯繳費明細'"
      :loading="insuranceDetailSubmitting"
      width="520px"
      @submit="submitInsuranceDetail"
    >
      <el-form
        ref="insuranceDetailFormRef"
        :model="insuranceDetailForm"
        :rules="insuranceDetailFormRules"
        label-width="110px"
      >
        <el-form-item label="保險 ID">
          <el-input :model-value="insuranceDetailForm.insurance_id" disabled />
        </el-form-item>
        <el-form-item label="日期" prop="excute_date">
          <el-date-picker
            v-model="insuranceDetailFormDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="類型" prop="insurance_excute_type">
          <el-select v-model="insuranceDetailForm.insurance_excute_type" style="width: 100%">
            <el-option label="繳費 (pay)" value="pay" />
            <el-option label="現金回饋 (cash)" value="cash" />
            <el-option label="退費 (return)" value="return" />
            <el-option label="預期 (expect)" value="expect" />
          </el-select>
        </el-form-item>
        <el-form-item label="金額" prop="excute_price">
          <el-input-number
            v-model="insuranceDetailForm.excute_price"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="備註">
          <el-input
            v-model="insuranceDetailMemoProxy"
            type="textarea"
            :rows="2"
            placeholder="(可選)"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Other-Asset Create / Edit Dialog ───────────────────────────────── -->
    <FormDialog
      v-model="otherAssetDialogVisible"
      :title="otherAssetFormMode === 'create' ? '新增資產分類' : '編輯資產分類'"
      :loading="otherAssetSubmitting"
      width="520px"
      @submit="submitOtherAsset"
    >
      <el-form
        ref="otherAssetFormRef"
        :model="otherAssetForm"
        :rules="otherAssetFormRules"
        label-width="110px"
      >
        <el-form-item label="ID" prop="asset_id">
          <el-input
            v-model="otherAssetForm.asset_id"
            placeholder="例如 AC-STK-001"
            :disabled="otherAssetFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="名稱" prop="asset_name">
          <el-input v-model="otherAssetForm.asset_name" />
        </el-form-item>
        <el-form-item label="類型" prop="asset_type">
          <el-select v-model="otherAssetForm.asset_type" style="width: 100%" allow-create filterable>
            <el-option label="股票 (stock)" value="stock" />
            <el-option label="房產 (estate)" value="estate" />
            <el-option label="保險 (insurance)" value="insurance" />
            <el-option label="貸款 (loan)" value="loan" />
            <el-option label="其他 (other)" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="歸屬地" prop="vesting_nation">
          <el-input v-model="otherAssetForm.vesting_nation" placeholder="例如 TW / US" />
        </el-form-item>
        <el-form-item label="啟用" prop="in_use">
          <el-radio-group v-model="otherAssetForm.in_use">
            <el-radio value="Y">啟用</el-radio>
            <el-radio value="N">停用</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number
            v-model="otherAssetIndexProxy"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
          <p class="text-xs text-on-surface-variant mt-1">
            留空時後端自動指派 max(asset_index)+1
          </p>
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Loan Create / Edit Dialog ──────────────────────────────────────── -->
    <FormDialog
      v-model="loanDialogVisible"
      :title="loanFormMode === 'create' ? '新增貸款' : '編輯貸款'"
      :loading="loanSubmitting"
      width="600px"
      @submit="submitLoan"
    >
      <el-form
        ref="loanFormRef"
        :model="loanForm"
        :rules="loanFormRules"
        label-width="120px"
      >
        <el-form-item label="貸款 ID" prop="loan_id">
          <el-input
            v-model="loanForm.loan_id"
            placeholder="例如 LN-001"
            :disabled="loanFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item label="名稱" prop="loan_name">
          <el-input v-model="loanForm.loan_name" />
        </el-form-item>
        <el-form-item label="類型" prop="loan_type">
          <el-input v-model="loanForm.loan_type" placeholder="例如 mortgage / car" />
        </el-form-item>
        <el-form-item label="還款帳戶 ID" prop="account_id">
          <el-input v-model="loanForm.account_id" />
        </el-form-item>
        <el-form-item label="還款帳戶名稱" prop="account_name">
          <el-input v-model="loanForm.account_name" />
        </el-form-item>
        <el-form-item label="年利率" prop="interest_rate">
          <el-input-number
            v-model="loanForm.interest_rate"
            :precision="4"
            :step="0.001"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
          <p class="text-xs text-on-surface-variant mt-1">小數表示,例如 0.035 = 3.5%</p>
        </el-form-item>
        <el-form-item label="期數 (月)" prop="period">
          <el-input-number
            v-model="loanForm.period"
            :min="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="申貸日" prop="apply_date">
          <el-date-picker
            v-model="loanFormApplyDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="寬限到期">
          <el-date-picker
            v-model="loanFormGraceDate"
            type="date"
            format="YYYY/MM/DD"
            placeholder="(可選)"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="繳款日" prop="pay_day">
          <el-input-number
            v-model="loanForm.pay_day"
            :min="1"
            :max="31"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="本金" prop="amount">
          <el-input-number
            v-model="loanForm.amount"
            :precision="2"
            :step="10000"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="已還本金" prop="repayed">
          <el-input-number
            v-model="loanForm.repayed"
            :precision="2"
            :step="1000"
            :min="0"
            :disabled="loanFormMode === 'edit'"
            controls-position="right"
            style="width: 100%"
          />
          <span v-if="loanFormMode === 'edit'" class="text-xs text-on-surface-muted ml-2">
            由還款明細自動計算
          </span>
        </el-form-item>
        <el-form-item label="排序" prop="loan_index">
          <el-input-number
            v-model="loanForm.loan_index"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Loan Detail Create / Edit Dialog ───────────────────────────────── -->
    <FormDialog
      v-model="loanDetailDialogVisible"
      :title="loanDetailFormMode === 'create' ? '新增還款明細' : '編輯還款明細'"
      :loading="loanDetailSubmitting"
      width="520px"
      @submit="submitLoanDetail"
    >
      <el-form
        ref="loanDetailFormRef"
        :model="loanDetailForm"
        :rules="loanDetailFormRules"
        label-width="110px"
      >
        <el-form-item label="貸款 ID">
          <el-input :model-value="loanDetailForm.loan_id" disabled />
        </el-form-item>
        <el-form-item label="日期" prop="excute_date">
          <el-date-picker
            v-model="loanDetailFormDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="類型" prop="loan_excute_type">
          <el-select v-model="loanDetailForm.loan_excute_type" style="width: 100%">
            <el-option label="本金 (principal)" value="principal" />
            <el-option label="利息 (interest)" value="interest" />
            <el-option label="增貸 (increment)" value="increment" />
            <el-option label="手續費 (fee)" value="fee" />
          </el-select>
        </el-form-item>
        <el-form-item label="金額" prop="excute_price">
          <el-input-number
            v-model="loanDetailForm.excute_price"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="備註">
          <el-input
            v-model="loanDetailMemoProxy"
            type="textarea"
            :rows="2"
            placeholder="(可選)"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Estate Detail Create / Edit Dialog ─────────────────────────────── -->
    <FormDialog
      v-model="estateDetailDialogVisible"
      :title="estateDetailFormMode === 'create' ? '新增房產明細' : '編輯房產明細'"
      :loading="estateDetailSubmitting"
      width="520px"
      @submit="submitEstateDetail"
    >
      <el-form
        ref="estateDetailFormRef"
        :model="estateDetailForm"
        :rules="estateDetailFormRules"
        label-width="110px"
      >
        <el-form-item label="房產 ID">
          <el-input :model-value="estateDetailForm.estate_id" disabled />
        </el-form-item>
        <el-form-item label="日期" prop="excute_date">
          <el-date-picker
            v-model="estateDetailFormDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="類型" prop="estate_excute_type">
          <el-select v-model="estateDetailForm.estate_excute_type" style="width: 100%">
            <el-option label="稅務 (tax)" value="tax" />
            <el-option label="管理費 (fee)" value="fee" />
            <el-option label="保險 (insurance)" value="insurance" />
            <el-option label="維修 (fix)" value="fix" />
            <el-option label="租金 (rent)" value="rent" />
            <el-option label="押金 (deposit)" value="deposit" />
          </el-select>
        </el-form-item>
        <el-form-item label="金額" prop="excute_price">
          <el-input-number
            v-model="estateDetailForm.excute_price"
            :precision="2"
            :step="1000"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="備註">
          <el-input
            v-model="estateDetailMemoProxy"
            type="textarea"
            :rows="2"
            placeholder="(可選)"
          />
        </el-form-item>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, shallowReactive, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useOtherAssetsStore } from '@/stores/otherAssets'
import {
  createEstate,
  createEstateDetail,
  createInsurance,
  createInsuranceDetail,
  createLoan,
  createLoanDetail,
  createOtherAsset,
  createStock,
  createStockDetail,
  deleteEstate,
  deleteEstateDetail,
  deleteInsurance,
  deleteInsuranceDetail,
  deleteLoan,
  deleteLoanDetail,
  deleteOtherAsset,
  deleteStock,
  deleteStockDetail,
  getEstateDetails,
  getInsuranceDetails,
  getLoanDetails,
  getStockDetails,
  updateEstate,
  updateEstateDetail,
  updateInsurance,
  updateInsuranceDetail,
  updateLoan,
  updateLoanDetail,
  updateOtherAsset,
  updateStock,
  updateStockDetail,
} from '@/api/otherAssets'
import type {
  EstateAsset,
  EstateAssetCreate,
  EstateJournal,
  EstateJournalCreate,
  InsuranceAsset,
  InsuranceAssetCreate,
  InsuranceJournal,
  InsuranceJournalCreate,
  LoanAsset,
  LoanAssetCreate,
  LoanJournal,
  LoanJournalCreate,
  OtherAsset,
  OtherAssetCreate,
  StockAsset,
  StockAssetCreate,
  StockJournal,
  StockJournalCreate,
} from '@/types/models'

const store = useOtherAssetsStore()
const confirm = useConfirm()

const activeTab = ref<string>('stocks')

// ─── Stock category options ─────────────────────────────────────────────────
const stockCategoryOptions = computed(() =>
  [...store.otherAssets]
    .filter((a) => a.asset_type === 'stock' && a.in_use === 'Y')
    .sort((a, b) => a.asset_index - b.asset_index),
)

const stocksAssetId = ref<string>('')

watch(stockCategoryOptions, (options) => {
  if (!stocksAssetId.value && options.length > 0) {
    stocksAssetId.value = options[0]!.asset_id
  }
})

watch(stocksAssetId, (assetId) => {
  if (assetId) void fetchStocks(assetId)
})

async function fetchStocks(assetId: string) {
  await store.fetchStocks(assetId)
}

// ─── Stock create/edit form ─────────────────────────────────────────────────
const stockDialogVisible = ref(false)
const stockFormMode = ref<'create' | 'edit'>('create')
const stockSubmitting = ref(false)
const stockFormRef = ref<FormInstance>()

interface StockFormState extends StockAssetCreate {}

function emptyStockForm(): StockFormState {
  return {
    stock_id: '',
    stock_code: '',
    stock_name: '',
    asset_id: stocksAssetId.value,
    expected_spend: 0,
  }
}

const stockForm = ref<StockFormState>(emptyStockForm())

const stockFormRules: FormRules = {
  stock_id: [{ required: true, message: '請輸入持有 ID', trigger: 'blur' }],
  stock_code: [{ required: true, message: '請輸入代號', trigger: 'blur' }],
  stock_name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
  expected_spend: [{ required: true, message: '請輸入預計投入金額', trigger: 'blur' }],
}

function openCreateStock() {
  stockFormMode.value = 'create'
  stockForm.value = emptyStockForm()
  stockDialogVisible.value = true
}

function openEditStock(row: StockAsset) {
  stockFormMode.value = 'edit'
  stockForm.value = {
    stock_id: row.stock_id,
    stock_code: row.stock_code,
    stock_name: row.stock_name,
    asset_id: row.asset_id,
    expected_spend: row.expected_spend,
  }
  stockDialogVisible.value = true
}

async function submitStock() {
  if (!stockFormRef.value) return
  const valid = await stockFormRef.value.validate().catch(() => false)
  if (!valid) return
  stockSubmitting.value = true
  try {
    if (stockFormMode.value === 'create') {
      await createStock({ ...stockForm.value })
      ElMessage.success('新增成功')
    } else {
      await updateStock(stockForm.value.stock_id, {
        stock_code: stockForm.value.stock_code,
        stock_name: stockForm.value.stock_name,
        asset_id: stockForm.value.asset_id,
        expected_spend: stockForm.value.expected_spend,
      })
      ElMessage.success('更新成功')
    }
    stockDialogVisible.value = false
    if (stocksAssetId.value) await fetchStocks(stocksAssetId.value)
  } finally {
    stockSubmitting.value = false
  }
}

async function handleDeleteStock(row: StockAsset) {
  const ok = await confirm({
    title: '刪除股票持有',
    message: `確定要刪除「${row.stock_name}」(${row.stock_code})?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteStock(row.stock_id)
  ElMessage.success('已刪除')
  stockDetailsByStock.delete(row.stock_id)
  if (stocksAssetId.value) await fetchStocks(stocksAssetId.value)
}

// ─── Stock journal (details) ────────────────────────────────────────────────
const stockDetailsByStock = shallowReactive(new Map<string, StockJournal[]>())
const stockDetailsLoadingByStock = shallowReactive(new Map<string, boolean>())

async function fetchStockDetails(stockId: string) {
  stockDetailsLoadingByStock.set(stockId, true)
  try {
    const details = await getStockDetails(stockId)
    stockDetailsByStock.set(stockId, details)
  } finally {
    stockDetailsLoadingByStock.set(stockId, false)
  }
}

function onStockExpandChange(row: StockAsset, expanded: StockAsset[]) {
  const isExpanded = expanded.some((r) => r.stock_id === row.stock_id)
  if (isExpanded && !stockDetailsByStock.has(row.stock_id)) {
    void fetchStockDetails(row.stock_id)
  }
}

interface StockDetailFormState extends StockJournalCreate {
  distinct_number?: number
}

const stockDetailDialogVisible = ref(false)
const stockDetailFormMode = ref<'create' | 'edit'>('create')
const stockDetailSubmitting = ref(false)
const stockDetailFormRef = ref<FormInstance>()

function emptyStockDetailForm(stockId: string): StockDetailFormState {
  return {
    stock_id: stockId,
    excute_type: 'buy',
    excute_amount: 0,
    excute_price: 0,
    excute_date: dayjs().format('YYYYMMDD'),
    account_id: '',
    account_name: '',
    memo: null,
  }
}

const stockDetailForm = ref<StockDetailFormState>(emptyStockDetailForm(''))

const stockDetailFormDate = computed<Date | null>({
  get: () =>
    stockDetailForm.value.excute_date
      ? dayjs(stockDetailForm.value.excute_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    stockDetailForm.value.excute_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const stockDetailFormRules: FormRules = {
  excute_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  excute_amount: [{ required: true, message: '請輸入數量', trigger: 'blur' }],
  excute_price: [{ required: true, message: '請輸入單價', trigger: 'blur' }],
  account_id: [{ required: true, message: '請輸入帳戶 ID', trigger: 'blur' }],
  account_name: [{ required: true, message: '請輸入帳戶名稱', trigger: 'blur' }],
}

function openCreateStockDetail(stock: StockAsset) {
  stockDetailFormMode.value = 'create'
  stockDetailForm.value = emptyStockDetailForm(stock.stock_id)
  stockDetailDialogVisible.value = true
}

function openEditStockDetail(stock: StockAsset, detail: StockJournal) {
  stockDetailFormMode.value = 'edit'
  stockDetailForm.value = {
    distinct_number: detail.distinct_number,
    stock_id: stock.stock_id,
    excute_type: detail.excute_type,
    excute_amount: detail.excute_amount,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    account_id: detail.account_id,
    account_name: detail.account_name,
    memo: detail.memo ?? null,
  }
  stockDetailDialogVisible.value = true
}

async function submitStockDetail() {
  if (!stockDetailFormRef.value) return
  const valid = await stockDetailFormRef.value.validate().catch(() => false)
  if (!valid) return
  stockDetailSubmitting.value = true
  try {
    const payload: StockJournalCreate = {
      stock_id: stockDetailForm.value.stock_id,
      excute_type: stockDetailForm.value.excute_type,
      excute_amount: Number(stockDetailForm.value.excute_amount ?? 0),
      excute_price: Number(stockDetailForm.value.excute_price ?? 0),
      excute_date: stockDetailForm.value.excute_date,
      account_id: stockDetailForm.value.account_id,
      account_name: stockDetailForm.value.account_name,
      memo: stockDetailForm.value.memo || null,
    }
    if (stockDetailFormMode.value === 'create') {
      await createStockDetail(stockDetailForm.value.stock_id, payload)
      ElMessage.success('新增成功')
    } else if (stockDetailForm.value.distinct_number !== undefined) {
      await updateStockDetail(stockDetailForm.value.distinct_number, payload)
      ElMessage.success('更新成功')
    }
    stockDetailDialogVisible.value = false
    await fetchStockDetails(stockDetailForm.value.stock_id)
  } finally {
    stockDetailSubmitting.value = false
  }
}

async function handleDeleteStockDetail(stock: StockAsset, detail: StockJournal) {
  const ok = await confirm({
    title: '刪除股票明細',
    message: `確定要刪除這筆 ${detail.excute_date} ${detail.excute_type} 紀錄?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteStockDetail(detail.distinct_number)
  ElMessage.success('已刪除')
  await fetchStockDetails(stock.stock_id)
}

// ─── Estates ────────────────────────────────────────────────────────────────
const estateCategoryOptions = computed(() =>
  [...store.otherAssets]
    .filter((a) => a.asset_type === 'estate' && a.in_use === 'Y')
    .sort((a, b) => a.asset_index - b.asset_index),
)

const estatesAssetId = ref<string>('')

watch(estateCategoryOptions, (options) => {
  if (!estatesAssetId.value && options.length > 0) {
    estatesAssetId.value = options[0]!.asset_id
  }
})

watch(estatesAssetId, (assetId) => {
  if (assetId) void store.fetchEstates(assetId)
})

function estateStatusVariant(status: string): 'success' | 'info' | 'warning' | 'danger' {
  switch (status) {
    case 'live':
      return 'success'
    case 'rent':
      return 'warning'
    case 'sold':
      return 'danger'
    default:
      return 'info'
  }
}

const estateDialogVisible = ref(false)
const estateFormMode = ref<'create' | 'edit'>('create')
const estateSubmitting = ref(false)
const estateFormRef = ref<FormInstance>()

function emptyEstateForm(): EstateAssetCreate {
  return {
    estate_id: '',
    estate_name: '',
    estate_type: '',
    estate_address: '',
    asset_id: estatesAssetId.value,
    obtain_date: dayjs().format('YYYYMMDD'),
    loan_id: null,
    estate_status: 'live',
    memo: null,
  }
}

const estateForm = ref<EstateAssetCreate>(emptyEstateForm())

const estateLoanIdProxy = computed<string>({
  get: () => estateForm.value.loan_id ?? '',
  set: (v) => {
    estateForm.value.loan_id = v.trim() ? v.trim() : null
  },
})

const estateMemoProxy = computed<string>({
  get: () => estateForm.value.memo ?? '',
  set: (v) => {
    estateForm.value.memo = v ? v : null
  },
})

const estateFormObtainDate = computed<Date | null>({
  get: () =>
    estateForm.value.obtain_date
      ? dayjs(estateForm.value.obtain_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    estateForm.value.obtain_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const estateFormRules: FormRules = {
  estate_id: [{ required: true, message: '請輸入房產 ID', trigger: 'blur' }],
  estate_name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
  estate_type: [{ required: true, message: '請輸入類型', trigger: 'blur' }],
  estate_address: [{ required: true, message: '請輸入地址', trigger: 'blur' }],
  obtain_date: [{ required: true, message: '請選擇取得日期', trigger: 'change' }],
  estate_status: [{ required: true, message: '請選擇狀態', trigger: 'change' }],
}

function openCreateEstate() {
  estateFormMode.value = 'create'
  estateForm.value = emptyEstateForm()
  estateDialogVisible.value = true
}

function openEditEstate(row: EstateAsset) {
  estateFormMode.value = 'edit'
  estateForm.value = {
    estate_id: row.estate_id,
    estate_name: row.estate_name,
    estate_type: row.estate_type,
    estate_address: row.estate_address,
    asset_id: row.asset_id,
    obtain_date: row.obtain_date,
    loan_id: row.loan_id ?? null,
    estate_status: row.estate_status,
    memo: row.memo ?? null,
  }
  estateDialogVisible.value = true
}

async function submitEstate() {
  if (!estateFormRef.value) return
  const valid = await estateFormRef.value.validate().catch(() => false)
  if (!valid) return
  estateSubmitting.value = true
  try {
    if (estateFormMode.value === 'create') {
      await createEstate({ ...estateForm.value })
      ElMessage.success('新增成功')
    } else {
      await updateEstate(estateForm.value.estate_id, {
        estate_name: estateForm.value.estate_name,
        estate_type: estateForm.value.estate_type,
        estate_address: estateForm.value.estate_address,
        asset_id: estateForm.value.asset_id,
        obtain_date: estateForm.value.obtain_date,
        loan_id: estateForm.value.loan_id ?? null,
        estate_status: estateForm.value.estate_status,
        memo: estateForm.value.memo ?? null,
      })
      ElMessage.success('更新成功')
    }
    estateDialogVisible.value = false
    if (estatesAssetId.value) await store.fetchEstates(estatesAssetId.value)
  } finally {
    estateSubmitting.value = false
  }
}

async function handleDeleteEstate(row: EstateAsset) {
  const ok = await confirm({
    title: '刪除房產',
    message: `確定要刪除「${row.estate_name}」?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteEstate(row.estate_id)
  ElMessage.success('已刪除')
  estateDetailsByEstate.delete(row.estate_id)
  if (estatesAssetId.value) await store.fetchEstates(estatesAssetId.value)
}

const estateDetailsByEstate = shallowReactive(new Map<string, EstateJournal[]>())
const estateDetailsLoadingByEstate = shallowReactive(new Map<string, boolean>())

async function fetchEstateDetails(estateId: string) {
  estateDetailsLoadingByEstate.set(estateId, true)
  try {
    const details = await getEstateDetails(estateId)
    estateDetailsByEstate.set(estateId, details)
  } finally {
    estateDetailsLoadingByEstate.set(estateId, false)
  }
}

function onEstateExpandChange(row: EstateAsset, expanded: EstateAsset[]) {
  const isExpanded = expanded.some((r) => r.estate_id === row.estate_id)
  if (isExpanded && !estateDetailsByEstate.has(row.estate_id)) {
    void fetchEstateDetails(row.estate_id)
  }
}

interface EstateDetailFormState extends EstateJournalCreate {
  distinct_number?: number
}

const estateDetailDialogVisible = ref(false)
const estateDetailFormMode = ref<'create' | 'edit'>('create')
const estateDetailSubmitting = ref(false)
const estateDetailFormRef = ref<FormInstance>()

function emptyEstateDetailForm(estateId: string): EstateDetailFormState {
  return {
    estate_id: estateId,
    estate_excute_type: 'tax',
    excute_price: 0,
    excute_date: dayjs().format('YYYYMMDD'),
    memo: null,
  }
}

const estateDetailForm = ref<EstateDetailFormState>(emptyEstateDetailForm(''))

const estateDetailMemoProxy = computed<string>({
  get: () => estateDetailForm.value.memo ?? '',
  set: (v) => {
    estateDetailForm.value.memo = v ? v : null
  },
})

const estateDetailFormDate = computed<Date | null>({
  get: () =>
    estateDetailForm.value.excute_date
      ? dayjs(estateDetailForm.value.excute_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    estateDetailForm.value.excute_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const estateDetailFormRules: FormRules = {
  excute_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  estate_excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  excute_price: [{ required: true, message: '請輸入金額', trigger: 'blur' }],
}

function openCreateEstateDetail(estate: EstateAsset) {
  estateDetailFormMode.value = 'create'
  estateDetailForm.value = emptyEstateDetailForm(estate.estate_id)
  estateDetailDialogVisible.value = true
}

function openEditEstateDetail(estate: EstateAsset, detail: EstateJournal) {
  estateDetailFormMode.value = 'edit'
  estateDetailForm.value = {
    distinct_number: detail.distinct_number,
    estate_id: estate.estate_id,
    estate_excute_type: detail.estate_excute_type,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    memo: detail.memo ?? null,
  }
  estateDetailDialogVisible.value = true
}

async function submitEstateDetail() {
  if (!estateDetailFormRef.value) return
  const valid = await estateDetailFormRef.value.validate().catch(() => false)
  if (!valid) return
  estateDetailSubmitting.value = true
  try {
    const payload: EstateJournalCreate = {
      estate_id: estateDetailForm.value.estate_id,
      estate_excute_type: estateDetailForm.value.estate_excute_type,
      excute_price: Number(estateDetailForm.value.excute_price ?? 0),
      excute_date: estateDetailForm.value.excute_date,
      memo: estateDetailForm.value.memo ?? null,
    }
    if (estateDetailFormMode.value === 'create') {
      await createEstateDetail(estateDetailForm.value.estate_id, payload)
      ElMessage.success('新增成功')
    } else if (estateDetailForm.value.distinct_number !== undefined) {
      await updateEstateDetail(estateDetailForm.value.distinct_number, payload)
      ElMessage.success('更新成功')
    }
    estateDetailDialogVisible.value = false
    await fetchEstateDetails(estateDetailForm.value.estate_id)
  } finally {
    estateDetailSubmitting.value = false
  }
}

async function handleDeleteEstateDetail(estate: EstateAsset, detail: EstateJournal) {
  const ok = await confirm({
    title: '刪除房產明細',
    message: `確定要刪除這筆 ${detail.excute_date} ${detail.estate_excute_type} 紀錄?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteEstateDetail(detail.distinct_number)
  ElMessage.success('已刪除')
  await fetchEstateDetails(estate.estate_id)
}

// ─── Insurances ─────────────────────────────────────────────────────────────
const insuranceCategoryOptions = computed(() =>
  [...store.otherAssets]
    .filter((a) => a.asset_type === 'insurance' && a.in_use === 'Y')
    .sort((a, b) => a.asset_index - b.asset_index),
)

const insurancesAssetId = ref<string>('')

watch(insuranceCategoryOptions, (options) => {
  if (!insurancesAssetId.value && options.length > 0) {
    insurancesAssetId.value = options[0]!.asset_id
  }
})

watch(insurancesAssetId, (assetId) => {
  if (assetId) void store.fetchInsurances(assetId)
})

const insuranceDialogVisible = ref(false)
const insuranceFormMode = ref<'create' | 'edit'>('create')
const insuranceSubmitting = ref(false)
const insuranceFormRef = ref<FormInstance>()

function emptyInsuranceForm(): InsuranceAssetCreate {
  return {
    insurance_id: '',
    insurance_name: '',
    asset_id: insurancesAssetId.value,
    in_account: '',
    out_account: '',
    start_date: dayjs().format('YYYYMMDD'),
    end_date: dayjs().add(1, 'year').format('YYYYMMDD'),
    pay_type: 'annual',
    pay_day: 1,
    expected_spend: 0,
    has_closed: 'N',
  }
}

const insuranceForm = ref<InsuranceAssetCreate>(emptyInsuranceForm())

const insuranceFormStartDate = computed<Date | null>({
  get: () =>
    insuranceForm.value.start_date
      ? dayjs(insuranceForm.value.start_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    insuranceForm.value.start_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const insuranceFormEndDate = computed<Date | null>({
  get: () =>
    insuranceForm.value.end_date
      ? dayjs(insuranceForm.value.end_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    insuranceForm.value.end_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const insuranceFormRules: FormRules = {
  insurance_id: [{ required: true, message: '請輸入保險 ID', trigger: 'blur' }],
  insurance_name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
  in_account: [{ required: true, message: '請輸入繳費帳戶', trigger: 'blur' }],
  out_account: [{ required: true, message: '請輸入領取帳戶', trigger: 'blur' }],
  start_date: [{ required: true, message: '請選擇起始日', trigger: 'change' }],
  end_date: [{ required: true, message: '請選擇終止日', trigger: 'change' }],
  pay_type: [{ required: true, message: '請輸入繳費頻率', trigger: 'blur' }],
  pay_day: [{ required: true, message: '請輸入繳款日', trigger: 'blur' }],
  expected_spend: [{ required: true, message: '請輸入預計保費', trigger: 'blur' }],
  has_closed: [{ required: true, message: '請選擇結案狀態', trigger: 'change' }],
}

function openCreateInsurance() {
  insuranceFormMode.value = 'create'
  insuranceForm.value = emptyInsuranceForm()
  insuranceDialogVisible.value = true
}

function openEditInsurance(row: InsuranceAsset) {
  insuranceFormMode.value = 'edit'
  insuranceForm.value = {
    insurance_id: row.insurance_id,
    insurance_name: row.insurance_name,
    asset_id: row.asset_id,
    in_account: row.in_account,
    out_account: row.out_account,
    start_date: row.start_date,
    end_date: row.end_date,
    pay_type: row.pay_type,
    pay_day: row.pay_day,
    expected_spend: row.expected_spend,
    has_closed: row.has_closed,
  }
  insuranceDialogVisible.value = true
}

async function submitInsurance() {
  if (!insuranceFormRef.value) return
  const valid = await insuranceFormRef.value.validate().catch(() => false)
  if (!valid) return
  insuranceSubmitting.value = true
  try {
    if (insuranceFormMode.value === 'create') {
      await createInsurance({ ...insuranceForm.value })
      ElMessage.success('新增成功')
    } else {
      const { insurance_id, ...rest } = insuranceForm.value
      await updateInsurance(insurance_id, rest)
      ElMessage.success('更新成功')
    }
    insuranceDialogVisible.value = false
    if (insurancesAssetId.value) await store.fetchInsurances(insurancesAssetId.value)
  } finally {
    insuranceSubmitting.value = false
  }
}

async function handleDeleteInsurance(row: InsuranceAsset) {
  const ok = await confirm({
    title: '刪除保險合約',
    message: `確定要刪除「${row.insurance_name}」?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteInsurance(row.insurance_id)
  ElMessage.success('已刪除')
  insuranceDetailsByPolicy.delete(row.insurance_id)
  if (insurancesAssetId.value) await store.fetchInsurances(insurancesAssetId.value)
}

const insuranceDetailsByPolicy = shallowReactive(new Map<string, InsuranceJournal[]>())
const insuranceDetailsLoadingByPolicy = shallowReactive(new Map<string, boolean>())

async function fetchInsuranceDetails(insuranceId: string) {
  insuranceDetailsLoadingByPolicy.set(insuranceId, true)
  try {
    const details = await getInsuranceDetails(insuranceId)
    insuranceDetailsByPolicy.set(insuranceId, details)
  } finally {
    insuranceDetailsLoadingByPolicy.set(insuranceId, false)
  }
}

function onInsuranceExpandChange(row: InsuranceAsset, expanded: InsuranceAsset[]) {
  const isExpanded = expanded.some((r) => r.insurance_id === row.insurance_id)
  if (isExpanded && !insuranceDetailsByPolicy.has(row.insurance_id)) {
    void fetchInsuranceDetails(row.insurance_id)
  }
}

interface InsuranceDetailFormState extends InsuranceJournalCreate {
  distinct_number?: number
}

const insuranceDetailDialogVisible = ref(false)
const insuranceDetailFormMode = ref<'create' | 'edit'>('create')
const insuranceDetailSubmitting = ref(false)
const insuranceDetailFormRef = ref<FormInstance>()

function emptyInsuranceDetailForm(insuranceId: string): InsuranceDetailFormState {
  return {
    insurance_id: insuranceId,
    insurance_excute_type: 'pay',
    excute_price: 0,
    excute_date: dayjs().format('YYYYMMDD'),
    memo: null,
  }
}

const insuranceDetailForm = ref<InsuranceDetailFormState>(emptyInsuranceDetailForm(''))

const insuranceDetailMemoProxy = computed<string>({
  get: () => insuranceDetailForm.value.memo ?? '',
  set: (v) => {
    insuranceDetailForm.value.memo = v ? v : null
  },
})

const insuranceDetailFormDate = computed<Date | null>({
  get: () =>
    insuranceDetailForm.value.excute_date
      ? dayjs(insuranceDetailForm.value.excute_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    insuranceDetailForm.value.excute_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const insuranceDetailFormRules: FormRules = {
  excute_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  insurance_excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  excute_price: [{ required: true, message: '請輸入金額', trigger: 'blur' }],
}

function openCreateInsuranceDetail(insurance: InsuranceAsset) {
  insuranceDetailFormMode.value = 'create'
  insuranceDetailForm.value = emptyInsuranceDetailForm(insurance.insurance_id)
  insuranceDetailDialogVisible.value = true
}

function openEditInsuranceDetail(insurance: InsuranceAsset, detail: InsuranceJournal) {
  insuranceDetailFormMode.value = 'edit'
  insuranceDetailForm.value = {
    distinct_number: detail.distinct_number,
    insurance_id: insurance.insurance_id,
    insurance_excute_type: detail.insurance_excute_type,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    memo: detail.memo ?? null,
  }
  insuranceDetailDialogVisible.value = true
}

async function submitInsuranceDetail() {
  if (!insuranceDetailFormRef.value) return
  const valid = await insuranceDetailFormRef.value.validate().catch(() => false)
  if (!valid) return
  insuranceDetailSubmitting.value = true
  try {
    const payload: InsuranceJournalCreate = {
      insurance_id: insuranceDetailForm.value.insurance_id,
      insurance_excute_type: insuranceDetailForm.value.insurance_excute_type,
      excute_price: Number(insuranceDetailForm.value.excute_price ?? 0),
      excute_date: insuranceDetailForm.value.excute_date,
      memo: insuranceDetailForm.value.memo ?? null,
    }
    if (insuranceDetailFormMode.value === 'create') {
      await createInsuranceDetail(insuranceDetailForm.value.insurance_id, payload)
      ElMessage.success('新增成功')
    } else if (insuranceDetailForm.value.distinct_number !== undefined) {
      await updateInsuranceDetail(insuranceDetailForm.value.distinct_number, payload)
      ElMessage.success('更新成功')
    }
    insuranceDetailDialogVisible.value = false
    await fetchInsuranceDetails(insuranceDetailForm.value.insurance_id)
  } finally {
    insuranceDetailSubmitting.value = false
  }
}

async function handleDeleteInsuranceDetail(insurance: InsuranceAsset, detail: InsuranceJournal) {
  const ok = await confirm({
    title: '刪除繳費明細',
    message: `確定要刪除這筆 ${detail.excute_date} ${detail.insurance_excute_type} 紀錄?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteInsuranceDetail(detail.distinct_number)
  ElMessage.success('已刪除')
  await fetchInsuranceDetails(insurance.insurance_id)
}

// ─── Loans ──────────────────────────────────────────────────────────────────
const loanDialogVisible = ref(false)
const loanFormMode = ref<'create' | 'edit'>('create')
const loanSubmitting = ref(false)
const loanFormRef = ref<FormInstance>()

function emptyLoanForm(): LoanAssetCreate {
  return {
    loan_id: '',
    loan_name: '',
    loan_type: '',
    account_id: '',
    account_name: '',
    interest_rate: 0,
    period: 12,
    apply_date: dayjs().format('YYYYMMDD'),
    grace_expire_date: null,
    pay_day: 1,
    amount: 0,
    repayed: 0,
    loan_index: 0,
  }
}

const loanForm = ref<LoanAssetCreate>(emptyLoanForm())

const loanFormApplyDate = computed<Date | null>({
  get: () =>
    loanForm.value.apply_date ? dayjs(loanForm.value.apply_date, 'YYYYMMDD').toDate() : null,
  set: (date) => {
    loanForm.value.apply_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const loanFormGraceDate = computed<Date | null>({
  get: () =>
    loanForm.value.grace_expire_date
      ? dayjs(loanForm.value.grace_expire_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    loanForm.value.grace_expire_date = date ? dayjs(date).format('YYYYMMDD') : null
  },
})

const loanFormRules: FormRules = {
  loan_id: [{ required: true, message: '請輸入貸款 ID', trigger: 'blur' }],
  loan_name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
  loan_type: [{ required: true, message: '請輸入類型', trigger: 'blur' }],
  account_id: [{ required: true, message: '請輸入帳戶 ID', trigger: 'blur' }],
  account_name: [{ required: true, message: '請輸入帳戶名稱', trigger: 'blur' }],
  interest_rate: [{ required: true, message: '請輸入年利率', trigger: 'blur' }],
  period: [{ required: true, message: '請輸入期數', trigger: 'blur' }],
  apply_date: [{ required: true, message: '請選擇申貸日', trigger: 'change' }],
  pay_day: [{ required: true, message: '請輸入繳款日', trigger: 'blur' }],
  amount: [{ required: true, message: '請輸入本金', trigger: 'blur' }],
  repayed: [{ required: true, message: '請輸入已還本金', trigger: 'blur' }],
  loan_index: [{ required: true, message: '請輸入排序', trigger: 'blur' }],
}

function openCreateLoan() {
  loanFormMode.value = 'create'
  loanForm.value = emptyLoanForm()
  loanDialogVisible.value = true
}

function openEditLoan(row: LoanAsset) {
  loanFormMode.value = 'edit'
  loanForm.value = {
    loan_id: row.loan_id,
    loan_name: row.loan_name,
    loan_type: row.loan_type,
    account_id: row.account_id,
    account_name: row.account_name,
    interest_rate: row.interest_rate,
    period: row.period,
    apply_date: row.apply_date,
    grace_expire_date: row.grace_expire_date ?? null,
    pay_day: row.pay_day,
    amount: row.amount,
    repayed: row.repayed,
    loan_index: row.loan_index,
  }
  loanDialogVisible.value = true
}

async function submitLoan() {
  if (!loanFormRef.value) return
  const valid = await loanFormRef.value.validate().catch(() => false)
  if (!valid) return
  loanSubmitting.value = true
  try {
    if (loanFormMode.value === 'create') {
      await createLoan({ ...loanForm.value })
      ElMessage.success('新增成功')
    } else {
      const { loan_id, ...rest } = loanForm.value
      await updateLoan(loan_id, rest)
      ElMessage.success('更新成功')
    }
    loanDialogVisible.value = false
    await store.fetchLoans()
  } finally {
    loanSubmitting.value = false
  }
}

async function handleDeleteLoan(row: LoanAsset) {
  const ok = await confirm({
    title: '刪除貸款',
    message: `確定要刪除「${row.loan_name}」?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteLoan(row.loan_id)
  ElMessage.success('已刪除')
  loanDetailsByLoan.delete(row.loan_id)
  await store.fetchLoans()
}

const loanDetailsByLoan = shallowReactive(new Map<string, LoanJournal[]>())
const loanDetailsLoadingByLoan = shallowReactive(new Map<string, boolean>())

async function fetchLoanDetails(loanId: string) {
  loanDetailsLoadingByLoan.set(loanId, true)
  try {
    const details = await getLoanDetails(loanId)
    loanDetailsByLoan.set(loanId, details)
  } finally {
    loanDetailsLoadingByLoan.set(loanId, false)
  }
}

function onLoanExpandChange(row: LoanAsset, expanded: LoanAsset[]) {
  const isExpanded = expanded.some((r) => r.loan_id === row.loan_id)
  if (isExpanded && !loanDetailsByLoan.has(row.loan_id)) {
    void fetchLoanDetails(row.loan_id)
  }
}

interface LoanDetailFormState extends LoanJournalCreate {
  distinct_number?: number
}

const loanDetailDialogVisible = ref(false)
const loanDetailFormMode = ref<'create' | 'edit'>('create')
const loanDetailSubmitting = ref(false)
const loanDetailFormRef = ref<FormInstance>()

function emptyLoanDetailForm(loanId: string): LoanDetailFormState {
  return {
    loan_id: loanId,
    loan_excute_type: 'principal',
    excute_price: 0,
    excute_date: dayjs().format('YYYYMMDD'),
    memo: null,
  }
}

const loanDetailForm = ref<LoanDetailFormState>(emptyLoanDetailForm(''))

const loanDetailMemoProxy = computed<string>({
  get: () => loanDetailForm.value.memo ?? '',
  set: (v) => {
    loanDetailForm.value.memo = v ? v : null
  },
})

const loanDetailFormDate = computed<Date | null>({
  get: () =>
    loanDetailForm.value.excute_date
      ? dayjs(loanDetailForm.value.excute_date, 'YYYYMMDD').toDate()
      : null,
  set: (date) => {
    loanDetailForm.value.excute_date = date ? dayjs(date).format('YYYYMMDD') : ''
  },
})

const loanDetailFormRules: FormRules = {
  excute_date: [{ required: true, message: '請選擇日期', trigger: 'change' }],
  loan_excute_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  excute_price: [{ required: true, message: '請輸入金額', trigger: 'blur' }],
}

function openCreateLoanDetail(loan: LoanAsset) {
  loanDetailFormMode.value = 'create'
  loanDetailForm.value = emptyLoanDetailForm(loan.loan_id)
  loanDetailDialogVisible.value = true
}

function openEditLoanDetail(loan: LoanAsset, detail: LoanJournal) {
  loanDetailFormMode.value = 'edit'
  loanDetailForm.value = {
    distinct_number: detail.distinct_number,
    loan_id: loan.loan_id,
    loan_excute_type: detail.loan_excute_type,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    memo: detail.memo ?? null,
  }
  loanDetailDialogVisible.value = true
}

async function submitLoanDetail() {
  if (!loanDetailFormRef.value) return
  const valid = await loanDetailFormRef.value.validate().catch(() => false)
  if (!valid) return
  loanDetailSubmitting.value = true
  try {
    const payload: LoanJournalCreate = {
      loan_id: loanDetailForm.value.loan_id,
      loan_excute_type: loanDetailForm.value.loan_excute_type,
      excute_price: Number(loanDetailForm.value.excute_price ?? 0),
      excute_date: loanDetailForm.value.excute_date,
      memo: loanDetailForm.value.memo ?? null,
    }
    if (loanDetailFormMode.value === 'create') {
      await createLoanDetail(loanDetailForm.value.loan_id, payload)
      ElMessage.success('新增成功')
    } else if (loanDetailForm.value.distinct_number !== undefined) {
      await updateLoanDetail(loanDetailForm.value.distinct_number, payload)
      ElMessage.success('更新成功')
    }
    loanDetailDialogVisible.value = false
    await fetchLoanDetails(loanDetailForm.value.loan_id)
  } finally {
    loanDetailSubmitting.value = false
  }
}

async function handleDeleteLoanDetail(loan: LoanAsset, detail: LoanJournal) {
  const ok = await confirm({
    title: '刪除還款明細',
    message: `確定要刪除這筆 ${detail.excute_date} ${detail.loan_excute_type} 紀錄?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteLoanDetail(detail.distinct_number)
  ElMessage.success('已刪除')
  await fetchLoanDetails(loan.loan_id)
}

// ─── Other-Assets ───────────────────────────────────────────────────────────
const otherAssetsSorted = computed(() =>
  [...store.otherAssets].sort((a, b) => a.asset_index - b.asset_index),
)

const otherAssetDialogVisible = ref(false)
const otherAssetFormMode = ref<'create' | 'edit'>('create')
const otherAssetSubmitting = ref(false)
const otherAssetFormRef = ref<FormInstance>()

function emptyOtherAssetForm(): OtherAssetCreate {
  return {
    asset_id: '',
    asset_name: '',
    asset_type: 'stock',
    vesting_nation: '',
    in_use: 'Y',
    asset_index: undefined,
  }
}

const otherAssetForm = ref<OtherAssetCreate>(emptyOtherAssetForm())

const otherAssetIndexProxy = computed<number | undefined>({
  get: () => otherAssetForm.value.asset_index,
  set: (v) => {
    otherAssetForm.value.asset_index = typeof v === 'number' ? v : undefined
  },
})

const otherAssetFormRules: FormRules = {
  asset_id: [{ required: true, message: '請輸入 ID', trigger: 'blur' }],
  asset_name: [{ required: true, message: '請輸入名稱', trigger: 'blur' }],
  asset_type: [{ required: true, message: '請選擇類型', trigger: 'change' }],
  vesting_nation: [{ required: true, message: '請輸入歸屬地', trigger: 'blur' }],
  in_use: [{ required: true, message: '請選擇啟用狀態', trigger: 'change' }],
}

function openCreateOtherAsset() {
  otherAssetFormMode.value = 'create'
  otherAssetForm.value = emptyOtherAssetForm()
  otherAssetDialogVisible.value = true
}

function openEditOtherAsset(row: OtherAsset) {
  otherAssetFormMode.value = 'edit'
  otherAssetForm.value = {
    asset_id: row.asset_id,
    asset_name: row.asset_name,
    asset_type: row.asset_type,
    vesting_nation: row.vesting_nation,
    in_use: row.in_use,
    asset_index: row.asset_index,
  }
  otherAssetDialogVisible.value = true
}

async function submitOtherAsset() {
  if (!otherAssetFormRef.value) return
  const valid = await otherAssetFormRef.value.validate().catch(() => false)
  if (!valid) return
  otherAssetSubmitting.value = true
  try {
    if (otherAssetFormMode.value === 'create') {
      await createOtherAsset({ ...otherAssetForm.value })
      ElMessage.success('新增成功')
    } else {
      const { asset_id, ...rest } = otherAssetForm.value
      await updateOtherAsset(asset_id, rest)
      ElMessage.success('更新成功')
    }
    otherAssetDialogVisible.value = false
    await store.fetchOtherAssets()
  } finally {
    otherAssetSubmitting.value = false
  }
}

async function handleDeleteOtherAsset(row: OtherAsset) {
  const ok = await confirm({
    title: '刪除資產分類',
    message: `確定要刪除「${row.asset_name}」(${row.asset_id})?`,
    type: 'warning',
  })
  if (!ok) return
  await deleteOtherAsset(row.asset_id)
  ElMessage.success('已刪除')
  await store.fetchOtherAssets()
}

// ─── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  void store.fetchOtherAssets()
  void store.fetchLoans()
})
</script>
