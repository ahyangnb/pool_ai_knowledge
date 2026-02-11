<template>
  <div class="app-container">
    <el-table v-loading="loading" :data="keyList" border fit highlight-current-row style="width: 100%">
      <el-table-column label="类型" width="120" align="center">
        <template slot-scope="{ row }">
          <span>{{ row.type }}</span>
        </template>
      </el-table-column>

      <el-table-column label="名称" width="180">
        <template slot-scope="{ row }">
          <span>{{ row.key_name || '-' }}</span>
        </template>
      </el-table-column>

      <el-table-column label="Key（脱敏）" min-width="220">
        <template slot-scope="{ row }">
          <span v-if="row.configured">{{ row.masked_value }}</span>
          <span v-else style="color: #909399;">未配置</span>
        </template>
      </el-table-column>

      <el-table-column label="来源" width="120" align="center">
        <template slot-scope="{ row }">
          <el-tag v-if="row.source" size="small">{{ row.source }}</el-tag>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column label="状态" width="100" align="center">
        <template slot-scope="{ row }">
          <el-tag :type="row.configured ? 'success' : 'info'" size="small">
            {{ row.configured ? '已配置' : '未配置' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" width="120" align="center">
        <template slot-scope="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)">
            {{ row.configured ? '修改' : '配置' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog :title="dialogTitle" :visible.sync="dialogVisible" width="500px">
      <el-form ref="form" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="Key 类型">
          <el-input :value="form.key_type" disabled />
        </el-form-item>
        <el-form-item label="名称" prop="key_name">
          <el-input v-model="form.key_name" placeholder="请输入名称，如 OpenAI Key" />
        </el-form-item>
        <el-form-item label="Key 值" prop="key_value">
          <el-input v-model="form.key_value" placeholder="请输入 API Key" show-password />
        </el-form-item>
      </el-form>
      <div slot="footer">
        <el-button @click="dialogVisible = false">取 消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确 定</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { fetchEffectiveKeys, saveApiKey } from '@/api/api-key'

export default {
  name: 'ApiKeyManagement',
  data() {
    return {
      loading: false,
      keyList: [],
      dialogVisible: false,
      submitting: false,
      form: {
        key_type: '',
        key_name: '',
        key_value: ''
      },
      rules: {
        key_name: [{ required: true, message: '请输入名称', trigger: 'blur' }],
        key_value: [{ required: true, message: '请输入 API Key', trigger: 'blur' }]
      }
    }
  },
  computed: {
    dialogTitle() {
      return this.form.key_type ? `配置 ${this.form.key_type} API Key` : '配置 API Key'
    }
  },
  created() {
    this.fetchKeys()
  },
  methods: {
    fetchKeys() {
      this.loading = true
      fetchEffectiveKeys().then(response => {
        const data = response.data
        this.keyList = Object.keys(data).map(type => ({
          type,
          ...data[type]
        }))
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    handleEdit(row) {
      this.form = {
        key_type: row.type,
        key_name: row.key_name || '',
        key_value: ''
      }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs.form.clearValidate()
      })
    },
    handleSubmit() {
      this.$refs.form.validate(valid => {
        if (!valid) return
        this.submitting = true
        saveApiKey(this.form).then(() => {
          this.$message({ type: 'success', message: '保存成功' })
          this.dialogVisible = false
          this.fetchKeys()
        }).finally(() => {
          this.submitting = false
        })
      })
    }
  }
}
</script>
