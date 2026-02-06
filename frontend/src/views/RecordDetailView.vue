<!-- src/views/RecordDetailView.vue -->

<template>
  <div class="record-detail-container">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-brand">
        <h1>📋 检测记录详情</h1>
        <p class="subtitle" v-if="record.id">记录ID: {{ record.id }}</p>
        <p class="subtitle" v-else>加载中...</p>
      </div>
      <div class="nav-actions">
        <el-button @click="goBack" type="info" size="large">
          <el-icon><ArrowLeft /></el-icon>
          返回列表
        </el-button>
        <el-button @click="exportToPDF" type="primary" size="large">
          <el-icon><Document /></el-icon>
          导出PDF报告
        </el-button>
        <el-button @click="shareRecord" type="success" size="large">
          <el-icon><Share /></el-icon>
          分享记录
        </el-button>
        <el-button @click="deleteRecord" type="danger" size="large">
          <el-icon><Delete /></el-icon>
          删除记录
        </el-button>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="loading-icon"><Loading /></el-icon>
      <p>正在加载记录详情...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <el-icon><Warning /></el-icon>
      <h3>加载失败</h3>
      <p>{{ error }}</p>
      <el-button @click="retryLoad"
        type="primary">重试</el-button>
    </div>

    <!-- 记录详情内容 -->
    <div v-else class="detail-content" id="pdf-content">
      <!-- 基本信息卡片 -->
      <div class="info-section">
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>基本信息</span>
            </div>
          </template>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">记录ID</span>
              <span class="info-value">{{ record.id }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">文件名称</span>
              <span class="info-value" :title="record.filename">
                {{ shortenFilename(record.filename, 40) }}
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">检测类型</span>
              <el-tag :type="getTypeTagType(record.detection_type)"
                size="large">
                {{ getTypeLabel(record.detection_type) }}
              </el-tag>
            </div>
            <div class="info-item">
              <span class="info-label">检测时间</span>
              <span class="info-value">{{ formatDateTime(record.detect_time) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">使用模型</span>
              <span class="info-value">{{ record.model_used || 'best.pt' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">处理时长</span>
              <span class="info-value" v-if="record.duration">
                {{ record.duration.toFixed(2) }}秒
              </span>
              <span class="info-value" v-else>--</span>
            </div>
          </div>
        </el-card>

        <!-- 参数卡片 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Setting /></el-icon>
              <span>检测参数</span>
            </div>
          </template>
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">置信度阈值</span>
              <span class="info-value">{{ (record.confidence_threshold || 0.25).toFixed(2) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">IoU阈值</span>
              <span class="info-value">{{ (record.iou_threshold || 0.45).toFixed(2) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">平均置信度</span>
              <span class="info-value">{{ ((record.confidence_avg || 0) * 100).toFixed(2) }}%</span>
            </div>
            <div class="info-item">
              <span class="info-label">检测数量</span>
              <span class="info-value">{{ record.total_objects || 0 }}</span>
            </div>
            <div v-if="record.frame_count" class="info-item">
              <span class="info-label">处理帧数</span>
              <span class="info-value">{{ record.frame_count }}</span>
            </div>
            <div v-if="record.fps" class="info-item">
              <span class="info-label">处理帧率</span>
              <span class="info-value">{{ record.fps.toFixed(2) }} FPS</span>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 图像/视频对比 -->
      <div class="media-section" v-if="record.detection_type === 'image' || record.detection_type === 'video'">
        <el-card class="media-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Picture /></el-icon>
              <span>图像对比</span>
            </div>
          </template>
          <div class="media-comparison">
            <div class="media-box">
              <h3>原始图像</h3>
              <div class="media-container">
                <img
                  v-if="record.detection_type === 'image'"
                  :src="getImageUrl(record.filename, 'uploads')"
                  :alt="record.filename"
                  class="detail-image"
                  @load="handleImageLoad"
                  @error="handleImageError"
                />
                <video
                  v-else-if="record.detection_type === 'video'"
                  :src="getVideoUrl(record.video_path || record.filename, 'uploads')"
                  controls
                  class="detail-video"
                ></video>
                <div v-if="!mediaLoaded.original" class="media-loading">
                  <el-icon><Loading /></el-icon>
                  <span>加载中...</span>
                </div>
              </div>
              <div class="media-info">
                <p><strong>文件:</strong> {{ getFileName(record.filename) }}</p>
                <p v-if="record.duration"><strong>时长:</strong> {{ record.duration.toFixed(2) }}秒</p>
              </div>
            </div>

            <div class="media-box">
              <h3>检测结果</h3>
              <div class="media-container">
                <img
                  v-if="record.detection_type === 'image' && record.result_filename"
                  :src="getImageUrl(record.result_filename, 'results')"
                  :alt="record.result_filename"
                  class="detail-image"
                  @load="handleResultImageLoad"
                  @error="handleResultImageError"
                />
                <video
                  v-else-if="record.detection_type === 'video' && record.processed_video_path"
                  :src="getVideoUrl(record.processed_video_path, 'results')"
                  controls
                  class="detail-video"
                ></video>
                <div v-else class="media-no-result">
                  <el-icon><Picture /></el-icon>
                  <span>暂无结果图像</span>
                </div>
                <div v-if="!mediaLoaded.result && record.result_filename" class="media-loading">
                  <el-icon><Loading /></el-icon>
                  <span>加载中...</span>
                </div>
              </div>
              <div class="media-info">
                <p v-if="record.result_filename"><strong>文件:</strong> {{ getFileName(record.result_filename) }}</p>
                <p v-if="record.total_objects"><strong>检测数量:</strong> {{ record.total_objects }}</p>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 检测详情表格 -->
      <div class="detection-section" v-if="detections.length > 0">
        <el-card class="detection-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><List /></el-icon>
              <span>检测详情 (共 {{ detections.length }} 个目标)</span>
            </div>
          </template>
          <div class="table-container">
            <el-table :data="detections" style="width: 100%" stripe>
              <el-table-column prop="index" label="序号" width="60"
                align="center">
                <template #default="{ $index }">
                  {{ $index + 1 }}
                </template>
              </el-table-column>
              <el-table-column prop="class" label="检测类别" width="120">
                <template #default="{ row }">
                  <el-tag :type="getDefectType(row.class)" size="small">
                    {{ row.class }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="confidence" label="置信度" width="120"
                sortable>
                <template #default="{ row }">
                  <div class="confidence-cell">
                    <el-progress
                      :percentage="Math.round(row.confidence * 100)"
                      :show-text="false"
                      :color="getConfidenceColor(row.confidence)"
                    />
                    <span class="confidence-text">{{ (row.confidence * 100).toFixed(1) }}%</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="bbox" label="边界框位置" width="200">
                <template #default="{ row }">
                  <div class="bbox-info">
                    <div class="bbox-coord">
                      <span class="coord-label">左上:</span>
                      <span class="coord-value">({{ row.x1 }}, {{ row.y1 }})</span>
                    </div>
                    <div class="bbox-coord">
                      <span class="coord-label">右下:</span>
                      <span class="coord-value">({{ row.x2 }}, {{ row.y2 }})</span>
                    </div>
                    <div class="bbox-size">
                      <span class="size-label">尺寸:</span>
                      <span class="size-value">{{ row.x2 - row.x1 }} × {{ row.y2 - row.y1 }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="area" label="面积" width="100"
                sortable>
                <template #default="{ row }">
                  {{ (row.x2 - row.x1) * (row.y2 - row.y1) }} px²
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row, $index }">
                  <el-button-group>
                    <el-button
                      @click="highlightDetection(row)"
                      type="primary"
                      size="small"
                      title="高亮显示"
                    >
                      <el-icon><View /></el-icon>
                    </el-button>
                    <el-button
                      @click="exportDetection(row, $index)"
                      type="success"
                      size="small"
                      title="导出信息"
                    >
                      <el-icon><Download /></el-icon>
                    </el-button>
                  </el-button-group>
                </template>
              </el-table-column>
            </el-table>

            <!-- 表格操作 -->
            <div class="table-actions">
              <el-button @click="exportTableToExcel" type="primary">
                <el-icon><Document /></el-icon>
                导出Excel
              </el-button>
              <el-button @click="exportTableToCSV" type="success">
                <el-icon><Document /></el-icon>
                导出CSV
              </el-button>
              <el-button @click="copyTableData" type="info">
                <el-icon><CopyDocument /></el-icon>
                复制数据
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 统计信息 -->
      <div class="stats-section" v-if="detections.length > 0">
        <el-card class="stats-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>统计信息</span>
            </div>
          </template>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ detections.length }}</div>
                <div class="stat-label">总检测数量</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><TrendCharts /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ calculateAverageConfidence() }}%</div>
                <div class="stat-label">平均置信度</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><PieChart /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ getDefectCount() }}</div>
                <div class="stat-label">缺陷数量</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Collection /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ getInsulatorCount() }}</div>
                <div class="stat-label">绝缘子数量</div>
              </div>
            </div>
          </div>

          <!-- 类别分布图表 -->
          <div class="chart-container" v-if="detections.length > 0">
            <div class="chart-grid">
              <div class="chart-item">
                <h4>绝缘子类别分布</h4>
                <div class="chart-wrapper">
                  <canvas ref="insulatorChartCanvas"></canvas>
                </div>
              </div>
              <div class="chart-item">
                <h4>缺陷类别分布</h4>
                <div class="chart-wrapper">
                  <canvas ref="defectChartCanvas"></canvas>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 无检测结果 -->
      <div v-else class="no-detections">
        <el-card class="empty-card" shadow="hover">
          <div class="empty-content">
            <el-icon size="80"><DataBoard /></el-icon>
            <h3>未检测到缺陷</h3>
            <p>此记录中未检测到任何绝缘子缺陷</p>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 图片高亮弹窗 -->
    <el-dialog
      v-model="highlightDialogVisible"
      title="缺陷位置高亮"
      width="80%"
      top="5vh"
      destroy-on-close
    >
      <div class="highlight-content">
        <div class="highlight-image">
          <canvas ref="highlightCanvas"
            class="highlight-canvas"></canvas>
        </div>
        <div class="highlight-info">
          <h4>缺陷信息</h4>
          <div class="highlight-details" v-if="highlightedDetection">
            <p><strong>类别:</strong> {{ highlightedDetection.class }}</p>
            <p><strong>置信度:</strong> {{ (highlightedDetection.confidence * 100).toFixed(1) }}%</p>
            <p><strong>位置:</strong> ({{ highlightedDetection.x1 }}, {{ highlightedDetection.y1 }}) - ({{ highlightedDetection.x2 }}, {{ highlightedDetection.y2 }})</p>
            <p><strong>尺寸:</strong> {{ highlightedDetection.x2 - highlightedDetection.x1 }} × {{ highlightedDetection.y2 - highlightedDetection.y1 }}</p>
            <p><strong>面积:</strong> {{ (highlightedDetection.x2 - highlightedDetection.x1) * (highlightedDetection.y2 - highlightedDetection.y1) }} px²</p>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { Chart, registerables } from 'chart.js'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import {
  ArrowLeft, Document, Share, Delete, Loading, Warning,
  InfoFilled, Setting, Picture, List, View, Download,
  CopyDocument, DataAnalysis, Collection, TrendCharts, PieChart,
  DataBoard
} from '@element-plus/icons-vue'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

// 定义props
const props = defineProps({
  recordId: {
    type: [Number, String],
    required: true
  }
})

// 注册Chart.js组件
Chart.register(...registerables)

const router = useRouter()
const route = useRoute()

// 响应式数据
const record = ref({})
const detections = ref([])
const loading = ref(true)
const error = ref('')
const mediaLoaded = ref({
  original: false,
  result: false
})
const highlightDialogVisible = ref(false)
const highlightedDetection = ref(null)
const insulatorChartCanvas = ref(null)
const defectChartCanvas = ref(null)
const highlightCanvas = ref(null)
let insulatorChartInstance = null
let defectChartInstance = null

// ==================== API基础地址 ====================
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

const apiBaseUrl = getApiBase()
console.log('🔧 API基础地址:', apiBaseUrl)

// 生命周期钩子
onMounted(() => {
  loadRecordDetail()
})

onUnmounted(() => {
  if (insulatorChartInstance) {
    insulatorChartInstance.destroy()
  }
  if (defectChartInstance) {
    defectChartInstance.destroy()
  }
})

// 监听recordId变化
watch(() => props.recordId, (newVal) => {
  if (newVal) {
    loadRecordDetail()
  }
})

// 方法
const loadRecordDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    // 优先使用路由参数id，其次使用props.recordId
    const recordId = route.params.id || props.recordId

    // 添加参数检查
    if (!recordId || recordId === 'undefined') {
      error.value = '记录ID参数无效'
      loading.value = false
      return
    }

    console.log('正在加载记录ID:', recordId)

    const response = await axios.get(`${apiBaseUrl}/api/records/${recordId}`)

    console.log('详情API响应:', response.data)

    if (response.data.record) {
      record.value = response.data.record
      detections.value = response.data.detections || []

      // 确保detections有索引
      detections.value.forEach((det, index) => {
        det.index = index + 1
      })

      // 初始化图表
      nextTick(() => {
        initCharts()
      })
    } else {
      error.value = '未找到记录详情'
    }
  } catch (err) {
    console.error('加载记录详情失败:', err)

    // 更详细的错误处理
    if (err.response?.status === 404) {
      error.value = '记录不存在，可能已被删除'
    } else if (err.response?.status === 400) {
      error.value = '请求参数错误'
    } else if (err.response?.status === 500) {
      error.value = '服务器内部错误，请稍后重试'
    } else if (err.code === 'ERR_NETWORK') {
      error.value = '网络连接失败，请检查后端服务是否运行'
    } else {
      error.value = err.response?.data?.error || '加载记录详情失败，请检查网络连接'
    }
  } finally {
    loading.value = false
  }
}

