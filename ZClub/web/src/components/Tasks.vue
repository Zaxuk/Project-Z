<template>
  <div class="tasks">
    <h2>任务列表</h2>
    <el-button type="primary" v-if="isAdmin || isParent" @click="showCreateTaskDialog = true">创建任务</el-button>
    
    <el-dialog
      v-model="showCreateTaskDialog"
      title="创建任务"
      width="600px"
    >
      <el-form :model="taskForm" label-width="100px">
        <el-form-item label="任务标题">
          <el-input v-model="taskForm.title" placeholder="请输入任务标题"></el-input>
        </el-form-item>
        <el-form-item label="任务描述">
          <el-input v-model="taskForm.description" type="textarea" placeholder="请输入任务描述"></el-input>
        </el-form-item>
        <el-form-item label="积分奖励">
          <el-input v-model.number="taskForm.pointsReward" type="number" placeholder="请输入积分奖励"></el-input>
        </el-form-item>
        <el-form-item label="任务类型">
          <el-select v-model="taskForm.taskType" placeholder="请选择任务类型">
            <el-option label="学习任务" value="study"></el-option>
            <el-option label="家务任务" value="chore"></el-option>
            <el-option label="行为任务" value="behavior"></el-option>
            <el-option label="临时任务" value="temporary"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="任务状态">
          <el-select v-model="taskForm.status" placeholder="请选择任务状态">
            <el-option label="待执行" value="pending"></el-option>
            <el-option label="进行中" value="in_progress"></el-option>
            <el-option label="已完成" value="completed"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateTaskDialog = false">取消</el-button>
          <el-button type="primary" @click="createTask">创建</el-button>
        </span>
      </template>
    </el-dialog>

    <el-table :data="tasks" style="width: 100%" v-loading="loading">
      <el-table-column prop="title" label="任务标题"></el-table-column>
      <el-table-column prop="description" label="任务描述"></el-table-column>
      <el-table-column prop="pointsReward" label="积分奖励"></el-table-column>
      <el-table-column prop="taskType" label="任务类型">
        <template #default="scope">
          <span v-if="scope.row.taskType === 'study'">学习任务</span>
          <span v-else-if="scope.row.taskType === 'chore'">家务任务</span>
          <span v-else-if="scope.row.taskType === 'behavior'">行为任务</span>
          <span v-else-if="scope.row.taskType === 'temporary'">临时任务</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="任务状态">
        <template #default="scope">
          <span v-if="scope.row.status === 'pending'">待执行</span>
          <span v-else-if="scope.row.status === 'in_progress'">进行中</span>
          <span v-else-if="scope.row.status === 'completed'">已完成</span>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <el-button v-if="isChild && scope.row.status === 'pending'" @click="completeTask(scope.row.id)">完成</el-button>
          <el-button v-if="isAdmin || isParent" @click="editTask(scope.row)">编辑</el-button>
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
  name: 'Tasks',
  setup() {
    const store = useStore()
    const loading = ref(false)
    const showCreateTaskDialog = ref(false)
    const taskForm = ref({
      title: '',
      description: '',
      pointsReward: 0,
      taskType: 'study',
      status: 'pending'
    })

    const tasks = computed(() => store.state.tasks)
    const isAdmin = computed(() => store.getters.isAdmin)
    const isParent = computed(() => store.getters.isParent)
    const isChild = computed(() => store.getters.isChild)

    onMounted(async () => {
      loading.value = true
      await store.dispatch('fetchTasks')
      loading.value = false
    })

    const createTask = async () => {
      try {
        const response = await axios.post('/api/tasks', {
          ...taskForm.value,
          familyId: store.state.user.familyId,
          createdBy: store.state.user.id
        })
        await store.dispatch('fetchTasks')
        showCreateTaskDialog.value = false
      } catch (error) {
        console.error('Failed to create task:', error)
      }
    }

    const completeTask = async (taskId) => {
      try {
        await store.dispatch('completeTask', {
          taskId,
          userId: store.state.user.id
        })
      } catch (error) {
        console.error('Failed to complete task:', error)
      }
    }

    const editTask = (task) => {
      // 编辑任务逻辑
      console.log('Edit task:', task)
    }

    return {
      tasks,
      loading,
      showCreateTaskDialog,
      taskForm,
      isAdmin,
      isParent,
      isChild,
      createTask,
      completeTask,
      editTask
    }
  }
}
</script>

<style scoped>
.tasks {
  padding: 20px;
}

.dialog-footer {
  width: 100%;
  display: flex;
  justify-content: flex-end;
}
</style>