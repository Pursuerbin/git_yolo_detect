<template>
  <el-card class="config-card" shadow="hover">
    <template #header>
      <div class="card-header">
        <el-icon><Cpu /></el-icon>
        <span>设备选择</span>
      </div>
    </template>
    <div class="device-selector">
      <!-- 设备检测状态 -->
      <div class="device-status" v-if="deviceInfo">
        <!-- 设备状态 -->
        <el-tag :type="deviceInfo.hasGpu ? 'success' : 'warning'" size="large">
          <el-icon><Cpu /></el-icon>
          {{ deviceInfo.currentDevice || 'CPU' }}
        </el-tag>
        <p class="device-desc" v-if="deviceInfo.hasGpu">
          🎮 GPU可用: {{ deviceInfo.gpuName }}
        </p>
        <p class="device-desc" v-else>
          ⚙️ 仅CPU可用
        </p>
      </div>
      
      <!-- 设备切换 -->
      <div class="device-toggle" v-if="deviceInfo && deviceInfo.hasGpu">
        <el-divider content-position="left">设备切换</el-divider>
        <el-radio-group v-model="selectedDevice" size="large" @change="onDeviceChange">
          <el-radio-button label="auto">自动选择</el-radio-button>
          <el-radio-button label="cpu">强制CPU</el-radio-button>
          <el-radio-button label="cuda">强制GPU</el-radio-button>
        </el-radio-group>
        <div class="toggle-info">
          <el-tag size="small" type="info">
            <el-icon><InfoFilled /></el-icon>
            切换设备后将重新加载模型
          </el-tag>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div class="loading-status" v-if="loadingDevice">
        <el-skeleton :rows="3" animated />
      </div>
      
      <!-- 错误状态 -->
      <div class="error-status" v-if="deviceError">
        <el-alert
          :title="deviceError"
          type="error"
          show-icon
          :closable="false"
        />
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, watch } from 'vue'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const props = defineProps({
  deviceInfo: {
    type: Object,
    default: null
  },
  loadingDevice: {
    type: Boolean,
    default: false
  },
  deviceError: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['deviceChange'])

const selectedDevice = ref('auto')

const onDeviceChange = (value) => {
  emit('deviceChange', value)
}

// 监听设备信息变化，更新选中设备
watch(
  () => props.deviceInfo,
  (newDeviceInfo) => {
    if (newDeviceInfo) {
      selectedDevice.value = newDeviceInfo.currentDevice === 'cpu' ? 'cpu' : 'auto'
    }
  },
  { immediate: true }
)
</script>

<style scoped>
.device-selector {
  padding: 10px 0;
}

.device-status {
  margin-bottom: 20px;
}

.device-desc {
  margin: 10px 0 0 0;
  font-size: 14px;
  color: #666;
}

.device-toggle {
  margin-top: 20px;
}

.toggle-info {
  margin-top: 10px;
}

.loading-status {
  margin: 20px 0;
}

.error-status {
  margin: 20px 0;
}
</style>