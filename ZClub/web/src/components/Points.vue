<template>
  <div class="points">
    <h2>积分管理</h2>
    
    <el-card>
      <template #header>
        <div class="card-header">
          <span>当前积分余额</span>
        </div>
      </template>
      <div class="balance">
        <el-tag size="large" type="success">{{ points }} Z币</el-tag>
      </div>
    </el-card>

    <el-card style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>积分历史</span>
        </div>
      </template>
      <el-table :data="pointRecords" style="width: 100%" v-loading="loading">
        <el-table-column prop="createdAt" label="时间"></el-table-column>
        <el-table-column prop="type" label="类型">
          <template #default="scope">
            <el-tag v-if="scope.row.type === 'earned'" type="success">赚取</el-tag>
            <el-tag v-else-if="scope.row.type === 'spent'" type="danger">消耗</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="amount" label="数量">
          <template #default="scope">
            <span v-if="scope.row.type === 'earned'">+{{ scope.row.amount }}</span>
            <span v-else-if="scope.row.type === 'spent'">-{{ scope.row.amount }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述"></el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'

export default {
  name: 'Points',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const pointRecords = ref([])
    const points = ref(0)

    onMounted(async () => {
      loading.value = true
      try {
        // 获取积分余额
        const balanceResponse = await axios.get(`/api/points/balance/${store.state.user.id}`)
        points.value = balanceResponse.data.balance

        // 获取积分历史
        const recordsResponse = await axios.get(`/api/points/records/${store.state.user.id}`)
        pointRecords.value = recordsResponse.data
      } catch (error) {
        console.error('Failed to fetch points:', error)
      } finally {
        loading.value = false
      }
    })

    return {
      points,
      pointRecords,
      loading
    }
  }
}
</script>

<style scoped>
.points {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.balance {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  padding: 20px 0;
}
</style>