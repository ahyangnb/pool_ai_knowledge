<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { getPosts } from '../../api/posts'

const router = useRouter()
const { t } = useI18n()
const posts = ref([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(12)
const loading = ref(false)

async function loadPosts() {
  loading.value = true
  try {
    const data = await getPosts({
      skip: (page.value - 1) * pageSize.value,
      limit: pageSize.value,
    })
    posts.value = data.posts
    total.value = data.total
  } catch (e) {
    console.error('Failed to load posts:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadPosts)
watch(page, loadPosts)
</script>

<template>
  <div class="posts-page">
    <h2 class="page-title">{{ t('posts.title') }}</h2>

    <el-row :gutter="16" v-loading="loading">
      <el-col :xs="24" :sm="12" :md="8" v-for="post in posts" :key="post.id">
        <el-card
          shadow="hover"
          class="post-card"
          @click="router.push(`/posts/${post.id}`)"
        >
          <template #header>
            <span class="post-title">{{ post.title }}</span>
          </template>
          <p class="post-excerpt">{{ post.content?.substring(0, 120) }}...</p>
          <div class="post-meta">
            <el-tag v-for="tag in post.tags?.slice(0, 3)" :key="tag" size="small" type="info">
              {{ tag }}
            </el-tag>
            <span class="post-date">{{ new Date(post.created_at).toLocaleDateString() }}</span>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div class="pagination" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="page"
        :page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
      />
    </div>
  </div>
</template>

<style scoped>
.page-title {
  margin-bottom: 20px;
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

.pagination {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
