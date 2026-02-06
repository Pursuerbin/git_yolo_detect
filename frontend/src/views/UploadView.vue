<!-- src/views/UploadView.vue -->
<template>
  <div class="upload-container">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-brand">
        <h1>
          <span class="icon-wrapper">🔌</span>
          <span class="title-text">绝缘子缺陷检测系统</span>
        </h1>
        <p class="subtitle">基于YOLOv11的智能检测平台</p>
      </div>
      <div class="nav-menu">
        <el-button @click="goToVideo" type="primary" size="large" class="nav-btn">
          <el-icon><VideoCamera /></el-icon>
          视频检测
        </el-button>
        <el-button @click="goToHistory" type="info" size="large" class="nav-btn">
          <el-icon><Histogram /></el-icon>
          历史记录
        </el-button>
        <el-button @click="goToAbout" type="info" size="large" class="nav-btn">
          <el-icon><InfoFilled /></el-icon>
          关于系统
        </el-button>
        <el-button @click="logout" type="warning" size="large" class="nav-btn">
          <el-icon><SwitchButton /></el-icon>
          退出登录
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧配置面板 -->
      <div class="config-panel">
        <!-- 模型选择 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Cpu /></el-icon>
              <span>模型选择</span>
            </div>
          </template>
          <div class="model-selector">
            <el-select
              v-model="selectedModel"
              placeholder="选择检测模型"
              size="large"
              @change="onModelChange"
              class="model-select"
            >
              <el-option
                v-for="model in modelList"
                :key="model"
                :label="model"
                :value="model"
              />
            </el-select>
            <div class="model-info">
              <el-tag 
                :type="!backendStatus.connected ? 'danger' : (modelLoaded ? 'success' : 'warning')" 
                size="large"
              >
                <el-icon>
                  <component :is="!backendStatus.connected ? 'WarningFilled' : (modelLoaded ? 'SuccessFilled' : 'WarningFilled')" />
                </el-icon>
                {{ 
                  !backendStatus.connected ? '未连接' : 
                  modelLoaded ? `已加载: ${modelInfo}` : '未加载'
                }}
              </el-tag>
            </div>
          </div>
        </el-card>
        <!-- 在模型选择卡片后面添加设备选择卡片 -->
        <el-card class="config-card" shadow="hover">
            <template #header>
                <div class="card-header">
                    <el-icon><Cpu /></el-icon>
                    <span>设备选择</span>
                </div>
            </template>
            <div class="device-selector">
                <!-- 设备检测状态 -->
                <!-- 在设备检测状态部分添加空值检查 -->
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

                <!-- 设备选择 -->
                <!-- 修改设备选项部分，添加空值检查 -->
                <div class="device-options">
                    <el-radio-group v-model="selectedDevice" @change="onDeviceChange">
                        <el-radio label="auto" border size="large">
                            <span class="device-option">
                                <el-icon><MagicStick /></el-icon>
                                自动选择
                            </span>
                        </el-radio>
                        <el-radio label="cpu" border size="large" :disabled="loadingDevice">
                            <span class="device-option">
                                <el-icon><Cpu /></el-icon>
                                CPU模式
                            </span>
                        </el-radio>
                        <el-radio label="gpu" border size="large"
                                  :disabled="loadingDevice || !(deviceInfo && deviceInfo.hasGpu)">
                            <span class="device-option">
                                <el-icon><VideoPlay /></el-icon>
                                GPU加速
                            </span>
                            <el-tooltip v-if="deviceInfo && !deviceInfo.hasGpu"
                                        content="未检测到GPU"
                                        placement="top">
                                <el-icon><Warning /></el-icon>
                            </el-tooltip>
                        </el-radio>
                    </el-radio-group>
                </div>

                <!-- 强制CPU选项（用于调试） -->
                <div class="force-cpu" v-if="showAdvanced">
                    <el-checkbox v-model="forceCpu" @change="onForceCpuChange">
                        强制使用CPU（调试用）
                    </el-checkbox>
                    <el-tooltip content="即使有GPU也使用CPU，用于兼容性测试" placement="top">
                        <el-icon><QuestionFilled /></el-icon>
                    </el-tooltip>
                </div>

                <!-- 设备信息按钮 -->
                <div class="device-actions">
                    <el-button @click="refreshDeviceInfo" :loading="loadingDevice" size="small">
                        <el-icon><Refresh /></el-icon>
                        刷新设备信息
                    </el-button>
                    <el-button @click="showAdvanced = !showAdvanced" type="text" size="small">
                        {{ showAdvanced ? '隐藏' : '高级' }}
                    </el-button>
                </div>
            </div>
        </el-card>

        <!-- 参数配置 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>检测参数</span>
            </div>
          </template>

          <div class="param-item">
            <div class="param-label">
              <span>置信度阈值</span>
              <el-tag size="small" type="info">{{ confThreshold.toFixed(2) }}</el-tag>
            </div>
            <div class="param-control">
              <el-slider
                v-model="confThreshold"
                :min="0.1"
                :max="0.9"
                :step="0.05"
                :show-tooltip="true"
                :format-tooltip="formatConfidence"
              />
            </div>
            <div class="param-desc">控制检测结果的可靠性，值越高要求越严格</div>
          </div>

          <el-divider />

          <div class="param-item">
            <div class="param-label">
              <span>IoU阈值</span>
              <el-tag size="small" type="info">{{ iouThreshold.toFixed(2) }}</el-tag>
            </div>
            <div class="param-control">
              <el-slider
                v-model="iouThreshold"
                :min="0.1"
                :max="0.9"
                :step="0.05"
                :show-tooltip="true"
                :format-tooltip="formatIoU"
              />
            </div>
            <div class="param-desc">控制重叠检测框的合并，值越高允许的重叠越少</div>
          </div>
        </el-card>

        <!-- 快速操作 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Operation /></el-icon>
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button
              type="primary"
              size="large"
              @click="detectImage"
              :disabled="!selectedFile || loading"
              :loading="loading"
              class="action-btn"
            >
              <template #icon>
                <el-icon><Search /></el-icon>
              </template>
              {{ loading ? '检测中...' : '开始检测' }}
            </el-button>

            <el-button
              type="warning"
              size="large"
              @click="clearFile"
              :disabled="!selectedFile"
              class="action-btn"
            >
              <template #icon>
                <el-icon><Delete /></el-icon>
              </template>
              清除文件
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 中间上传区域 -->
      <div class="upload-area">
        <!-- 上传卡片 -->
        <el-card class="upload-card" shadow="never">
          <template #header>
            <div class="upload-header">
              <el-icon><UploadFilled /></el-icon>
              <span>图片上传</span>
              <el-tag type="info" size="small">支持 JPG, PNG, JPEG 格式</el-tag>
            </div>
          </template>

          <div
            class="upload-zone"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
            :class="{ 'drag-over': isDragOver }"
            @click="triggerFileInput"
          >
            <input
              type="file"
              id="file-input"
              accept=".jpg,.jpeg,.png"
              @change="onFileSelected"
              hidden
            >

            <div class="upload-content" v-if="!selectedFile">
              <div class="upload-icon">
                <el-icon size="80"><Upload /></el-icon>
              </div>
              <div class="upload-text">
                <h3>点击或拖拽图片到此处</h3>
                <p>支持单张图片上传，最大10MB</p>
              </div>
              <el-button type="primary" size="large" class="select-btn">
                <el-icon><FolderOpened /></el-icon>
                选择文件
              </el-button>
            </div>

            <!-- 文件预览 -->
            <div class="file-preview" v-else>
              <div class="preview-header">
                <div class="file-info">
                  <el-icon><Document /></el-icon>
                  <div class="file-details">
                    <h4>{{ selectedFile.name }}</h4>
                    <p>{{ formatFileSize(selectedFile.size) }} • {{ getFileType(selectedFile.type) }}</p>
                  </div>
                </div>
                <el-button @click.stop="clearFile" type="danger" text circle>
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>

              <div class="preview-image">
                <img :src="originalImage" alt="预览图片" />
                <div class="preview-overlay">
                  <el-button @click.stop="triggerFileInput" type="primary" circle>
                    <el-icon><Refresh /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="error-alert">
            <el-alert
              :title="error"
              type="error"
              :closable="true"
              @close="error = ''"
              show-icon
            />
          </div>
        </el-card>

        <!-- 检测结果 -->
        <div v-if="detectionResult" class="result-section">
          <el-card class="result-card" shadow="never">
            <template #header>
              <div class="result-header">
                <el-icon><Finished /></el-icon>
                <span>检测结果</span>
                <el-tag :type="detections.length > 0 ? 'warning' : 'success'" size="small">
                  {{ detections.length > 0 ? `共检测${detections.length}处` : '未检测出' }}
                </el-tag>
              </div>
            </template>

            <!-- 图像对比 -->
            <div class="image-comparison">
              <div class="comparison-item">
                <div class="comparison-header">
                  <el-icon><Picture /></el-icon>
                  <span>原始图像</span>
                </div>
                <div class="comparison-image">
                  <img :src="originalImage" alt="原始图像" />
                  <div class="image-label">原始</div>
                </div>
              </div>

              <div class="comparison-arrow">
                <el-icon size="40"><Right /></el-icon>
              </div>

              <div class="comparison-item">
                <div class="comparison-header">
                  <el-icon><DataAnalysis /></el-icon>
                  <span>检测结果</span>
                </div>
                <div class="comparison-image">
                  <img :src="resultImage" alt="检测结果" />
                  <div class="image-label">结果</div>
                </div>
              </div>
            </div>

            <!-- 检测统计 -->
            <div class="detection-stats">
              <el-row :gutter="20">
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><Timer /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ new Date().toLocaleTimeString() }}</div>
                      <div class="stat-label">检测时间</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><PieChart /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ avgConfidence.toFixed(4) }}</div>
                      <div class="stat-label">平均置信度</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><Collection /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ detections.length }}</div>
                      <div class="stat-label">检测数量</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="6">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><DataBoard /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ selectedModel }}</div>
                      <div class="stat-label">使用模型</div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 缺陷详情表格 -->
            <div v-if="detections.length > 0" class="detection-table">
              <div class="table-header">
                <h3>检测详情</h3>
                <div class="table-actions">
                  <el-button @click="exportToExcel" type="success" size="small">
                    <el-icon><Download /></el-icon>
                    导出Excel
                  </el-button>
                  <el-button @click="saveToHistory" type="primary" size="small">
                    <el-icon><DocumentAdd /></el-icon>
                    保存记录
                  </el-button>
                </div>
              </div>

              <el-table :data="detections" height="300" stripe class="defect-table">
                <el-table-column type="index" label="序号" width="80" align="center">
                  <template #default="scope">
                    <el-tag size="small">{{ scope.$index + 1 }}</el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="class" label=“检测类型” width="120">
                  <template #default="scope">
                    <el-tag :type="getDefectType(scope.row.class)" size="large">
                      {{ scope.row.class }}
                    </el-tag>
                  </template>
                </el-table-column>

                <el-table-column prop="confidence" label="置信度" width="120">
                  <template #default="scope">
                    <div class="confidence-cell">
                      <el-progress
                        :percentage="Math.round(scope.row.confidence * 100)"
                        :color="getConfidenceColor(scope.row.confidence)"
                        :show-text="false"
                      />
                      <span class="confidence-text">
                        {{ (scope.row.confidence * 100).toFixed(1) }}%
                      </span>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column label="位置坐标" width="200">
                  <template #default="scope">
                    <div class="coordinate-cell">
                      <div class="coordinate-point">
                        ({{ scope.row.x1 }}, {{ scope.row.y1 }})
                      </div>
                      <el-icon><Right /></el-icon>
                      <div class="coordinate-point">
                        ({{ scope.row.x2 }}, {{ scope.row.y2 }})
                      </div>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column label="边界框" width="120">
                  <template #default="scope">
                    <div class="bounding-box">
                      <div class="box-dimensions">
                        {{ Math.abs(scope.row.x2 - scope.row.x1) }} × {{ Math.abs(scope.row.y2 - scope.row.y1) }}
                      </div>
                      <div class="box-unit">像素</div>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column label="操作" width="100" align="center">
                  <template #default="scope">
                    <el-button
                      @click="viewDefectDetail(scope.row)"
                      type="link"
                      size="small"
                    >
                      <el-icon><View /></el-icon>
                      查看
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>

            <!-- 无缺陷提示 -->
            <div v-else class="no-defects">
              <div class="no-defects-content">
                <el-icon size="80" color="#67C23A"><CircleCheck /></el-icon>
                <h3>✅ 未检测到任何缺陷</h3>
                <p>当前图像中的绝缘子状态良好，无缺陷发现</p>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 右侧信息面板 -->
      <div class="info-panel">
        <!-- 系统状态 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>系统状态</span>
            </div>
          </template>
          <div class="status-list">
            <div class="status-item">
              <div class="status-label">
                <el-icon><Connection /></el-icon>
                <span>后端连接</span>
              </div>
              <el-tag :type="backendStatus.connected ? 'success' : 'danger'" effect="dark">
                {{ backendStatus.connected ? '正常' : '离线' }}
              </el-tag>
            </div>

            <div class="status-item">
              <div class="status-label">
                <el-icon><Cpu /></el-icon>
                <span>模型状态</span>
              </div>
              <el-tag 
                :type="!backendStatus.connected ? 'danger' : (modelLoaded ? 'success' : 'warning')" 
                effect="dark"
              >
                {{ 
                  !backendStatus.connected ? '后端离线' : 
                  modelLoaded ? '已加载' : '未加载'
                }}
              </el-tag>
            </div>

            <div class="status-item">
              <div class="status-label">
                <el-icon><DataLine /></el-icon>
                <span>检测次数</span>
              </div>
              <el-tag type="info" effect="dark">{{ detectionCount }}</el-tag>
            </div>
          </div>
        </el-card>

        <!-- 检测记录 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>最近记录</span>
            </div>
          </template>
          <div class="recent-records">
            <div v-if="recentRecords.length === 0" class="empty-records">
              <el-empty description="暂无检测记录" :image-size="100" />
            </div>
            <div v-else class="record-list">
              <div v-for="(record, index) in recentRecords" :key="index"
                   class="record-item"
                   @click="viewRecordDetail(record.id)">
                <div class="record-time">
                  <el-icon><Clock /></el-icon>
                  {{ record.time }}
                </div>
                <div class="record-info">
                  <div class="record-name">{{ record.name }}</div>
                  <div class="record-stats">
                    <el-tag size="small" :type="record.defects > 0 ? 'danger' : 'success'">
                      {{ record.defects }}处检测
                    </el-tag>
                  </div>
                </div>
              </div>
            </div>
            <div class="record-footer">
              <el-button @click="goToHistory" type="link" size="small">查看全部记录 →</el-button>
            </div>
          </div>
        </el-card>

        <!-- 使用提示 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Lightning /></el-icon>
              <span>使用提示</span>
            </div>
          </template>
          <div class="tips-list">
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>建议使用高分辨率图片以获得更准确的检测结果</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>适当调整置信度阈值可以平衡检测精度和召回率</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>检测结果会自动保存到历史记录中</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="footer">
      <div class="footer-content">
        <div class="footer-info">
          <p>© 2026 绝缘子智能缺陷检测系统 v1.1.0</p>
          <p>基于 YOLOv11 深度学习模型 | 开发者：吴权彬</p>
        </div>
        <div class="footer-contact">
          <p>📧 邮箱：1597338110@qq.com</p>
          <p>📱 电话：19303010517</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { ElMessageBox, ElNotification } from 'element-plus'