const retryLoad = () => {
  loadRecordDetail()
}

const goBack = () => {
  // 跳转到历史记录页面
  router.push('/history')
}

const getFileName = (path) => {
  if (!path) return ''
  return path.split('/').pop() || path
}

const shortenFilename = (filename, maxLength = 30) => {
  if (!filename || filename.length <= maxLength) return filename
  const parts = filename.split('.')
  const ext = parts.pop()
  const name = parts.join('.')
  return name.substring(0, maxLength - 3) + '...' + ext
}

const getTypeLabel = (type) => {
  const types = {
    'image': '图片检测',
    'video': '视频检测',
    'camera': '摄像头检测'
  }
  return types[type] || '未知类型'
}

const getTypeTagType = (type) => {
  const types = {
    'image': 'success',
    'video': 'primary',
    'camera': 'warning'
  }
  return types[type] || 'info'
}

const formatDateTime = (date) => {
  if (!date) return '--'
  return new Date(date).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getImageUrl = (filename, type = 'uploads') => {
  if (!filename) return ''
  return `${apiBaseUrl}/static/${type}/${filename}?t=${Date.now()}`
}

const getVideoUrl = (filename, type = 'uploads') => {
  if (!filename) return ''
  return `${apiBaseUrl}/static/${type}/${filename}`
}

const handleImageLoad = () => {
  mediaLoaded.value.original = true
}

const handleImageError = (e) => {
  console.error('原始图像加载失败:', e.target.src)
  e.target.src = 'https://via.placeholder.com/400x300?text=图片加载失败'
}

const handleResultImageLoad = () => {
  mediaLoaded.value.result = true
}

const handleResultImageError = (e) => {
  console.error('结果图像加载失败:', e.target.src)
  e.target.src = 'https://via.placeholder.com/400x300?text=结果图片加载失败'
}

const getDefectType = (className) => {
  const types = {
    '瓷质': 'success',
    '玻璃': 'info',
    '复合': '',
    '污秽': 'warning',
    '锈蚀': 'warning',
    '破损': 'danger'
  }
  return types[className] || ''
}

const getConfidenceColor = (confidence) => {
  if (confidence >= 0.8) return '#67C23A'
  if (confidence >= 0.6) return '#E6A23C'
  if (confidence >= 0.4) return '#F56C6C'
  return '#909399'
}

const calculateAverageConfidence = () => {
  if (detections.value.length === 0) return 0
  const total = detections.value.reduce((sum, det) => sum + det.confidence, 0)
  return ((total / detections.value.length) * 100).toFixed(1)
}

const getDefectCountByType = (type) => {
  return detections.value.filter(det => det.class === type).length
}

const getDefectCount = () => {
  const defectTypes = ['破损', '污秽', '锈蚀']
  return detections.value.filter(det => defectTypes.includes(det.class)).length
}

const getInsulatorCount = () => {
  const insulatorTypes = ['瓷质', '玻璃', '复合']
  return detections.value.filter(det => insulatorTypes.includes(det.class)).length
}

const initCharts = () => {
  if (detections.value.length === 0) return
  initInsulatorChart()
  initDefectChart()
}

const initInsulatorChart = () => {
  if (!insulatorChartCanvas.value) return

  if (insulatorChartInstance) {
    insulatorChartInstance.destroy()
  }

  // 统计绝缘子类别分布
  const insulatorTypes = ['瓷质', '玻璃', '复合']
  const classCounts = {}
  
  // 初始化所有绝缘子类型的计数为0
  insulatorTypes.forEach(type => {
    classCounts[type] = 0
  })
  
  // 统计实际检测到的绝缘子类型
  detections.value.forEach(det => {
    const className = det.class
    if (insulatorTypes.includes(className)) {
      classCounts[className] = (classCounts[className] || 0) + 1
    }
  })

  const labels = Object.keys(classCounts)
  const data = Object.values(classCounts)

  // 设置颜色
  const backgroundColors = [
    '#36A2EB', '#4BC0C0', '#9966FF'
  ]

  const ctx = insulatorChartCanvas.value.getContext('2d')
  insulatorChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: backgroundColors.slice(0, labels.length),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || ''
              const value = context.raw || 0
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = total > 0 ? Math.round((value / total) * 100) : 0
              return `${label}: ${value} (${percentage}%)`
            }
          }
        }
      }
    }
  })
}

