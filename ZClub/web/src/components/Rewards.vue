<template>
  <div class="rewards">
    <h2>奖励商城</h2>
    
    <el-tabs>
      <el-tab-pane label="自定义奖励">
        <el-button type="primary" v-if="isAdmin" @click="showCreateRewardDialog = true">创建奖励</el-button>
        
        <el-dialog
          v-model="showCreateRewardDialog"
          title="创建奖励"
          width="600px"
        >
          <el-form :model="rewardForm" label-width="100px">
            <el-form-item label="奖励名称">
              <el-input v-model="rewardForm.name" placeholder="请输入奖励名称"></el-input>
            </el-form-item>
            <el-form-item label="奖励描述">
              <el-input v-model="rewardForm.description" type="textarea" placeholder="请输入奖励描述"></el-input>
            </el-form-item>
            <el-form-item label="所需积分">
              <el-input v-model.number="rewardForm.pointsRequired" type="number" placeholder="请输入所需积分"></el-input>
            </el-form-item>
            <el-form-item label="库存数量">
              <el-input v-model.number="rewardForm.stock" type="number" placeholder="请输入库存数量（可选）"></el-input>
            </el-form-item>
          </el-form>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="showCreateRewardDialog = false">取消</el-button>
              <el-button type="primary" @click="createReward">创建</el-button>
            </span>
          </template>
        </el-dialog>

        <el-table :data="rewards" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="奖励名称"></el-table-column>
          <el-table-column prop="description" label="奖励描述"></el-table-column>
          <el-table-column prop="pointsRequired" label="所需积分"></el-table-column>
          <el-table-column prop="stock" label="库存数量">
            <template #default="scope">
              <span v-if="scope.row.stock === null">无限制</span>
              <span v-else>{{ scope.row.stock }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button v-if="isChild" @click="redeemReward(scope.row.id)">兑换</el-button>
              <el-button v-if="isAdmin" @click="editReward(scope.row)">编辑</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      
      <el-tab-pane label="系统默认奖励">
        <el-table :data="defaultRewards" style="width: 100%" v-loading="loading">
          <el-table-column prop="name" label="奖励名称"></el-table-column>
          <el-table-column prop="description" label="奖励描述"></el-table-column>
          <el-table-column prop="pointsRequired" label="所需积分"></el-table-column>
          <el-table-column label="操作">
            <template #default="scope">
              <el-button v-if="isChild" @click="redeemReward(scope.row.id)">兑换</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'
import axios from 'axios'

export default {
  name: 'Rewards',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const showCreateRewardDialog = ref(false)
    const rewardForm = ref({
      name: '',
      description: '',
      pointsRequired: 0,
      stock: null
    })

    const rewards = computed(() => store.state.rewards)
    const defaultRewards = computed(() => store.state.defaultRewards)
    const isAdmin = computed(() => store.getters.isAdmin)
    const isChild = computed(() => store.getters.isChild)

    onMounted(async () => {
      loading.value = true
      await store.dispatch('fetchRewards')
      await store.dispatch('fetchDefaultRewards')
      loading.value = false
    })

    const createReward = async () => {
      try {
        const response = await axios.post('/api/rewards', {
          ...rewardForm.value,
          familyId: store.state.user.familyId,
          createdBy: store.state.user.id
        })
        await store.dispatch('fetchRewards')
        showCreateRewardDialog.value = false
      } catch (error) {
        console.error('Failed to create reward:', error)
      }
    }

    const redeemReward = async (rewardId) => {
      try {
        await store.dispatch('redeemReward', {
          rewardId,
          userId: store.state.user.id
        })
      } catch (error) {
        console.error('Failed to redeem reward:', error)
      }
    }

    const editReward = (reward) => {
      // 编辑奖励逻辑
      console.log('Edit reward:', reward)
    }

    return {
      rewards,
      defaultRewards,
      loading,
      showCreateRewardDialog,
      rewardForm,
      isAdmin,
      isChild,
      createReward,
      redeemReward,
      editReward
    }
  }
}
</script>

<style scoped>
.rewards {
  padding: 20px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>