import {Collection} from "@element-plus/icons-vue";  // 添加这一行

// 导入所有图标
const icons = ElementPlusIconsVue

const router = useRouter()

// ==================== 响应式数据 ====================
const selectedFile = ref(null)
const originalImage = ref('')
const resultImage = ref('')
const detections = ref([])
const loading = ref(false)
const error = ref('')
const detectionResult = ref(null)
const modelList = ref([])
const selectedModel = ref('best.pt')
const confThreshold = ref(0.25)
const iouThreshold = ref(0.45)
const modelInfo = ref('')
const isDragOver = ref(false)
const modelLoaded = ref(true)
const detectionCount = ref(0)
const recentRecords = ref([])
const selectedDevice = ref('auto')  // 'auto', 'cpu', 'gpu'
const forceCpu = ref(false)

// 修改这里：给 deviceInfo 一个默认值
const deviceInfo = ref({
    hasGpu: false,
    currentDevice: 'cpu',
    gpuName: '',
    devices: [],
    pytorchVersion: ''
})

// 添加后端连接状态
const backendStatus = ref({
    connected: false,
    lastChecked: null,
    error: null
})

const loadingDevice = ref(false)
const showAdvanced = ref(false)
let backendCheckInterval = null

// ==================== 方法 ====================

// ==================== 配置 ====================
// 更智能的API基础地址配置
const getApiBase = () => {
  const hostname = window.location.hostname
  const protocol = window.location.protocol
  const backendPort = 5000

  // 开发环境（本地）
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `http://localhost:${backendPort}`
  }

  // 服务器环境
  return `${protocol}//${hostname}:${backendPort}`
}

