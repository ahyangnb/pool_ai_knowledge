<script setup>
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'

const router = useRouter()
const { t, locale } = useI18n()

function switchLanguage(lang) {
  locale.value = lang
  localStorage.setItem('language', lang)
}
</script>

<template>
  <el-container class="app-container">
    <el-header class="app-header">
      <div class="header-left" @click="router.push('/')">
        <el-icon :size="24"><Reading /></el-icon>
        <span class="app-title">{{ t('nav.title') }}</span>
      </div>
      <el-menu
        mode="horizontal"
        :router="true"
        :default-active="$route.path"
        class="header-menu"
      >
        <el-menu-item index="/">{{ t('nav.home') }}</el-menu-item>
        <el-menu-item index="/posts">{{ t('nav.posts') }}</el-menu-item>
        <el-menu-item index="/chat">{{ t('nav.chat') }}</el-menu-item>
      </el-menu>
      <div class="lang-switch">
        <el-dropdown @command="switchLanguage" trigger="click">
          <el-button text>
            <el-icon><Switch /></el-icon>
            {{ locale === 'zh-CN' ? '中文' : 'EN' }}
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="zh-CN" :disabled="locale === 'zh-CN'">
                中文
              </el-dropdown-item>
              <el-dropdown-item command="en" :disabled="locale === 'en'">
                English
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
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
  flex: 1;
}

.lang-switch {
  flex-shrink: 0;
  margin-left: 12px;
}

.app-main {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}
</style>
