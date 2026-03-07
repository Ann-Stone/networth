<template>
  <el-card class="box-card-component" style="margin-left: 8px">
    <div style="position: relative">
      <mallki class-name="mallki-text" text="贈與額度使用率" />
      <div v-for="item in giftedList" :key="item.owner" class="progress-item">
        <span>{{ item.owner }}</span>
        <el-progress :percentage="item.rate" class="progress-bar" />
        <span>{{ item.amount }}</span>
      </div>
    </div>
  </el-card>
</template>

<script>
import Mallki from '@/components/TextHoverEffect/Mallki'

export default {
  components: { Mallki },
  props: {
    year: { type: String, default: new Date().getFullYear().toString() }
  },
  data() {
    return {
      giftedList: []
    }
  },
  watch: {
    year: {
      immediate: true,
      handler(newValue) {
        this.$store.dispatch('GetGiftedList', newValue).then((response) => {
          this.giftedList = response.data
        })
      }
    }
  }
}
</script>

<style rel="stylesheet/scss" lang="scss" >
.box-card-component {
  .el-card__header {
    padding: 0px !important;
  }
}
</style>
<style rel="stylesheet/scss" lang="scss" scoped>
.box-card-component {
  .box-card-header {
    position: relative;
    height: 220px;
  }

  .mallki-text {
    margin-bottom: 35px;
  }

  .progress-item {
    margin-bottom: 10px;
    font-size: 14px;
    display: flex;

    span {
      min-width: 100px;

      &:last-child {
        text-align: right;
      }
    }

    .progress-bar {
      width: 50%;
    }
  }

  @media only screen and (max-width: 1510px) {
    .mallki-text {
      display: none;
    }
  }
}
</style>