const API_BASE = getApiBase()
console.log('🔧 API基础地址:', API_BASE)

// 修改所有axios请求：
// 1. 修改 loadDeviceInfo 函数
// 检查后端连接状态
const checkBackendStatus = async () => {
    try {
        const res = await axios.get(`${API_BASE}/api/health`, {
            timeout: 3000
        })
        if (res.data.status === 'healthy') {
            backendStatus.value = {
                connected: true,
                lastChecked: new Date(),
                error: null
            }
            // 更新模型加载状态
            modelLoaded.value = res.data.model_loaded || false
            console.log('✅ 后端连接正常')
            return true
        } else {
            throw new Error('后端服务不健康')
        }
    } catch (err) {
        console.error('❌ 后端连接失败:', err)
        backendStatus.value = {
            connected: false,
            lastChecked: new Date(),
            error: err.message
        }
        // 后端离线时，模型状态也视为未加载
        modelLoaded.value = false
        
        // 显示错误提示
        ElNotification({
            title: '后端连接失败',
            message: '无法连接到检测服务，请检查后端是否运行',
            type: 'error',
            duration: 5000
        })
        return false
    }
}

// 加载设备信息
const loadDeviceInfo = async () => {
    loadingDevice.value = true
    try {
        // 先检查后端连接
        const isConnected = await checkBackendStatus()
        if (!isConnected) {
            // 后端未连接，使用默认值
            deviceInfo.value = {
                hasGpu: false,
                currentDevice: 'cpu',
                gpuName: '',
                devices: [{ type: 'CPU', name: 'CPU', available: true }],
                pytorchVersion: '未知'
            }
            return
        }
        
        const res = await axios.get(`${API_BASE}/api/device_info`, {
            timeout: 5000
        })
        if (res.data.success) {
            deviceInfo.value = {
                hasGpu: res.data.cuda_available || false,
                currentDevice: res.data.current_device || 'cpu',
                gpuName: res.data.devices?.find(d => d.type === 'GPU')?.name || '',
                devices: res.data.devices || [],
                pytorchVersion: res.data.pytorch_version || '未知'
            }
            console.log('✅ 设备信息加载成功:', deviceInfo.value)

            // 自动选择设备（只在当前设备未设置时）
            if (deviceInfo.value.currentDevice === '未设置' || deviceInfo.value.currentDevice === 'cpu') {
                if (deviceInfo.value.hasGpu) {
                    console.log('🔧 自动选择GPU')
                    await switchDevice('gpu')
                } else {
                    console.log('🔧 自动选择CPU')
                    selectedDevice.value = 'cpu'
                }
            } else {
                // 根据当前设备设置单选按钮
                selectedDevice.value = deviceInfo.value.currentDevice.includes('cuda') ? 'gpu' : 'cpu'
            }
        } else {
            // 如果API返回失败，使用默认值
            console.warn('❌ 设备信息API返回失败，使用默认值')
            deviceInfo.value = {
                hasGpu: false,
                currentDevice: 'cpu',
                gpuName: '',
                devices: [{ type: 'CPU', name: 'CPU', available: true }],
                pytorchVersion: '未知'
            }
        }
    } catch (err) {
        console.error('❌ 获取设备信息失败:', err)
        // 使用安全的默认值
        deviceInfo.value = {
            hasGpu: false,
            currentDevice: 'cpu',
            gpuName: '',
            devices: [{ type: 'CPU', name: 'CPU', available: true }],
            pytorchVersion: '未知'
        }

        // 显示错误提示（非阻塞）
        ElNotification({
            title: '设备信息获取失败',
            message: '使用CPU模式，不影响基本功能',
            type: 'warning',
            duration: 3000
        })
    } finally {
        loadingDevice.value = false
    }
}