const initDefectChart = () => {
  if (!defectChartCanvas.value) return

  if (defectChartInstance) {
    defectChartInstance.destroy()
  }

  // 统计缺陷类别分布
  const defectTypes = ['破损', '污秽', '锈蚀']
  const classCounts = {}
  
  // 初始化所有缺陷类型的计数为0
  defectTypes.forEach(type => {
    classCounts[type] = 0
  })
  
  // 统计实际检测到的缺陷类型
  detections.value.forEach(det => {
    const className = det.class
    if (defectTypes.includes(className)) {
      classCounts[className] = (classCounts[className] || 0) + 1
    }
  })

  const labels = Object.keys(classCounts)
  const data = Object.values(classCounts)

  // 设置颜色
  const backgroundColors = [
    '#FF6384', '#FFCE56', '#FF9F40'
  ]

  const ctx = defectChartCanvas.value.getContext('2d')
  defectChartInstance = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: backgroundColors.slice(0, labels.length),
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: 'right',
          labels: {
            font: {
              size: 12
            }
          }
        },
        tooltip: {
          callbacks: {
            label: (context) => {
              const label = context.label || ''
              const value = context.raw || 0
              const total = context.dataset.data.reduce((a, b) => a + b, 0)
              const percentage = total > 0 ? Math.round((value / total) * 100) : 0
              return `${label}: ${value} (${percentage}%)`
            }
          }
        }
      }
    }
  })
}

