<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getPost } from '../../api/posts'
import { renderMarkdown } from '../../utils/markdown'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const post = ref(null)
const loading = ref(false)

async function loadPost() {
  loading.value = true
  try {
    post.value = await getPost(route.params.id)
  } catch (e) {
    console.error('Failed to load post:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadPost)
watch(locale, loadPost)
</script>

<template>
  <div class="post-detail" v-loading="loading">
    <el-button text @click="router.back()" class="back-btn">
      <el-icon><ArrowLeft /></el-icon>
      {{ t('detail.back') }}
    </el-button>

    <template v-if="post">
      <h1 class="post-title">{{ post.title }}</h1>
      <div class="post-info">
        <el-tag v-for="tag in post.tags" :key="tag" size="small" type="info">
          {{ tag }}
        </el-tag>
        <span class="post-date">{{ new Date(post.created_at).toLocaleDateString() }}</span>
      </div>
      <el-divider />
      <div class="post-content markdown-body" v-html="renderMarkdown(post.content)"></div>

      <el-divider />
      <div class="chat-cta">
        <p>{{ t('detail.chatCta') }}</p>
        <el-button type="primary" @click="router.push({ path: '/chat', query: { postId: post.id, postTitle: post.title } })">
          <el-icon><ChatDotRound /></el-icon>
          {{ t('detail.askAi') }}
        </el-button>
      </div>
    </template>

    <el-empty v-else-if="!loading" :description="t('detail.notFound')" />
  </div>
</template>

<style scoped>
.back-btn {
  margin-bottom: 16px;
}

.post-title {
  font-size: 28px;
  margin-bottom: 16px;
  line-height: 1.4;
}

.post-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.post-date {
  font-size: 13px;
  color: #999;
}

.post-content {
  margin-top: 16px;
}

.chat-cta {
  text-align: center;
  padding: 20px 0;
}

.chat-cta p {
  margin-bottom: 12px;
  color: #666;
}
</style>