// 切换设备,避免循环
// 修改 switchDevice 函数，确保异常处理
const switchDevice = async (deviceType) => {
    try {
        loadingDevice.value = true
        const res = await axios.post(`${API_BASE}/api/switch_device`, {
            device_type: deviceType
        }, {
            timeout: 5000
        })

        if (res.data.success) {
            // 更新设备信息，避免再次调用 loadDeviceInfo
            deviceInfo.value.currentDevice = res.data.device
            deviceInfo.value.hasGpu = deviceType === 'gpu'

            if (!res.data.message.includes('已在')) {
                ElNotification({
                    title: '设备切换成功',
                    message: `已切换到 ${res.data.device}`,
                    type: 'success',
                    duration: 2000
                })
            }
        }
    } catch (err) {
        console.error('切换设备失败:', err)
        ElNotification({
            title: '设备切换失败',
            message: '将使用CPU模式',
            type: 'error',
            duration: 3000
        })
        // 确保回到CPU模式
        deviceInfo.value.currentDevice = 'cpu'
        deviceInfo.value.hasGpu = false
        selectedDevice.value = 'cpu'
    } finally {
        loadingDevice.value = false
    }
}

// 设备变更处理 - 添加空值检查
const onDeviceChange = (deviceType) => {
    if (deviceType === 'gpu' && !deviceInfo.value?.hasGpu) {
        ElNotification({
            title: 'GPU不可用',
            message: '未检测到可用的GPU设备',
            type: 'warning',
            duration: 3000
        })
        selectedDevice.value = 'cpu'
        return
    }
    switchDevice(deviceType)
}