const highlightDetection = (detection) => {
  highlightedDetection.value = detection
  highlightDialogVisible.value = true
  nextTick(() => {
    drawHighlightedDetection()
  })
}

const drawHighlightedDetection = () => {
  const canvas = highlightCanvas.value
  if (!canvas || !highlightedDetection.value) return

  const ctx = canvas.getContext('2d')
  const img = new Image()
  img.crossOrigin = 'anonymous'

  img.onload = () => {
    // 设置canvas尺寸
    canvas.width = img.width
    canvas.height = img.height

    // 绘制原始图像
    ctx.drawImage(img, 0, 0)

    // 绘制高亮框
    const det = highlightedDetection.value
    ctx.strokeStyle = '#FF0000'
    ctx.lineWidth = 3
    ctx.strokeRect(det.x1, det.y1, det.x2 - det.x1, det.y2 - det.y1)

    // 绘制标签背景
    ctx.fillStyle = 'rgba(255, 0, 0, 0.7)'
    ctx.fillRect(det.x1, det.y1 - 25, 150, 25)

    // 绘制标签文本
    ctx.fillStyle = '#FFFFFF'
    ctx.font = 'bold 14px Arial'
    ctx.fillText(
      `${det.class} (${(det.confidence * 100).toFixed(1)}%)`,
      det.x1 + 5,
      det.y1 - 8
    )
  }

  img.onerror = () => {
    console.error('高亮图像加载失败')
    ctx.fillStyle = '#f8f9fa'
    ctx.fillRect(0, 0, canvas.width, canvas.height)
    ctx.fillStyle = '#666'
    ctx.font = '16px Arial'
    ctx.fillText('图像加载失败', 10, 30)
  }

  // 优先使用结果图像，如果没有则使用原始图像
  const imgUrl = record.value.result_filename
    ? getImageUrl(record.value.result_filename, 'results')
    : getImageUrl(record.value.filename, 'uploads')

  img.src = imgUrl
}

