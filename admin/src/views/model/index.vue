<template>
  <div class="app-container">
    <el-card v-loading="loading">
      <div slot="header">
        <span>当前模型</span>
      </div>
      <el-tag type="success" size="medium">{{ currentModel || '未设置' }}</el-tag>
    </el-card>

    <el-card v-loading="loading" style="margin-top: 20px;">
      <div slot="header">
        <span>可用模型列表</span>
      </div>
      <el-table :data="models" border fit highlight-current-row>
        <el-table-column label="模型名称" min-width="300">
          <template slot-scope="{ row }">
            <span>{{ row }}</span>
          </template>
        </el-table-column>

        <el-table-column label="状态" width="120" align="center">
          <template slot-scope="{ row }">
            <el-tag v-if="row === currentModel" type="success" size="small">使用中</el-tag>
            <span v-else style="color: #909399;">-</span>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" align="center">
          <template slot-scope="{ row }">
            <el-button
              v-if="row !== currentModel"
              type="primary"
              size="small"
              :loading="switching === row"
              @click="handleSwitch(row)"
            >
              切换
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { fetchModels, switchModel } from '@/api/model'

export default {
  name: 'ModelManagement',
  data() {
    return {
      loading: false,
      models: [],
      currentModel: '',
      switching: null
    }
  },
  created() {
    this.getModels()
  },
  methods: {
    getModels() {
      this.loading = true
      fetchModels().then(response => {
        this.models = response.data.models || []
        this.currentModel = response.data.current || ''
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    handleSwitch(model) {
      this.$confirm(`确定要切换到模型 "${model}" 吗？`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.switching = model
        switchModel(model).then(() => {
          this.$message({ type: 'success', message: '切换成功' })
          this.currentModel = model
        }).finally(() => {
          this.switching = null
        })
      }).catch(() => {})
    }
  }
}
</script>