// 强制CPU变更处理
const onForceCpuChange = (value) => {
    if (value) {
        selectedDevice.value = 'cpu'
        switchDevice('cpu')
        ElNotification({
            title: '强制CPU模式',
            message: '已强制使用CPU进行检测',
            type: 'info',
            duration: 2000
        })
    }
}

// 刷新设备信息
const refreshDeviceInfo = async () => {
    await loadDeviceInfo()
}

// ==================== 计算属性 ====================
const avgConfidence = computed(() => {
  if (detections.value.length === 0) return 0
  const total = detections.value.reduce((sum, det) => sum + det.confidence, 0)
  return total / detections.value.length
})

// ==================== 生命周期钩子 ====================
onMounted(async () => {
    console.log('🚀 UploadView 开始初始化')
    console.log('🌐 当前URL:', window.location.href)
    console.log('🔧 API_BASE:', API_BASE)

    try {
        // 先检查后端连接状态
        await checkBackendStatus()
        console.log('✅ 后端连接状态检查完成')
        
        // 先加载模型列表
        await loadModelList()
        console.log('✅ 模型列表加载完成')

        // 然后加载设备信息
        await loadDeviceInfo()
        console.log('✅ 设备信息加载完成')

        // 最后加载历史记录
        await loadRecentRecords()
        console.log('✅ 历史记录加载完成')

        detectionCount.value = localStorage.getItem('detectionCount') || 0
        console.log('🎯 初始化完成')
        
        // 定期检查后端连接状态（每10秒）
        backendCheckInterval = setInterval(async () => {
            await checkBackendStatus()
        }, 10000)
        console.log('🔄 已启动后端连接定期检查')
    } catch (error) {
        console.error('❌ 初始化失败:', error)
    }
})

onUnmounted(() => {
    if (backendCheckInterval) {
        clearInterval(backendCheckInterval)
        console.log('🔄 已停止后端连接定期检查')
    }
})

// ==================== 方法 ====================
// 加载模型列表
const loadModelList = async () => {
  try {
    // 先检查后端连接
    const isConnected = await checkBackendStatus()
    if (!isConnected) {
      modelList.value = ['best.pt']
      selectedModel.value = 'best.pt'
      modelInfo.value = 'best.pt (默认)'
      return
    }
    
    const res = await axios.get(`${API_BASE}/api/models`)
    modelList.value = res.data
    if (modelList.value.length > 0) {
      selectedModel.value = modelList.value[0]
      modelInfo.value = selectedModel.value
    }
  } catch (err) {
    console.error('获取模型列表失败:', err)
    modelList.value = ['best.pt']
    selectedModel.value = 'best.pt'
    modelInfo.value = 'best.pt (默认)'
  }
}

// 加载最近记录
// 修改 loadRecentRecords 函数
const loadRecentRecords = async () => {
  try {
    // 正确的API端点
    const res = await axios.get('/api/history')

    // 确保返回的是数组
    const records = Array.isArray(res.data) ? res.data : []

    // 只取最近的5条，按时间倒序
    const recent = records
      .slice(0, 5)
      .map(record => {
        // 格式化时间
        let timeStr = '未知时间'
        if (record.detect_time) {
          try {
            const date = new Date(record.detect_time)
            timeStr = date.toLocaleString('zh-CN')
          } catch (e) {
            timeStr = record.detect_time
          }
        }

        return {
          name: record.filename || '未命名文件',
          time: timeStr,
          defects: record.total_objects || 0,
          id: record.id // 保留ID用于跳转
        }
      })

    recentRecords.value = recent
    console.log('✅ 加载最近记录成功:', recentRecords.value)
  } catch (err) {
    console.error('加载最近记录失败:', err)
    recentRecords.value = []

    // 显示错误提示（非阻塞）
    ElNotification({
      title: '加载记录失败',
      message: '无法加载历史记录，但可以继续检测',
      type: 'warning',
      duration: 3000
    })
  }
}

// 模型切换
const onModelChange = () => {
  modelInfo.value = selectedModel.value
  modelLoaded.value = true
}

// 拖拽相关事件
const onDragOver = () => {
  isDragOver.value = true
}

const onDragLeave = () => {
  isDragOver.value = false
}

const onDrop = (event) => {
  isDragOver.value = false
  const file = event.dataTransfer.files[0]
  handleFile(file)
}

// 触发文件选择
const triggerFileInput = () => {
  document.getElementById('file-input').click()
}

// 文件选择处理
const onFileSelected = (event) => {
  const file = event.target.files[0]
  handleFile(file)
}

// 处理文件
const handleFile = (file) => {
  if (!file) return

  // 验证文件类型
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png']
  if (!validTypes.includes(file.type)) {
    error.value = '请上传有效的图片文件（JPG/JPEG/PNG）'
    return
  }

  // 验证文件大小（限制10MB）
  if (file.size > 10 * 1024 * 1024) {
    error.value = '文件大小不能超过10MB'
    return
  }

  selectedFile.value = file
  error.value = ''
  detectionResult.value = null
  detections.value = []

  // 创建预览
  const reader = new FileReader()
  reader.onload = (e) => {
    originalImage.value = e.target.result
    resultImage.value = ''
  }
  reader.readAsDataURL(file)
}