const exportDetection = (detection, index) => {
  const data = {
    序号: index + 1,
    检测类别: detection.class,
    置信度: `${(detection.confidence * 100).toFixed(2)}%`,
    左上角坐标: `(${detection.x1}, ${detection.y1})`,
    右下角坐标: `(${detection.x2}, ${detection.y2})`,
    宽度: detection.x2 - detection.x1,
    高度: detection.y2 - detection.y1,
    面积: (detection.x2 - detection.x1) * (detection.y2 - detection.y1)
  }

  const blob = new Blob([JSON.stringify(data, null, 2)], {
    type: 'application/json'
  })

  saveAs(blob, `检测记录_${record.value.id}_缺陷_${index + 1}.json`)
}

const exportTableToExcel = () => {
  if (detections.value.length === 0) {
    ElNotification({
      title: '导出失败',
      message: '没有可导出的数据',
      type: 'warning',
      duration: 2000
    })
    return
  }

  const data = detections.value.map((det, index) => ({
    序号: index + 1,
    检测类别: det.class,
    置信度: `${(det.confidence * 100).toFixed(2)}%`,
    左上角X: det.x1,
    左上角Y: det.y1,
    右下角X: det.x2,
    右下角Y: det.y2,
    宽度: det.x2 - det.x1,
    高度: det.y2 - det.y1,
    面积: (det.x2 - det.x1) * (det.y2 - det.y1)
  }))

  const ws = XLSX.utils.json_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '检测详情')

  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  const blob = new Blob([excelBuffer], {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  })

  const timestamp = new Date().toISOString().replace(/[-:.]/g, '')
  saveAs(blob, `检测记录_${record.value.id}_详情_${timestamp}.xlsx`)

  ElNotification({
    title: '导出成功',
    message: 'Excel文件已生成',
    type: 'success',
    duration: 2000
  })
}

