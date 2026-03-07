<template>
  <div class="search-area base">
    <span
      class="title"
      @click="isShowArea = !isShowArea"
    >&nbsp;搜尋區塊 (按一下縮放)&nbsp;</span>
    <div v-show="isShowArea">
      <slot name="content" />
    </div>
  </div>
</template>

<script>
export default {
  name: 'SearchArea',
  data() {
    return {
      isShowArea: true
    }
  }
}
</script>

<style lang="scss" scoped>
.search-area {
  position: relative;

  &.base {
    width: 100%;
    border: 3px solid #d8dce5;
    border-radius: 6px;
    padding: 20px 10px 15px 10px;
  }

  .title {
    position: absolute;
    top: -12px;
    background-color: #ffffff;
    color: #c3c7cf;
    cursor: pointer;
  }
}
</style>