// 清除文件
const clearFile = () => {
  selectedFile.value = null
  originalImage.value = ''
  resultImage.value = ''
  detections.value = []
  detectionResult.value = null
  document.getElementById('file-input').value = ''
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取文件类型
const getFileType = (mimeType) => {
  const types = {
    'image/jpeg': 'JPEG 图片',
    'image/jpg': 'JPG 图片',
    'image/png': 'PNG 图片'
  }
  return types[mimeType] || '未知文件'
}

// 格式化置信度
const formatConfidence = (value) => {
  return `置信度: ${value.toFixed(2)}`
}

// 格式化IoU
const formatIoU = (value) => {
  return `IoU: ${value.toFixed(2)}`
}

// 获取缺陷类型标签
const getDefectType = (type) => {
  const types = {
    '瓷质': 'success',
    '玻璃': 'primary',
    '复合': 'info',
    '污秽': 'warning',
    '锈蚀': 'danger',
    '破损': 'danger'
  }
  return types[type] || 'info'
}

// 获取置信度颜色
const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67C23A' // 绿色
  if (confidence >= 0.6) return '#E6A23C' // 黄色
  if (confidence >= 0.4) return '#F56C6C' // 红色
  return '#909399' // 灰色
}

// 查看检测详情
const viewDefectDetail = (defect) => {
  ElMessageBox.alert(
    `<div class="defect-detail">
      <h3>检测详情</h3>
      <p><strong>类型:</strong> ${defect.class}</p>
      <p><strong>置信度:</strong> ${(defect.confidence * 100).toFixed(1)}%</p>
      <p><strong>位置:</strong> (${defect.x1}, ${defect.y1}) → (${defect.x2}, ${defect.y2})</p>
      <p><strong>尺寸:</strong> ${Math.abs(defect.x2 - defect.x1)} × ${Math.abs(defect.y2 - defect.y1)} 像素</p>
    </div>`,
    '缺陷信息',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '确定'
    }
  )
}

// 2. 修改 detectImage 函数中的图片URL
// 检测图片
const detectImage = async () => {
  if (!selectedFile.value) {
    error.value = '请先选择一张图片'
    return
  }

  // 检查后端连接状态
  const isConnected = await checkBackendStatus()
  if (!isConnected) {
    error.value = '后端服务未连接，请检查后端是否运行'
    return
  }

  const formData = new FormData()
  formData.append('image', selectedFile.value)
  formData.append('model', selectedModel.value)
  formData.append('conf', confThreshold.value.toString())
  formData.append('iou', iouThreshold.value.toString())
  formData.append('use_gpu', (selectedDevice.value === 'gpu').toString())
  formData.append('force_cpu', forceCpu.value.toString())  // 添加强制CPU参数

  loading.value = true
  error.value = ''

  try {
    const response = await axios.post(`${API_BASE}/api/detect`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000
    })

    if (response.data.success) {
      detectionResult.value = response.data
      originalImage.value = `${API_BASE}${response.data.original}`
      resultImage.value = `${API_BASE}${response.data.result}`
      detections.value = response.data.detections || []

      ElNotification({
          title: '检测成功',
          message: `发现${detections.value.length}处缺陷，平均置信度${avgConfidence.value.toFixed(4)},使用设备: ${response.data.device_used || 'CPU'}`,
          type: 'success',
          duration: 3000
      })

      // 更新检测计数
      detectionCount.value++
      localStorage.setItem('detectionCount', detectionCount.value)

      // 重新加载最近记录
      await loadRecentRecords()
    } else {
      error.value = response.data.error || '检测失败'
    }
  } catch (err) {
    console.error('检测失败:', err)
    error.value = `检测失败: ${err.response?.data?.error || err.message}`

    // 如果是GPU错误，建议切换到CPU
    if (selectedDevice.value === 'gpu' && error.value.includes('CUDA')) {
        ElNotification({
            title: 'GPU错误',
            message: 'GPU检测失败，建议切换到CPU模式',
            type: 'error',
            duration: 4000
      })
    }
  } finally {
    loading.value = false
  }
}

const viewRecordDetail = (recordId) => {
  if (recordId) {
    // 跳转到历史记录页面或打开详情弹窗
    router.push({ path: '/history', query: { recordId } })
  }
}

// 保存到历史记录
const saveToHistory = async () => {
  try {
    // 这里调用后端保存接口
    // 实际已经在detect接口中保存了
    ElNotification({
      title: '保存成功',
      message: '检测结果已自动保存到历史记录',
      type: 'success',
      duration: 2000
    })
  } catch (err) {
    console.error('保存失败:', err)
    ElNotification({
      title: '保存失败',
      message: '保存失败，请重试',
      type: 'error',
      duration: 2000
    })
  }
}

// 导出为Excel
const exportToExcel = () => {
  if (detections.value.length === 0) {
    ElNotification({
      title: '导出失败',
      message: '没有检测结果可导出',
      type: 'warning',
      duration: 2000
    })
    return
  }

  import('xlsx').then(xlsx => {
    // 准备数据
    const data = [
      ['序号', '缺陷类型', '置信度', '位置坐标', '尺寸(像素)', '检测时间'],
      ...detections.value.map((det, idx) => [
        idx + 1,
        det.class,
        `${(det.confidence * 100).toFixed(1)}%`,
        `(${det.x1}, ${det.y1}) → (${det.x2}, ${det.y2})`,
        `${Math.abs(det.x2 - det.x1)} × ${Math.abs(det.y2 - det.y1)}`,
        new Date().toLocaleString()
      ])
    ]

    // 添加统计信息
    data.push([])
    data.push(['统计信息', '', '', '', '', ''])
    data.push(['总缺陷数', detections.value.length, '', '', '', ''])
    data.push(['平均置信度', `${avgConfidence.value.toFixed(4)}`, '', '', '', ''])
    data.push(['检测模型', selectedModel.value, '', '', '', ''])
    data.push(['检测时间', new Date().toLocaleString(), '', '', '', ''])

    // 创建Excel工作簿
    const worksheet = xlsx.utils.aoa_to_sheet(data)
    const workbook = xlsx.utils.book_new()
    xlsx.utils.book_append_sheet(workbook, worksheet, '检测结果')

    // 生成文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `绝缘子检测结果_${timestamp}.xlsx`

    // 导出文件
    xlsx.writeFile(workbook, filename)

    ElNotification({
      title: '导出成功',
      message: `文件已保存为: ${filename}`,
      type: 'success',
      duration: 3000
    })
  }).catch(err => {
    console.error('导出失败:', err)
    ElNotification({
      title: '导出失败',
      message: '请确保已安装xlsx库。如果未安装，请在项目目录下运行: npm install xlsx',
      type: 'error',
      duration: 3000
    })
  })
}

