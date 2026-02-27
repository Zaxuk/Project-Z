<template>
  <div class="notifications">
    <h2>通知中心</h2>
    
    <el-table :data="notifications" style="width: 100%" v-loading="loading">
      <el-table-column prop="createdAt" label="时间"></el-table-column>
      <el-table-column prop="title" label="标题"></el-table-column>
      <el-table-column prop="message" label="内容"></el-table-column>
      <el-table-column prop="readStatus" label="状态">
        <template #default="scope">
          <el-tag v-if="scope.row.readStatus === 'unread'" type="warning">未读</el-tag>
          <el-tag v-else-if="scope.row.readStatus === 'read'" type="info">已读</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button v-if="scope.row.readStatus === 'unread'" @click="markAsRead(scope.row.id)">标记为已读</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Notifications',
  setup() {
    const store = useStore()
    const loading = ref(false)

    const notifications = computed(() => store.state.notifications)

    onMounted(async () => {
      loading.value = true
      await store.dispatch('fetchNotifications')
      loading.value = false
    })

    const markAsRead = async (notificationId) => {
      await store.dispatch('markNotificationAsRead', notificationId)
    }

    return {
      notifications,
      loading,
      markAsRead
    }
  }
}
</script>

<style scoped>
.notifications {
  padding: 20px;
}
</style>