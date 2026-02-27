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
import axios from 'axios'

export default {
  name: 'Notifications',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const notifications = ref([])

    onMounted(async () => {
      loading.value = true
      try {
        const response = await axios.get(`/api/notifications/${store.state.user.id}`)
        notifications.value = response.data
      } catch (error) {
        console.error('Failed to fetch notifications:', error)
      } finally {
        loading.value = false
      }
    })

    const markAsRead = async (notificationId) => {
      try {
        await axios.put(`/api/notifications/${notificationId}/read`)
        // 更新本地通知状态
        const notification = notifications.value.find(n => n.id === notificationId)
        if (notification) {
          notification.readStatus = 'read'
        }
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
      }
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