// 导航功能
const goToVideo = () => {
  router.push('/video')
}

const goToHistory = () => {
  router.push('/history')
}

const goToAbout = () => {
  router.push('/about')
}

const logout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '提示',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    // 用户点击确定
    router.push('/login')
  } catch (error) {
    // 用户点击取消，不需要处理
    if (error !== 'cancel' && error !== 'close') {
      console.warn('退出登录对话框错误:', error)
    }
  }
}

// 监听检测结果
watch(detections, (newVal) => {
  if (newVal.length > 0) {
    console.log(`检测到 ${newVal.length} 处缺陷`)
  }
})
</script>

<style scoped>
.upload-container {
  min-height: 100vh;
  /* 替换原有的渐变背景 */
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7eb 100%);

  /* 添加图片背景 */
  /*background-image: url('/1.png'); */ /*这里修改为图片相对路径---放于public目录
  /*background-size: cover; */      /* 使图片覆盖整个容器 */
  /*background-position: center; */ /* 居中显示 */
  /*background-attachment: fixed; */ /* 固定背景，内容滚动时背景不动 */
  /*background-repeat: no-repeat; */ /* 不重复 */

  font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', sans-serif;
}

/* 顶部导航栏 */
.top-nav {
  background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
  color: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-brand h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 图标保持原始颜色 */
.nav-brand h1 .icon-wrapper {
  color: white; /* 或者您想要的颜色，如 #409EFF */
  font-size: 32px;
}

/* 文字部分使用渐变色 */
.nav-brand h1 .title-text {
  background: linear-gradient(45deg, #fff, #a8edea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  margin: 5px 0 0 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.nav-menu {
  display: flex;
  gap: 15px;
  align-items: center;
}

.nav-btn {
  font-weight: 600;
  padding: 12px 24px;
  border-radius: 10px;
  transition: all 0.3s ease;
}

.nav-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 320px 1fr 320px;
  gap: 24px;
  padding: 30px;
  max-width: 1920px;
  margin: 0 auto;
}

/* 配置面板 */
.config-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.config-card {
  border-radius: 16px;
  border: none;
  background: white;
  color: #333; /* 添加默认深色文字 */
}

.config-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 20px;
  border-bottom: none;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: black; /* 标题文字保持白色 */
}

.card-header .el-icon {
  font-size: 24px;
  color: black; /* 标题图标保持白色 */
}

/* 模型选择器 */
.model-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.model-select {
  width: 100%;
}

.model-info {
  text-align: center;
}

.model-info .el-tag {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 8px;
  color: #333; /* 模型信息标签文字颜色 */
  background-color: #f0f9ff; /* 可调整背景色增加对比度 */
}

/* 设备选择器样式 */
.device-selector {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.device-status {
    text-align: center;
    padding: 12px;
    background: #f0f9ff;
    border-radius: 8px;
}

.device-status .el-tag {
    font-size: 16px;
    padding: 8px 16px;
    margin-bottom: 8px;
}

.device-desc {
    margin: 8px 0 0 0;
    color: #666;
    font-size: 14px;
}

.device-options {
    display: flex;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}

.device-option {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}

.force-cpu {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 8px;
    background: #f9f9f9;
    border-radius: 6px;
    font-size: 14px;
}

.device-actions {
    display: flex;
    justify-content: space-between;
    margin-top: 10px;
}

/* 参数控制 */
.param-item {
  padding: 16px 0;
}

.param-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: 600;
  color: #2c3e50;
}

/* 添加点击效果 */
.record-item {
  cursor: pointer;
  transition: all 0.3s ease;
}

.record-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 卡片内容区域文字颜色修正 */
.param-label span {
  color: #2c3e50; /* 确保参数标签可见 */
}


.param-control :deep(.el-slider) {
  margin: 8px 0;
}

.param-desc {
  font-size: 12px;
  color: #7f8c8d;
  margin-top: 8px;
  line-height: 1.5;
}

/* 快速操作 */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
}