const exportTableToCSV = () => {
  if (detections.value.length === 0) {
    ElNotification({
      title: '导出失败',
      message: '没有可导出的数据',
      type: 'warning',
      duration: 2000
    })
    return
  }

  const headers = ['序号', '检测类别', '置信度', '左上角X', '左上角Y', '右下角X', '右下角Y', '宽度', '高度', '面积']
  const rows = detections.value.map((det, index) => [
    index + 1,
    det.class,
    `${(det.confidence * 100).toFixed(2)}%`,
    det.x1,
    det.y1,
    det.x2,
    det.y2,
    det.x2 - det.x1,
    det.y2 - det.y1,
    (det.x2 - det.x1) * (det.y2 - det.y1)
  ])

  const csvContent = [
    headers.join(','),
    ...rows.map(row => row.join(','))
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], {
    type: 'text/csv;charset=utf-8'
  })

  const timestamp = new Date().toISOString().replace(/[-:.]/g, '')
  saveAs(blob, `检测记录_${record.value.id}_详情_${timestamp}.csv`)

  ElNotification({
    title: '导出成功',
    message: 'CSV文件已生成',
    type: 'success',
    duration: 2000
  })
}

const copyTableData = () => {
  if (detections.value.length === 0) {
    ElNotification({
      title: '复制失败',
      message: '没有可复制的数据',
      type: 'warning',
      duration: 2000
    })
    return
  }

  const text = detections.value.map((det, index) =>
    `${index + 1}. ${det.class} - ${(det.confidence * 100).toFixed(1)}%`
  ).join('\n')

  navigator.clipboard.writeText(text).then(() => {
    ElNotification({
      title: '复制成功',
      message: '数据已复制到剪贴板',
      type: 'success',
      duration: 2000
    })
  })
}

