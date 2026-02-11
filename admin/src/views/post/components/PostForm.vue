<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" :rules="rules" label-width="80px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="postForm.title" placeholder="请输入帖子标题" maxlength="200" show-word-limit />
      </el-form-item>

      <el-form-item label="语言" prop="language">
        <el-select v-model="postForm.language" placeholder="请选择语言">
          <el-option label="中文" value="zh-CN" />
          <el-option label="English" value="en" />
        </el-select>
      </el-form-item>

      <el-form-item label="标签">
        <el-tag
          v-for="tag in postForm.tags"
          :key="tag"
          closable
          :disable-transitions="false"
          style="margin-right: 8px;"
          @close="handleTagClose(tag)"
        >
          {{ tag }}
        </el-tag>
        <el-input
          v-if="tagInputVisible"
          ref="tagInput"
          v-model="tagInputValue"
          size="small"
          style="width: 120px;"
          @keyup.enter.native="handleTagConfirm"
          @blur="handleTagConfirm"
        />
        <el-button v-else size="small" @click="showTagInput">+ 添加标签</el-button>
      </el-form-item>

      <el-form-item label="内容" prop="content">
        <Tinymce ref="editor" v-model="postForm.content" :height="400" />
      </el-form-item>

      <el-form-item>
        <el-button v-loading="loading" type="primary" @click="submitForm">
          {{ isEdit ? '更新' : '发布' }}
        </el-button>
        <el-button @click="goBack">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import Tinymce from '@/components/Tinymce'
import { fetchPost, createPost, updatePost } from '@/api/post'

export default {
  name: 'PostForm',
  components: { Tinymce },
  props: {
    isEdit: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      postForm: {
        title: '',
        content: '',
        language: 'zh-CN',
        tags: []
      },
      loading: false,
      tagInputVisible: false,
      tagInputValue: '',
      rules: {
        title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
        content: [{ required: true, message: '请输入内容', trigger: 'blur' }],
        language: [{ required: true, message: '请选择语言', trigger: 'change' }]
      }
    }
  },
  created() {
    if (this.isEdit) {
      const id = this.$route.params && this.$route.params.id
      this.fetchData(id)
    }
  },
  methods: {
    fetchData(id) {
      fetchPost(id).then(response => {
        this.postForm = response.data
        if (!this.postForm.tags) {
          this.$set(this.postForm, 'tags', [])
        }
      }).catch(err => {
        console.log(err)
      })
    },
    handleTagClose(tag) {
      this.postForm.tags.splice(this.postForm.tags.indexOf(tag), 1)
    },
    showTagInput() {
      this.tagInputVisible = true
      this.$nextTick(() => {
        this.$refs.tagInput.$refs.input.focus()
      })
    },
    handleTagConfirm() {
      const val = this.tagInputValue.trim()
      if (val && !this.postForm.tags.includes(val)) {
        this.postForm.tags.push(val)
      }
      this.tagInputVisible = false
      this.tagInputValue = ''
    },
    submitForm() {
      this.$refs.postForm.validate(valid => {
        if (!valid) return false

        this.loading = true
        const action = this.isEdit
          ? updatePost(this.$route.params.id, this.postForm)
          : createPost(this.postForm)

        action.then(() => {
          this.$notify({
            title: '成功',
            message: this.isEdit ? '更新成功' : '发布成功',
            type: 'success',
            duration: 2000
          })
          this.loading = false
          this.$router.push('/post/list')
        }).catch(() => {
          this.loading = false
        })
      })
    },
    goBack() {
      this.$router.push('/post/list')
    }
  }
}
</script>
