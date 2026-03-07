<template>
  <el-tabs v-model="activeTab" class="page">
    <el-tab-pane label="貸款" name="貸款" lazy>
      <Liability />
    </el-tab-pane>
    <el-tab-pane
      v-for="(item, index) in itemList"
      :key="index"
      :label="item.asset_name"
      :name="item.asset_name"
      lazy
    >
      <component
        v-if="activeTab === item.asset_name"
        :is="getComponentName(item.asset_type)"
        :asset-id="item.asset_id"
      />
    </el-tab-pane>
  </el-tabs>
</template>

<script>
import { mapState } from 'vuex'

import EstateContent from './Estate/index'
import InsurenceContent from './Insurance/index'
import Liability from './Liability/index'
import StockContent from './Stock/index'

export default {
  name: 'OtherAssetsDetail',
  components: { EstateContent, InsurenceContent, Liability, StockContent },
  data() {
    return {
      activeTab: '貸款'
    }
  },
  computed: {
    ...mapState({
      itemList: (state) => state.otherAssets.otherAssets.itemList
    })
  },
  created() {
    this.$store.dispatch('GetOtherAssetItems')
  },
  methods: {
    getComponentName(type) {
      switch (type) {
        case 'Stock':
          return 'StockContent'
        case 'Insurance':
          return 'InsurenceContent'
        case 'Estate':
          return 'EstateContent'
      }
    }
  }
}
</script>