const exportToPDF = async () => {
  try {
    ElNotification({
      title: 'PDF生成',
      message: '正在生成PDF报告，请稍候...',
      type: 'info',
      duration: 3000
    })

    const element = document.getElementById('pdf-content')

    // 使用html2canvas将元素转换为canvas
    const canvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false
    })

    // 获取图片数据
    const imgData = canvas.toDataURL('image/png')

    // 创建PDF
    const pdf = new jsPDF('p', 'mm', 'a4')
    const imgWidth = 210
    const imgHeight = canvas.height * imgWidth / canvas.width

    pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight)

    // 保存PDF
    const timestamp = new Date().toISOString().replace(/[-:.]/g, '')
    pdf.save(`检测报告_${timestamp}.pdf`)

    ElNotification({
      title: '导出成功',
      message: 'PDF报告已生成',
      type: 'success',
      duration: 2000
    })
  } catch (err) {
    console.error('生成PDF失败:', err)
    ElNotification({
      title: '生成失败',
      message: '生成PDF报告失败',
      type: 'error',
      duration: 3000
    })
  }
}

const shareRecord = () => {
  const shareUrl = `${window.location.origin}/record/${record.value.id}`
  navigator.clipboard.writeText(shareUrl).then(() => {
    ElNotification({
      title: '复制成功',
      message: '分享链接已复制到剪贴板',
      type: 'success',
      duration: 2000
    })
  })
}

