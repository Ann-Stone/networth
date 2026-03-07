<template>
  <el-row :gutter="40" class="panel-group">
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel">
        <div class="card-panel-icon-wrapper icon-used">
          <svg-icon icon-class="chart" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">預算使用率</div>
          <span class="card-panel-num"
          >{{ summaryObj.spending }} / {{ budget }} =
            {{ ((summaryObj.spending / budget) * 100).toFixed(2) }}%</span
            >
            <!-- <count-to
            :start-val="0"
            :end-val="102400"
            :duration="2600"
            class="card-panel-num"
          /> -->
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel">
        <div class="card-panel-icon-wrapper icon-freedom">
          <svg-icon icon-class="guide" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">財務自由度(淨值/每月或年支出)</div>
          <count-to
            :start-val="0"
            :end-val="summaryObj.freedom"
            :duration="3600"
            :decimals="2"
            class="card-panel-num"
          />
          %
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel">
        <div class="card-panel-icon-wrapper icon-work-freedom">
          <svg-icon icon-class="guide" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">工作自由度(所有被動收入/所有收入)</div>
          <count-to
            :start-val="0"
            :end-val="summaryObj.workFreedom"
            :duration="3000"
            :decimals="2"
            class="card-panel-num"
          />
          %
        </div>
      </div>
    </el-col>
    <el-col :xs="12" :sm="12" :lg="6" class="card-panel-col">
      <div class="card-panel">
        <div class="card-panel-icon-wrapper icon-return-rate">
          <svg-icon icon-class="money" class-name="card-panel-icon" />
        </div>
        <div class="card-panel-description">
          <div class="card-panel-text">淨資產成長率</div>
          <count-to
            :start-val="0"
            :end-val="summaryObj.netAssetGrowth"
            :duration="3200"
            :decimals="2"
            class="card-panel-num"
          />
          %
        </div>
      </div>
    </el-col>
  </el-row>
</template>

<script>
import CountTo from 'vue-count-to'

export default {
  components: {
    CountTo
  },
  props: {
    period: {
      type: String,
      default: null
    },
    periodType: {
      type: String,
      default: null
    },
    summaryObj: {
      type: Object,
      default: null
    }
  },
  data() {
    return {
      budget: 0
    }
  },
  watch: {
    period: {
      immediate: true,
      handler(newValue) {
        this.$store
          .dispatch('GetBudgetUsed', {
            type: this.periodType,
            dateValue: newValue
          })
          .then(response => {
            this.budget = response.data
          })
      }
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" scoped>
.panel-group {
  margin-top: 10px;

  .card-panel-col {
    margin-bottom: 20px;
  }

  .card-panel {
    height: 108px;
    cursor: pointer;
    font-size: 12px;
    position: relative;
    overflow: hidden;
    color: #666;
    background: #fff;
    box-shadow: 4px 4px 40px rgba(0, 0, 0, 0.05);
    border-color: rgba(0, 0, 0, 0.05);
    &:hover {
      .card-panel-icon-wrapper {
        color: #fff;
      }
      .icon-used {
        background: #f4516c;
      }
      .icon-work-freedom {
        background: #36a3f7;
      }
      .icon-return-rate {
        background: #40c9c6;
      }
      .icon-freedom {
        background: #34bfa3;
      }
    }
    .icon-used {
      color: #f4516c;
    }
    .icon-work-freedom {
      color: #36a3f7;
    }
    .icon-return-rate {
      color: #40c9c6;
    }
    .icon-freedom {
      color: #34bfa3;
    }
    .card-panel-icon-wrapper {
      float: left;
      margin: 14px 0 0 14px;
      padding: 16px;
      transition: all 0.38s ease-out;
      border-radius: 6px;
    }
    .card-panel-icon {
      float: left;
      font-size: 48px;
    }
    .card-panel-description {
      float: right;
      font-weight: bold;
      margin: 26px;
      margin-left: 0px;
      .card-panel-text {
        line-height: 18px;
        color: rgba(0, 0, 0, 0.45);
        font-size: 16px;
        margin-bottom: 12px;
      }
      .card-panel-num {
        font-size: 20px;
      }
    }
  }
}
</style>
