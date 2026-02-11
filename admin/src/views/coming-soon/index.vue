<template>
  <div class="coming-soon-container">
    <div class="content">
      <i class="el-icon-time icon" />
      <h2>敬请期待</h2>
      <p>该功能正在开发中，请耐心等待...</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ComingSoon'
}
</script>

<style scoped>
.coming-soon-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 120px);
}
.content {
  text-align: center;
  color: #909399;
}
.icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: #c0c4cc;
}
h2 {
  font-size: 24px;
  margin-bottom: 12px;
  color: #606266;
}
p {
  font-size: 14px;
}
</style>
