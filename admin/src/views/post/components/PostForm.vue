<template>
  <div class="app-container">
    <el-form ref="postForm" :model="postForm" :rules="rules" label-width="80px">
      <el-form-item label="标题" prop="title">
        <el-input v-model="postForm.title" placeholder="请输入帖子标题" maxlength="200" show-word-limit />
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
        content: ''
      },
      loading: false,
      rules: {
        title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
        content: [{ required: true, message: '请输入内容', trigger: 'blur' }]
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
      }).catch(err => {
        console.log(err)
      })
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