/* 上传区域 */
.upload-area {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.upload-card {
  border-radius: 16px;
  background: white;
  min-height: 400px;
}

.upload-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.upload-header .el-icon {
  font-size: 24px;
  color: #667eea;
}

/* 上传区域 */
.upload-zone {
  border: 3px dashed #e0e0e0;
  border-radius: 16px;
  padding: 60px 40px;
  background: #fafafa;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-zone:hover {
  border-color: #667eea;
  background: #f0f4ff;
}

.upload-zone.drag-over {
  border-color: #667eea;
  background: #e8edff;
  transform: scale(1.02);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.upload-icon {
  color: #667eea;
}

.upload-text h3 {
  margin: 0 0 8px 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.upload-text p {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.select-btn {
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
}

/* 文件预览 */
.file-preview {
  width: 100%;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 12px;
  margin-bottom: 20px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-info .el-icon {
  font-size: 32px;
  color: #667eea;
}

.file-details h4 {
  margin: 0 0 4px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.file-details p {
  margin: 0;
  color: #7f8c8d;
  font-size: 14px;
}

.preview-image {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.preview-image img {
  width: 100%;
  height: auto;
  display: block;
  transition: transform 0.3s ease;
}

.preview-image:hover img {
  transform: scale(1.02);
}

.preview-overlay {
  position: absolute;
  top: 16px;
  right: 16px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.preview-image:hover .preview-overlay {
  opacity: 1;
}

/* 错误提示 */
.error-alert {
  margin-top: 20px;
}

.error-alert :deep(.el-alert) {
  border-radius: 12px;
}

/* 结果部分 */
.result-card {
  border-radius: 16px;
  background: white;
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
}

.result-header .el-icon {
  font-size: 24px;
  color: #67C23A;
}

/* 图像对比 */
.image-comparison {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  margin: 40px 0;
  padding: 40px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 20px;
}

.comparison-item {
  flex: 1;
  max-width: 400px;
}

.comparison-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.comparison-image {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  transition: transform 0.3s ease;
}

.comparison-image:hover {
  transform: translateY(-4px);
}

.comparison-image img {
  width: 100%;
  height: auto;
  display: block;
}

.image-label {
  position: absolute;
  bottom: 16px;
  left: 16px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.comparison-arrow {
  color: #667eea;
}

/* 检测统计 */
.detection-stats {
  margin: 40px 0;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-4px);
  background: white;
}

.stat-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  font-size: 28px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

/* 检测表格 */
.detection-table {
  margin: 40px 0;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.table-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.table-actions {
  display: flex;
  gap: 10px;
}

.defect-table {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.defect-table :deep(.el-table__row) {
  transition: all 0.3s ease;
}

.defect-table :deep(.el-table__row:hover) {
  background-color: #f8f9fa;
  transform: translateY(-2px);
}

.confidence-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.confidence-cell :deep(.el-progress) {
  flex: 1;
}

.confidence-text {
  font-weight: 600;
  color: #2c3e50;
  min-width: 60px;
  text-align: right;
}

.coordinate-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.coordinate-point {
  padding: 4px 8px;
  background: #f8f9fa;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.bounding-box {
  text-align: center;
}

.box-dimensions {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.box-unit {
  font-size: 12px;
  color: #7f8c8d;
}

/* 无缺陷提示 */
.no-defects {
  padding: 60px 40px;
  text-align: center;
  background: linear-gradient(135deg, #f8fff8 0%, #e8f5e9 100%);
  border-radius: 20px;
  margin: 40px 0;
}

.no-defects-content h3 {
  margin: 20px 0 10px 0;
  color: #67C23A;
  font-size: 24px;
  font-weight: 600;
}

.no-defects-content p {
  color: #7f8c8d;
  font-size: 16px;
}

/* 信息面板 */
.info-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card {
  border-radius: 16px;
  background: white;
}

/* 状态列表 */
.status-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.status-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.status-label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #2c3e50;
  font-weight: 500;
}

/* 最近记录 */
.recent-records {
  min-height: 200px;
}

.empty-records {
  padding: 40px 0;
}

.record-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
  width: 100%; /* 确保宽度充满容器 */
  box-sizing: border-box; /* 包含padding和border */
}

.record-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.record-time {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #667eea;
  font-size: 12px;
  font-weight: 500;
  min-width: 120px;
}

/* 记录信息容器 - 添加宽度限制 */
.record-info {
  flex: 1;
  min-width: 0; /* 关键！允许flex项缩小到小于内容大小 */
}

/* 记录名称 - 添加文本溢出处理 */
.record-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 4px;
  overflow: hidden;
  overflow: hidden; /* 溢出隐藏 */
  text-overflow: ellipsis; /* 显示省略号 */
  white-space: nowrap; /* 不换行 */
  width: 100%; /* 充满父容器 */
  display: block; /* 块级元素 */
}

.record-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

/* 提示列表 */
.tips-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: linear-gradient(135deg, #f0f7ff 0%, #e6f2ff 100%);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.tip-item:hover {
  background: linear-gradient(135deg, #e6f2ff 0%, #d9ebff 100%);
  transform: translateX(4px);
}

.tip-item .el-icon {
  color: #667eea;
  margin-top: 2px;
}

.tip-item span {
  color: #2c3e50;
  font-size: 14px;
  line-height: 1.5;
}

/* 页脚 */
.footer {
  margin-top: 60px;
  padding: 40px 0;
  background: linear-gradient(135deg, #2c3e50 0%, #1a2530 100%);
  color: white;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 40px;
}

.footer-info p, .footer-contact p {
  margin: 8px 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.footer-info p:first-child {
  font-size: 16px;
  font-weight: 600;
  color: white;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .main-content {
    grid-template-columns: 280px 1fr 280px;
    gap: 20px;
    padding: 20px;
  }
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .config-panel,
  .info-panel {
    order: 2;
  }

  .upload-area {
    order: 1;
  }

  .image-comparison {
    flex-direction: column;
    gap: 30px;
  }
}

@media (max-width: 768px) {
  .top-nav {
    flex-direction: column;
    gap: 20px;
    padding: 20px;
    text-align: center;
  }

  .nav-menu {
    flex-wrap: wrap;
    justify-content: center;
  }

  .main-content {
    padding: 16px;
  }

  .upload-zone {
    padding: 40px 20px;
  }

  .upload-content h3 {
    font-size: 20px;
  }

  .detection-stats .el-col {
    margin-bottom: 16px;
  }

  .footer-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.result-card {
  animation: fadeIn 0.6s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.config-card {
  animation: slideIn 0.4s ease-out;
}

/* 优化动画 */
@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.7; }
  100% { opacity: 1; }
}

.upload-zone.drag-over {
  animation: pulse 2s infinite;
}

</style>
