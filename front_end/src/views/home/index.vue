<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getPosts } from '../../api/posts'

const router = useRouter()
const { t } = useI18n()
const recentPosts = ref([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const data = await getPosts({ skip: 0, limit: 6 })
    recentPosts.value = data.posts
  } catch (e) {
    console.error('Failed to load posts:', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home">
    <div class="hero">
      <h1>{{ t('home.heroTitle') }}</h1>
      <p class="hero-desc">{{ t('home.heroDesc') }}</p>
      <div class="hero-actions">
        <el-button type="primary" size="large" @click="router.push('/posts')">
          <el-icon><Document /></el-icon>
          {{ t('home.browsePosts') }}
        </el-button>
        <el-button size="large" @click="router.push('/chat')">
          <el-icon><ChatDotRound /></el-icon>
          {{ t('home.aiChat') }}
        </el-button>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>{{ t('home.recentPosts') }}</h2>
        <el-button text type="primary" @click="router.push('/posts')">{{ t('home.viewAll') }}</el-button>
      </div>
      <el-row :gutter="16" v-loading="loading">
        <el-col :xs="24" :sm="12" :md="8" v-for="post in recentPosts" :key="post.id">
          <el-card
            shadow="hover"
            class="post-card"
            @click="router.push(`/posts/${post.id}`)"
          >
            <template #header>
              <span class="post-title">{{ post.title }}</span>
            </template>
            <p class="post-excerpt">{{ post.content?.substring(0, 100) }}...</p>
            <div class="post-meta">
              <el-tag v-for="tag in post.tags?.slice(0, 3)" :key="tag" size="small" type="info">
                {{ tag }}
              </el-tag>
              <span class="post-date">{{ new Date(post.created_at).toLocaleDateString() }}</span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<style scoped>
.hero {
  text-align: center;
  padding: 60px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: #fff;
  margin-bottom: 40px;
}

.hero h1 {
  font-size: 36px;
  margin-bottom: 12px;
}

.hero-desc {
  font-size: 16px;
  opacity: 0.9;
  margin-bottom: 24px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.post-card {
  cursor: pointer;
  margin-bottom: 16px;
  transition: transform 0.2s;
}

.post-card:hover {
  transform: translateY(-2px);
}

.post-title {
  font-weight: 600;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-excerpt {
  color: #666;
  font-size: 13px;
  line-height: 1.6;
  margin-bottom: 12px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.post-date {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}
</style>