const deleteRecord = async () => {
  try {
    const result = await ElMessageBox.confirm(
      `确定要删除记录 "${record.value.filename}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    if (result === 'confirm') {
      const response = await axios.delete(`${apiBaseUrl}/api/records/${record.value.id}`)

      if (response.data.success) {
        ElNotification({
          title: '删除成功',
          message: '记录已删除',
          type: 'success',
          duration: 2000
        })

        // 返回历史记录页面
        setTimeout(() => {
          goBack()
        }, 1000)
      }
    }
  } catch (err) {
    if (err.response && err.response.status === 404) {
      ElNotification({
        title: '删除失败',
        message: '记录不存在或已被删除',
        type: 'error',
        duration: 3000
      })
    } else {
      console.error('删除记录失败:', err)
      ElNotification({
        title: '删除失败',
        message: '删除记录失败，请重试',
        type: 'error',
        duration: 3000
      })
    }
  }
}

// 导入Element Plus组件
import { ElNotification, ElMessageBox } from 'element-plus'
</script>

<style scoped>
.record-detail-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
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
}

.subtitle {
  margin: 5px 0 0 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
}

.nav-actions {
  display: flex;
  gap: 12px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #409EFF;
}

.loading-icon {
  font-size: 48px;
  margin-bottom: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 错误状态 */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: #F56C6C;
  text-align: center;
}

.error-state .el-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.error-state h3 {
  margin: 0 0 10px 0;
  font-size: 24px;
}

/* 详情内容 */
.detail-content {
  padding: 30px;
  max-width: 1600px;
  margin: 0 auto;
}

/* 信息区域 */
.info-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.info-card {
  border-radius: 16px;
  background: white;
}

.info-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 16px 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
}

.info-label {
  font-size: 12px;
  color: #6c757d;
  font-weight: 500;
}

.info-value {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

/* 媒体对比区域 */
.media-section {
  margin-bottom: 30px;
}

.media-card {
  border-radius: 16px;
  background: white;
}

.media-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 16px 20px;
}

.media-comparison {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
  padding: 20px;
}

.media-box {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.media-box h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.media-container {
  position: relative;
  width: 100%;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.detail-video {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}

.media-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  color: #409EFF;
  gap: 10px;
}

.media-no-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 15px;
  color: #6c757d;
  height: 100%;
}

.media-no-result .el-icon {
  font-size: 48px;
}

.media-info {
  padding: 10px;
  background: #f8f9fa;
  border-radius: 8px;
  font-size: 14px;
}

.media-info p {
  margin: 5px 0;
  color: #2c3e50;
}

/* 检测详情表格 */
.detection-section {
  margin-bottom: 30px;
}

.detection-card {
  border-radius: 16px;
  background: white;
}

.detection-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 16px 20px;
}

.table-container {
  padding: 20px;
}

.table-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e9ecef;
}

/* 表格单元格样式 */
.confidence-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.confidence-text {
  min-width: 50px;
  text-align: right;
  font-size: 14px;
  color: #2c3e50;
}

.bbox-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.bbox-coord {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.coord-label {
  color: #6c757d;
  min-width: 35px;
}

.coord-value {
  color: #2c3e50;
  font-family: monospace;
}

.bbox-size {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.size-label {
  color: #6c757d;
  min-width: 35px;
}

.size-value {
  color: #2c3e50;
  font-family: monospace;
}

/* 统计信息 */
.stats-section {
  margin-bottom: 30px;
}

.stats-card {
  border-radius: 16px;
  background: white;
}

.stats-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 16px 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 10px;
  font-size: 24px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #6c757d;
  margin-top: 4px;
}

/* 图表区域 */
.chart-container {
  margin-top: 30px;
  padding: 0 20px 20px;
}

.chart-container h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 18px;
  font-weight: 600;
}

.chart-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.chart-item {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.3s ease;
}

.chart-item:hover {
  background: #e9ecef;
}

.chart-item h4 {
  margin: 0 0 15px 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
}

.chart-wrapper {
  height: 300px;
  position: relative;
}

/* 无检测结果 */
.no-detections {
  margin-bottom: 30px;
}

.empty-card {
  border-radius: 16px;
  background: white;
}

.empty-content {
  padding: 60px 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: #6c757d;
}

.empty-content .el-icon {
  margin-bottom: 20px;
}

.empty-content h3 {
  margin: 0 0 10px 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.empty-content p {
  margin: 0;
  font-size: 16px;
}

/* 高亮弹窗 */
.highlight-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

.highlight-image {
  width: 100%;
  height: 400px;
  overflow: auto;
  border-radius: 12px;
  background: #f8f9fa;
  display: flex;
  align-items: center;
  justify-content: center;
}

.highlight-canvas {
  max-width: 100%;
  max-height: 100%;
  display: block;
}

.highlight-info {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.highlight-info h4 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.highlight-details p {
  margin: 10px 0;
  color: #2c3e50;
  font-size: 14px;
  line-height: 1.5;
}

.highlight-details strong {
  color: #1e3c72;
  font-weight: 600;
  min-width: 60px;
  display: inline-block;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .media-comparison {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .info-section {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .highlight-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .top-nav {
    flex-direction: column;
    gap: 20px;
    padding: 20px;
    text-align: center;
  }

  .nav-actions {
    flex-wrap: wrap;
    justify-content: center;
  }

  .detail-content {
    padding: 16px;
  }

  .media-comparison {
    padding: 10px;
  }

  .media-container {
    height: 250px;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .table-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
