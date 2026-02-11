<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-left" @click="router.push('/')">
        <el-icon :size="24"><Reading /></el-icon>
        <span class="app-title">AI 知识库</span>
      </div>
      <el-menu
        mode="horizontal"
        :router="true"
        :default-active="$route.path"
        class="header-menu"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/posts">文章</el-menu-item>
        <el-menu-item index="/chat">AI 对话</el-menu-item>
      </el-menu>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
</template>

<style scoped>
.app-container {
  min-height: 100vh;
}

.app-header {
  display: flex;
  align-items: center;
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-right: 40px;
  flex-shrink: 0;
}

.app-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--el-color-primary);
  white-space: nowrap;
}

.header-menu {
  border-bottom: none;
}

.app-main {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
</style>
