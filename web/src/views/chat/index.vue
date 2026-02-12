<script setup>
import { ref, nextTick, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { chatWithAgent } from '../../api/chat'
import { getPosts } from '../../api/posts'
import { renderMarkdown } from '../../utils/markdown'

const route = useRoute()
const router = useRouter()
const { t, locale } = useI18n()
const inputMessage = ref('')
const messages = ref([])
const loading = ref(false)
const chatContainer = ref(null)

// Article context
const selectedPostId = ref(null)
const selectedPostTitle = ref('')
const postOptions = ref([])
const postsLoading = ref(false)

async function loadPostOptions() {
  postsLoading.value = true
  try {
    const data = await getPosts({ skip: 0, limit: 100 })
    postOptions.value = data.posts
  } catch (e) {
    console.error('Failed to load posts:', e)
  } finally {
    postsLoading.value = false
  }
}

onMounted(async () => {
  await loadPostOptions()
  if (route.query.postId) {
    selectedPostId.value = route.query.postId
    selectedPostTitle.value = route.query.postTitle || ''
  }
})
watch(locale, loadPostOptions)

function onPostChange(postId) {
  if (postId) {
    const post = postOptions.value.find((p) => p.id === postId)
    selectedPostTitle.value = post?.title || ''
  } else {
    selectedPostTitle.value = ''
  }
}

function clearPostContext() {
  selectedPostId.value = null
  selectedPostTitle.value = ''
}

async function sendMessage() {
  const text = inputMessage.value.trim()
  if (!text || loading.value) return

  const userMsg = { role: 'user', content: text }
  if (selectedPostId.value) {
    userMsg.postTitle = selectedPostTitle.value
  }
  messages.value.push(userMsg)
  inputMessage.value = ''
  loading.value = true
  scrollToBottom()

  try {
    const data = await chatWithAgent(text, {
      postId: selectedPostId.value,
      language: locale.value,
    })
    const assistantMsg = { role: 'assistant', content: data.response }
    if (data.references?.length) {
      assistantMsg.references = data.references
    }
    messages.value.push(assistantMsg)
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: t('chat.error'),
      error: true,
    })
  } finally {
    loading.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight
    }
  })
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}
</script>

<template>
  <div class="chat-page">
    <h2 class="page-title">{{ t('chat.title') }}</h2>
    <p class="page-desc">{{ t('chat.desc') }}</p>

    <!-- Article context selector -->
    <div class="context-bar">
      <el-select
        v-model="selectedPostId"
        :placeholder="t('chat.selectPost')"
        clearable
        filterable
        :loading="postsLoading"
        @change="onPostChange"
        class="post-select"
      >
        <el-option
          v-for="post in postOptions"
          :key="post.id"
          :label="post.title"
          :value="post.id"
        />
      </el-select>
      <el-tag
        v-if="selectedPostId"
        type="success"
        closable
        @close="clearPostContext"
        class="context-tag"
      >
        <el-icon class="context-tag-icon"><Document /></el-icon>
        <span class="context-tag-text">{{ t('chat.contextPrefix') }}: {{ selectedPostTitle }}</span>
      </el-tag>
    </div>

    <div class="chat-box">
      <div class="chat-messages" ref="chatContainer">
        <div v-if="messages.length === 0" class="chat-empty">
          <el-icon :size="48" color="#c0c4cc"><ChatDotRound /></el-icon>
          <p>{{ t('chat.emptyHint') }}</p>
          <p class="chat-empty-hint">{{ t('chat.emptySubHint') }}</p>
        </div>

        <div
          v-for="(msg, index) in messages"
          :key="index"
          class="message"
          :class="msg.role"
        >
          <div class="message-avatar">
            <el-icon v-if="msg.role === 'user'" :size="20"><User /></el-icon>
            <el-icon v-else :size="20"><Monitor /></el-icon>
          </div>
          <div class="message-content">
            <div v-if="msg.postTitle" class="message-context">
              <el-icon :size="12"><Document /></el-icon>
              {{ msg.postTitle }}
            </div>
            <div
              class="message-bubble"
              :class="{ error: msg.error, 'markdown-body': msg.role === 'assistant' }"
            >
              <template v-if="msg.role === 'assistant'">
                <div v-html="renderMarkdown(msg.content)"></div>
              </template>
              <template v-else>{{ msg.content }}</template>
            </div>
            <div v-if="msg.references?.length" class="message-refs">
              <el-icon :size="12"><Link /></el-icon>
              <span
                v-for="ref in msg.references"
                :key="ref.post_id"
                class="ref-link"
                @click="router.push(`/posts/${ref.post_id}`)"
              >{{ ref.title }}</span>
            </div>
          </div>
        </div>

        <div v-if="loading" class="message assistant">
          <div class="message-avatar">
            <el-icon :size="20"><Monitor /></el-icon>
          </div>
          <div class="message-bubble typing">
            <span></span><span></span><span></span>
          </div>
        </div>
      </div>

      <div class="chat-input">
        <el-input
          v-model="inputMessage"
          type="textarea"
          :rows="2"
          :placeholder="selectedPostId ? t('chat.placeholderWithPost', { title: selectedPostTitle }) : t('chat.placeholder')"
          @keydown="handleKeydown"
          :disabled="loading"
        />
        <el-button
          type="primary"
          :loading="loading"
          @click="sendMessage"
          :disabled="!inputMessage.trim()"
        >
          {{ t('chat.send') }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  margin-bottom: 8px;
}

.page-desc {
  color: #666;
  font-size: 14px;
  margin-bottom: 16px;
}

.context-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.post-select {
  width: 360px;
}

.context-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  max-width: 360px;
}

.context-tag :deep(.el-tag__content) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  overflow: hidden;
  min-width: 0;
}

.context-tag-icon {
  flex-shrink: 0;
}

.context-tag-text {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.chat-box {
  background: #fff;
  border-radius: 12px;
  border: 1px solid var(--el-border-color-light);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 300px);
  min-height: 400px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.chat-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
  gap: 12px;
}

.chat-empty-hint {
  font-size: 13px;
}

.message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message.user .message-avatar {
  background: var(--el-color-primary-light-7);
  color: var(--el-color-primary);
}

.message-content {
  max-width: 70%;
}

.message-context {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--el-color-success);
  margin-bottom: 4px;
}

.message-refs {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
  font-size: 12px;
  color: #999;
}

.ref-link {
  color: var(--el-color-primary);
  cursor: pointer;
  text-decoration: underline;
  text-decoration-style: dashed;
  text-underline-offset: 2px;
}

.ref-link:hover {
  color: var(--el-color-primary-dark-2);
  text-decoration-style: solid;
}

.message.user .message-context {
  justify-content: flex-end;
}

.message-bubble {
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.user .message-bubble {
  background: var(--el-color-primary);
  color: #fff;
  border-top-right-radius: 4px;
}

.message.assistant .message-bubble {
  background: #f0f2f5;
  color: #333;
  border-top-left-radius: 4px;
  white-space: normal;
}

.message-bubble.error {
  background: var(--el-color-danger-light-9);
  color: var(--el-color-danger);
}

.typing {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 14px 20px;
}

.typing span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
  animation: typing 1.2s infinite ease-in-out;
}

.typing span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 60%, 100% { opacity: 0.3; transform: scale(0.8); }
  30% { opacity: 1; transform: scale(1); }
}

.chat-input {
  display: flex;
  gap: 10px;
  padding: 16px;
  border-top: 1px solid var(--el-border-color-light);
  align-items: flex-end;
}

.chat-input .el-textarea {
  flex: 1;
}

.chat-input .el-button {
  height: 54px;
}
</style>
