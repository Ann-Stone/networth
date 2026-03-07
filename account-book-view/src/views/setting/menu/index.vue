<template>
  <el-tabs v-model="activeTab" class="page">
    <el-tab-pane label="流水帳項目" name="cashFlow">
      <cashFlow-component />
    </el-tab-pane>
    <el-tab-pane label="帳戶" name="account" lazy>
      <account-component />
    </el-tab-pane>
    <el-tab-pane label="信用卡" name="creditCard" lazy>
      <credit-card-component />
    </el-tab-pane>
    <el-tab-pane label="非現金資產" name="asset" lazy>
      <other-asset-component />
    </el-tab-pane>
    <!-- <el-tab-pane
      label="貸款"
      name="loan"
      lazy
    >
      <loan-component />
    </el-tab-pane> -->
  </el-tabs>
</template>

<script>
import AccountComponent from './account/index'
import CashFlowComponent from './cashflow/index'
import CreditCardComponent from './creditCard/index'
import LoanComponent from './loan/index'
import OtherAssetComponent from './otherAssets/index'

export default {
  name: 'MenuSetting',
  components: {
    AccountComponent,
    CashFlowComponent,
    CreditCardComponent,
    LoanComponent,
    OtherAssetComponent
  },
  data() {
    return {
      activeTab: 'cashFlow'
    }
  }
}
</script>

