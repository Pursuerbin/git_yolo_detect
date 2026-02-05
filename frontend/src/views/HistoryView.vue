<!-- src/views/HistoryView.vue -->
<template>
  <div class="history-container">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-brand">
        <h1>📋 检测历史记录</h1>
        <p class="subtitle">查看和管理所有检测记录</p>
      </div>
      <div class="nav-menu">
        <el-button @click="goToHome" type="info" size="large" class="nav-btn">
          <el-icon><Picture /></el-icon>
          图片检测
        </el-button>
        <el-button @click="goToVideo" type="info" size="large" class="nav-btn">
          <el-icon><VideoCamera /></el-icon>
          视频检测
        </el-button>
        <el-button @click="goToAbout" type="info" size="large" class="nav-btn">
          <el-icon><InfoFilled /></el-icon>
          关于系统
        </el-button>
        <el-tooltip content="刷新数据" placement="bottom">
          <el-button @click="refreshData" type="primary" circle size="large">
            <el-icon><Refresh /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧筛选面板 -->
      <div class="filter-panel">
        <!-- 搜索筛选 -->
        <el-card class="filter-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Search /></el-icon>
              <span>搜索筛选</span>
            </div>
          </template>
          <div class="search-filter">
            <el-input
              v-model="searchQuery"
              placeholder="搜索图片/视频名称..."
              clearable
              size="large"
              @input="handleSearch"
              class="search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
        </el-card>

        <!-- 检测类型筛选 -->
        <el-card class="filter-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Filter /></el-icon>
              <span>检测类型</span>
            </div>
          </template>
          <div class="type-filter">
            <el-checkbox-group v-model="selectedTypes" @change="filterRecords">
              <el-checkbox label="image" size="large">
                <div class="type-option">
                  <el-icon><Picture /></el-icon>
                  <span>图片检测</span>
                </div>
              </el-checkbox>
              <el-checkbox label="video" size="large">
                <div class="type-option">
                  <el-icon><VideoCamera /></el-icon>
                  <span>视频检测</span>
                </div>
              </el-checkbox>
              <el-checkbox label="camera" size="large">
                <div class="type-option">
                  <el-icon><Camera /></el-icon>
                  <span>摄像头检测</span>
                </div>
              </el-checkbox>
            </el-checkbox-group>
          </div>
        </el-card>

        <!-- 时间筛选 -->
        <el-card class="filter-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Calendar /></el-icon>
              <span>时间范围</span>
            </div>
          </template>
          <div class="date-filter">
            <div class="date-picker">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                size="large"
                @change="filterByDate"
                class="date-range-picker"
              />
            </div>
            <div class="quick-dates">
              <el-button
                v-for="btn in quickDateButtons"
                :key="btn.label"
                :type="btn.active ? 'primary' : 'default'"
                size="small"
                @click="selectQuickDate(btn)"
                class="quick-date-btn"
              >
                {{ btn.label }}
              </el-button>
            </div>
          </div>
        </el-card>

        <!-- 统计信息 -->
        <el-card class="filter-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><DataAnalysis /></el-icon>
              <span>统计概览</span>
            </div>
          </template>
          <div class="stats-summary">
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Document /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ totalRecords }}</div>
                <div class="stat-label">总记录数</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Picture /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ imageCount }}</div>
                <div class="stat-label">图片检测</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><VideoCamera /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ videoCount }}</div>
                <div class="stat-label">视频检测</div>
              </div>
            </div>
            <div class="stat-item">
              <div class="stat-icon">
                <el-icon><Camera /></el-icon>
              </div>
              <div class="stat-content">
                <div class="stat-value">{{ cameraCount }}</div>
                <div class="stat-label">摄像头检测</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 中间记录列表区域 -->
      <div class="records-area">
        <!-- 操作工具栏 -->
        <el-card class="toolbar-card" shadow="never">
          <div class="toolbar">
            <div class="toolbar-left">
              <h3>检测记录列表</h3>
              <el-tag type="info" size="large">
                共 {{ filteredRecords.length }} 条记录
              </el-tag>
            </div>
            <!-- 在 toolbar-right 部分修改 -->
            <div class="toolbar-right">
              <!-- 添加选中记录计数 -->
              <div v-if="selectedRecords.length > 0" class="selection-count">
                已选中 {{ selectedRecords.length }} 条记录
              </div>

              <el-button-group>
                <el-button @click="toggleViewMode('list')" :type="viewMode === 'list' ? 'primary' : 'default'">
                  <el-icon><Menu /></el-icon>
                  列表视图
                </el-button>
                <el-button @click="toggleViewMode('grid')" :type="viewMode === 'grid' ? 'primary' : 'default'">
                  <el-icon><Grid /></el-icon>
                  网格视图
                </el-button>
              </el-button-group>

              <el-dropdown @command="handleBatchCommand" class="batch-dropdown">
                <el-button type="primary" size="large">
                  批量操作
                  <el-icon><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="export" :disabled="selectedRecords.length === 0">
                      <el-icon><Download /></el-icon>
                      导出选中记录 ({{ selectedRecords.length }})
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided :disabled="selectedRecords.length === 0">
                      <el-icon><Delete /></el-icon>
                      删除选中记录 ({{ selectedRecords.length }})
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </el-card>

        <!-- 列表视图 -->
        <div v-if="viewMode === 'list'" class="list-view">
          <el-card class="records-card" shadow="never">
            <el-table
              :data="paginatedRecords"
              style="width: 100%"
              stripe
              @selection-change="handleSelectionChange"
              class="history-table"
              :default-sort="{ prop: 'detect_time', order: 'descending' }"
            >
              <el-table-column type="selection" width="55" align="center" />

              <el-table-column label="预览" width="100" align="center">
                <!-- 在 HistoryView.vue 的模板中 -->
                <template #default="{ row }">
                  <div class="record-preview" @click="previewRecord(row)">
                    <div v-if="row.detection_type === 'image'" class="image-preview">
                      <img
                        :src="getPreviewImageUrl(row)"
                        alt="预览"
                        class="preview-img"
                        @error="handleImageError"
                      />
                      <div class="preview-overlay">
                        <el-icon><ZoomIn /></el-icon>
                      </div>
                    </div>
                    <div v-else class="video-preview">
                      <div class="video-icon">
                        <el-icon><VideoPlay /></el-icon>
                      </div>
                      <div class="preview-overlay">
                        <el-icon><Play /></el-icon>
                      </div>
                    </div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column prop="filename" label="文件名称" min-width="180">
                <template #default="{ row }">
                  <div class="file-info">
                    <div class="file-name">
                      <el-tooltip :content="row.filename" placement="top">
                        <span class="filename-text">{{ shortenFilename(row.filename) }}</span>
                      </el-tooltip>
                    </div>
                    <div class="file-type">
                      <el-tag :type="getTypeTagType(row.detection_type)" size="small" effect="dark">
                        {{ getTypeLabel(row.detection_type) }}
                      </el-tag>
                    </div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column prop="detect_time" label="检测时间" width="180" sortable>
                <template #default="{ row }">
                  <div class="time-cell">
                    <div class="date">{{ formatDate(row.detect_time) }}</div>
                    <div class="time">{{ formatTime(row.detect_time) }}</div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="检测结果" width="120">
                <template #default="{ row }">
                  <div class="result-cell">
                    <div class="defect-count">
                      <el-icon><Collection /></el-icon>
                      <span>{{ row.total_objects || 0 }}</span>
                    </div>
                    <div class="confidence" v-if="row.confidence_avg">
                      <el-progress
                        :percentage="Math.round(row.confidence_avg * 100)"
                        :color="getConfidenceColor(row.confidence_avg)"
                        :show-text="false"
                        class="confidence-bar"
                      />
                      <span class="confidence-text">{{ (row.confidence_avg * 100).toFixed(1) }}%</span>
                    </div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column prop="model_used" label="使用模型" width="140">
                <template #default="{ row }">
                  <div class="model-cell">
                    <el-tag size="small" effect="plain">
                      {{ row.model_used || 'best.pt' }}
                    </el-tag>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="检测参数" width="180">
                <template #default="{ row }">
                  <div class="params-cell">
                    <div class="param-item">
                      <span class="param-label">置信度:</span>
                      <span class="param-value">{{ (row.confidence_threshold || 0.25).toFixed(2) }}</span>
                    </div>
                    <div class="param-item">
                      <span class="param-label">IoU:</span>
                      <span class="param-value">{{ (row.iou_threshold || 0.45).toFixed(2) }}</span>
                    </div>
                  </div>
                </template>
              </el-table-column>

              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <div class="action-buttons">
                    <el-button
                      @click="viewRecordDetail(row)"
                      type="primary"
                      size="small"
                      class="action-btn"
                    >
                      <el-icon><View /></el-icon>
                      查看详情
                    </el-button>
                    <el-dropdown @command="handleActionCommand(row, $event)" trigger="click" class="more-dropdown">
                      <el-button size="small" circle>
                        <el-icon><More /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-menu>
                          <el-dropdown-item command="download">
                            <el-icon><Download /></el-icon>
                            下载结果
                          </el-dropdown-item>
                          <el-dropdown-item command="export">
                            <el-icon><Document /></el-icon>
                            导出报告
                          </el-dropdown-item>
                          <el-dropdown-item command="share" divided>
                            <el-icon><Share /></el-icon>
                            分享链接
                          </el-dropdown-item>
                          <el-dropdown-item command="delete" class="delete-item">
                            <el-icon><Delete /></el-icon>
                            删除记录
                          </el-dropdown-item>
                        </el-dropdown-menu>
                      </template>
                    </el-dropdown>
                  </div>
                </template>
              </el-table-column>
            </el-table>

            <!-- 分页 -->
            <div class="pagination-container">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :total="filteredRecords.length"
                :page-sizes="[15, 20, 30, 50]"
                layout="total, sizes, prev, pager, next, jumper"
                @size-change="handleSizeChange"
                @current-change="handleCurrentChange"
                class="pagination"
              />
            </div>
          </el-card>
        </div>

        <!-- 网格视图 -->
        <div v-else class="grid-view">
          <div class="records-grid">
            <div
              v-for="record in paginatedRecords"
              :key="record.id"
              class="record-card"
              @click="viewRecordDetail(record)"
            >
              <div class="card-header">
                <div class="record-type">
                  <el-tag :type="getTypeTagType(record.detection_type)" size="small" effect="dark">
                    {{ getTypeLabel(record.detection_type) }}
                  </el-tag>
                </div>
                <div class="record-time">
                  <el-icon><Clock /></el-icon>
                  {{ formatTime(record.detect_time) }}
                </div>
              </div>

              <div class="card-preview">
                <div v-if="record.detection_type === 'image'" class="image-card-preview">
                  <img
                    :src="getPreviewImageUrl(record)"
                    alt="预览"
                    class="card-preview-img"
                    @error="handleImageError"
                  />
                </div>
                <div v-else class="video-card-preview">
                  <div class="video-card-icon">
                    <el-icon size="40"><VideoPlay /></el-icon>
                  </div>
                  <div class="video-label">
                    <span>视频检测</span>
                  </div>
                </div>
              </div>

              <div class="card-content">
                <div class="card-title">
                  <el-tooltip :content="record.filename" placement="top">
                    <h4>{{ shortenFilename(record.filename, 25) }}</h4>
                  </el-tooltip>
                </div>

                <div class="card-stats">
                  <div class="stat-item">
                    <el-icon><Collection /></el-icon>
                    <span class="stat-value">{{ record.total_objects || 0 }}</span>
                    <span class="stat-label">检测数</span>
                  </div>
                  <div class="stat-item">
                    <el-icon><TrendCharts /></el-icon>
                    <span class="stat-value">{{ (record.confidence_avg * 100 || 0).toFixed(1) }}%</span>
                    <span class="stat-label">置信度</span>
                  </div>
                  <div class="stat-item">
                    <el-icon><Cpu /></el-icon>
                    <span class="stat-value">{{ record.model_used?.split('.')[0] || 'best' }}</span>
                    <span class="stat-label">模型</span>
                  </div>
                </div>

                <div class="card-params">
                  <div class="param-tag">
                    <span>置信度参数: {{ (record.confidence_threshold || 0.25).toFixed(2) }}</span>
                  </div>
                  <div class="param-tag">
                    <span>IoU参数: {{ (record.iou_threshold || 0.45).toFixed(2) }}</span>
                  </div>
                </div>
              </div>

              <div class="card-footer">
                <div class="card-actions">
                  <el-button
                    @click.stop="viewRecordDetail(record)"
                    type="primary"
                    size="small"
                    class="card-btn"
                  >
                    <el-icon><View /></el-icon>
                    查看详情
                  </el-button>
                  <el-button
                    @click.stop="downloadResult(record)"
                    type="success"
                    size="small"
                    class="card-btn"
                  >
                    <el-icon><Download /></el-icon>
                    下载
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 网格视图分页 -->
          <div class="pagination-container">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :total="filteredRecords.length"
              :page-sizes="[16, 24, 32, 48]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleSizeChange"
              @current-change="handleCurrentChange"
              class="pagination"
            />
          </div>
        </div>

        <!-- 空状态 -->
        <div v-if="filteredRecords.length === 0 && !loading" class="empty-state">
          <el-card class="empty-card" shadow="never">
            <div class="empty-content">
              <div class="empty-icon">
                <el-icon size="80"><DataBoard /></el-icon>
              </div>
              <div class="empty-text">
                <h3>暂无检测记录</h3>
                <p>开始使用检测功能后，您的记录将在这里显示</p>
              </div>
              <div class="empty-actions">
                <el-button @click="goToHome" type="primary" size="large">
                  <el-icon><Picture /></el-icon>
                  开始图片检测
                </el-button>
                <el-button @click="goToVideo" type="success" size="large">
                  <el-icon><VideoCamera /></el-icon>
                  开始视频检测
                </el-button>
              </div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 右侧信息面板 -->
      <div class="info-panel">
        <!-- 系统信息 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Monitor /></el-icon>
              <span>系统信息</span>
            </div>
          </template>
          <div class="system-info">
            <div class="info-item">
              <div class="info-label">
                <el-icon><DataLine /></el-icon>
                <span>总检测次数</span>
              </div>
              <div class="info-value">{{ totalRecords }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">
                <el-icon><Clock /></el-icon>
                <span>最早记录</span>
              </div>
              <div class="info-value">{{ oldestRecordTime }}</div>
            </div>
            <div class="info-item">
              <div class="info-label">
                <el-icon><TrendCharts /></el-icon>
                <span>平均置信度</span>
              </div>
              <div class="info-value">{{ averageConfidence }}%</div>
            </div>
            <div class="info-item">
              <div class="info-label">
                <el-icon><Collection /></el-icon>
                <span>总检测数</span>
              </div>
              <div class="info-value">{{ totalDefects }}</div>
            </div>
          </div>
        </el-card>

        <!-- 最近活跃 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>最近检测</span>
            </div>
          </template>
          <div class="recent-activity">
            <div v-if="recentRecords.length === 0" class="empty-activity">
              <el-empty description="暂无最近记录" :image-size="80" />
            </div>
            <div v-else class="activity-list">
              <div v-for="(record, index) in recentRecords" :key="index" class="activity-item">
                <div class="activity-icon">
                  <el-icon v-if="record.detection_type === 'image'"><Picture /></el-icon>
                  <el-icon v-else-if="record.detection_type === 'video'"><VideoCamera /></el-icon>
                  <el-icon v-else><Camera /></el-icon>
                </div>
                <div class="activity-content">
                  <div class="activity-title">{{ record.filename }}</div>
                  <div class="activity-time">{{ formatRelativeTime(record.detect_time) }}</div>
                </div>
                <div class="activity-result">
                  <el-tag size="small" :type="record.total_objects > 0 ? 'danger' : 'success'">
                    {{ record.total_objects }} 检测
                  </el-tag>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 导出选项 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Download /></el-icon>
              <span>导出选项</span>
            </div>
          </template>
          <div class="export-options">
            <div class="export-option">
              <el-button @click="exportAllRecords" type="primary" size="large" class="export-btn">
                <el-icon><Document /></el-icon>
                导出全部记录
              </el-button>
              <div class="export-desc">导出当前所有筛选后的记录为Excel</div>
            </div>
            <div class="export-option">
              <el-button @click="exportStatistics" type="success" size="large" class="export-btn">
                <el-icon><TrendCharts /></el-icon>
                导出统计报告
              </el-button>
              <div class="export-desc">生成包含统计图表的PDF报告</div>
            </div>
            <div class="export-option">
              <el-button @click="clearAllRecords" type="danger" size="large" class="export-btn">
                <el-icon><Delete /></el-icon>
                清空所有记录
              </el-button>
              <div class="export-desc">谨慎操作，删除后将无法恢复</div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 记录详情弹窗 -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="`检测记录详情 - ${selectedRecord?.filename}`"
      width="90%"
      top="5vh"
      destroy-on-close
      class="detail-dialog"
    >
      <RecordDetailView
        v-if="selectedRecord"
        :record-id="selectedRecord.id"
        @close="detailDialogVisible = false"
      />
    </el-dialog>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="previewDialogVisible"
      title="预览"
      width="70%"
      top="10vh"
      destroy-on-close
      class="preview-dialog"
    >
      <div v-if="previewRecordData" class="preview-content">
        <div v-if="previewRecordData.detection_type === 'image'" class="image-preview-content">
          <div class="preview-image-container">
            <img :src="getFullImageUrl(previewRecordData)" alt="预览" class="preview-full-image" />
          </div>
          <div class="preview-info">
            <h4>{{ previewRecordData.filename }}</h4>
            <div class="preview-meta">
              <el-tag :type="getTypeTagType(previewRecordData.detection_type)" size="large">
                {{ getTypeLabel(previewRecordData.detection_type) }}
              </el-tag>
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                {{ formatDateTime(previewRecordData.detect_time) }}
              </span>
            </div>
          </div>
        </div>
        <div v-else class="video-preview-content">
          <div class="preview-video-container">
            <video
              :src="getFullVideoUrl(previewRecordData)"
              controls
              class="preview-full-video"
            ></video>
          </div>
          <div class="preview-info">
            <h4>{{ previewRecordData.filename }}</h4>
            <div class="preview-meta">
              <el-tag type="primary" size="large">
                {{ getTypeLabel(previewRecordData.detection_type) }}
              </el-tag>
              <span class="meta-item">
                <el-icon><Clock /></el-icon>
                {{ formatDateTime(previewRecordData.detect_time) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

// 添加 Element Plus 组件导入
import { ElNotification, ElMessageBox, ElLoading } from 'element-plus'
import RecordDetailView from './RecordDetailView.vue'

const icons = ElementPlusIconsVue
const router = useRouter()

// ==================== 响应式数据 ====================
const records = ref([])
const filteredRecords = ref([])
const selectedRecords = ref([])
const searchQuery = ref('')
const selectedTypes = ref(['image', 'video', 'camera'])
const dateRange = ref([])
const viewMode = ref('list')
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const detailDialogVisible = ref(false)
const previewDialogVisible = ref(false)
const selectedRecord = ref(null)
const previewRecordData = ref(null)

// 快速日期按钮
const quickDateButtons = ref([
  { label: '今天', value: 'today', active: false },
  { label: '昨天', value: 'yesterday', active: false },
  { label: '近7天', value: '7days', active: false },
  { label: '近30天', value: '30days', active: false },
  { label: '全部', value: 'all', active: true }
])

// ==================== 计算属性 ====================
// 总记录数
const totalRecords = computed(() => records.value.length)

// 分类统计
const imageCount = computed(() => records.value.filter(r => r.detection_type === 'image').length)
const videoCount = computed(() => records.value.filter(r => r.detection_type === 'video').length)
const cameraCount = computed(() => records.value.filter(r => r.detection_type === 'camera').length)

// 平均置信度
// 修改 averageConfidence 计算属性
const averageConfidence = computed(() => {
  if (records.value.length === 0) return '0.0';

  // 筛选出有有效置信度值的记录
  const validRecords = records.value.filter(record => {
    const avg = record.confidence_avg;
    return avg !== null && avg !== undefined && !isNaN(avg) && avg > 0;
  });

  if (validRecords.length === 0) return '0.0';

  const total = validRecords.reduce((sum, record) => {
    const avg = parseFloat(record.confidence_avg) || 0;
    return sum + avg;
  }, 0);

  const avgPercent = (total / validRecords.length * 100);

  // 确保不是 NaN
  if (isNaN(avgPercent)) {
    return '0.0';
  }

  return avgPercent.toFixed(1);
});

// 总缺陷数
const totalDefects = computed(() => {
  return records.value.reduce((sum, record) => sum + (record.total_objects || 0), 0)
})

// 最早记录时间
const oldestRecordTime = computed(() => {
  if (records.value.length === 0) return '--'
  const dates = records.value.map(r => new Date(r.detect_time))
  const oldest = new Date(Math.min(...dates))
  return formatDate(oldest)
})

// 最近记录（前5条）
const recentRecords = computed(() => {
  return [...records.value]
    .sort((a, b) => new Date(b.detect_time) - new Date(a.detect_time))
    .slice(0, 5)
})

// 分页记录
const paginatedRecords = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredRecords.value.slice(start, end)
})

// ==================== 生命周期钩子 ====================
onMounted(() => {
  loadRecords()
})

// ==================== 方法 ====================
const loadRecords = async () => {
  loading.value = true;
  try {
    const res = await axios.get('http://localhost:5000/api/history');
    console.log('API返回的历史记录数据:', res.data);

    // 检查第一条记录的detections字段
    if (res.data.length > 0) {
      console.log('第一条记录的detections字段类型:', typeof res.data[0].detections);
      console.log('第一条记录的detections字段内容:', res.data[0].detections);
    }

    records.value = await Promise.all(res.data.map(async (record) => {
      // 处理置信度平均值
      let confidence_avg = record.confidence_avg || 0;

      // 确保 confidence_avg 是数字
      if (confidence_avg !== null && confidence_avg !== undefined) {
        confidence_avg = parseFloat(confidence_avg);
        // 如果转换失败或不是数字，设为0
        if (isNaN(confidence_avg)) {
          confidence_avg = 0;
        }
      } else {
        confidence_avg = 0;
      }

      // 确保置信度值在合理范围内
      if (confidence_avg < 0) confidence_avg = 0;
      if (confidence_avg > 1) confidence_avg = 1;

      let detections = record.detections || [];

      // 如果 confidence_avg 为 0，尝试获取详情
      if (!confidence_avg && record.id) {
        try {
          const detailRes = await axios.get(`http://localhost:5000/api/records/${record.id}`);
          if (detailRes.data.record && detailRes.data.record.confidence_avg) {
            let detailAvg = parseFloat(detailRes.data.record.confidence_avg) || 0;
            if (!isNaN(detailAvg)) {
              confidence_avg = detailAvg;
            }
          }

          if (detailRes.data.detections) {
            detections = detailRes.data.detections;
          }
        } catch (err) {
          console.warn(`获取记录 ${record.id} 详情失败:`, err);
        }
      }

      return {
        id: record.id || 0,
        filename: record.filename || '',
        model_used: record.model_used || 'best.pt',
        confidence_threshold: parseFloat(record.confidence_threshold) || 0.25,
        iou_threshold: parseFloat(record.iou_threshold) || 0.45,
        detect_time: record.detect_time ? new Date(record.detect_time) : new Date(),
        detection_type: record.detection_type || 'image',
        total_objects: parseInt(record.total_objects) || 0,
        result_filename: record.result_filename || null,
        video_path: record.video_path || null,
        processed_video_path: record.processed_video_path || null,
        processed_video_filename: record.processed_video_path ?
          record.processed_video_path.split('/').pop() : null,
        // 确保 confidence_avg 有有效值
        confidence_avg: confidence_avg,
        // 存储检测详情
        detections: detections
      };
    }));

    console.log('处理后的记录数据:', records.value);
    filterRecords();
  } catch (err) {
    console.error('加载历史记录失败:', err);
    ElNotification({
      title: '加载失败',
      message: '无法加载历史记录，请检查网络连接',
      type: 'error',
      duration: 3000
    });
  } finally {
    loading.value = false;
  }
};

// 刷新数据
const refreshData = () => {
  loadRecords()
  ElNotification({
    title: '刷新成功',
    message: '数据已更新',
    type: 'success',
    duration: 2000
  })
}

// 筛选记录
const filterRecords = () => {
  let result = [...records.value]

  // 按类型筛选
  if (selectedTypes.value.length > 0) {
    result = result.filter(record => selectedTypes.value.includes(record.detection_type))
  }

  // 按搜索词筛选
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(record =>
      record.filename.toLowerCase().includes(query)
    )
  }

  // 按日期筛选
  if (dateRange.value && dateRange.value.length === 2) {
    const startDate = new Date(dateRange.value[0])
    const endDate = new Date(dateRange.value[1])
    endDate.setHours(23, 59, 59, 999)

    result = result.filter(record => {
      const recordDate = new Date(record.detect_time)
      return recordDate >= startDate && recordDate <= endDate
    })
  }

  filteredRecords.value = result
  currentPage.value = 1 // 重置到第一页
}

// 搜索处理
const handleSearch = () => {
  filterRecords()
}

// 按日期筛选
const filterByDate = () => {
  filterRecords()
  // 更新快速按钮状态
  quickDateButtons.value.forEach(btn => btn.active = false)
}

// 选择快速日期
const selectQuickDate = (btn) => {
  quickDateButtons.value.forEach(b => b.active = false)
  btn.active = true

  if (btn.value === 'all') {
    dateRange.value = []
  } else {
    const now = new Date()
    const start = new Date()

    switch (btn.value) {
      case 'today':
        start.setHours(0, 0, 0, 0)
        dateRange.value = [start, now]
        break
      case 'yesterday':
        start.setDate(now.getDate() - 1)
        start.setHours(0, 0, 0, 0)
        const yesterdayEnd = new Date(start)
        yesterdayEnd.setHours(23, 59, 59, 999)
        dateRange.value = [start, yesterdayEnd]
        break
      case '7days':
        start.setDate(now.getDate() - 7)
        dateRange.value = [start, now]
        break
      case '30days':
        start.setDate(now.getDate() - 30)
        dateRange.value = [start, now]
        break
    }
  }

  filterRecords()
}

// 切换视图模式
// 在 toggleViewMode 方法中调整
const toggleViewMode = (mode) => {
  viewMode.value = mode
  // 根据视图模式调整每页显示数量
  pageSize.value = mode === 'grid' ? 16 : 20  // 网格16个，列表20条
  currentPage.value = 1
}

// 处理批量操作
const handleBatchCommand = (command) => {
  if (selectedRecords.value.length === 0) {
    ElNotification({
      title: '提示',
      message: '请先选择记录',
      type: 'warning',
      duration: 2000
    })
    return
  }

  switch (command) {
    case 'export':
      exportSelectedRecords()
      break
    case 'delete':
      deleteSelectedRecords()
      break
  }
}

// 导出选中记录
const exportSelectedRecords = async () => {
  if (selectedRecords.value.length === 0) {
    ElNotification({
      title: '提示',
      message: '请先选择要导出的记录',
      type: 'warning',
      duration: 2000
    })
    return
  }

  try {
    // 等待用户确认
    await ElMessageBox.confirm(
      `确定要导出选中的 ${selectedRecords.value.length} 条记录吗？`,
      '导出确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info'
      }
    )

    // 动态导入xlsx库
    const xlsx = await import('xlsx')

    // 准备数据
    const data = [
      ['检测记录批量导出报告', '', '', '', '', '', '', '', ''],
      ['导出时间', new Date().toLocaleString(), '', '', '', '', '', '', ''],
      ['导出记录数', selectedRecords.value.length, '', '', '', '', '', '', ''],
      [],
      ['序号', '文件名称', '检测类型', '检测时间', '缺陷数量', '平均置信度', '使用模型', '置信度阈值', 'IoU阈值']
    ]

    // 添加选中记录数据
    selectedRecords.value.forEach((record, index) => {
      // 需要先确保记录有完整信息
      const fullRecord = records.value.find(r => r.id === record.id) || record

      data.push([
        index + 1,
        fullRecord.filename,
        getTypeLabel(fullRecord.detection_type),
        formatDateTime(fullRecord.detect_time),
        fullRecord.total_objects || 0,
        (fullRecord.confidence_avg * 100 || 0).toFixed(1) + '%',
        fullRecord.model_used || 'best.pt',
        (fullRecord.confidence_threshold || 0.25).toFixed(2),
        (fullRecord.iou_threshold || 0.45).toFixed(2)
      ])
    })

    // 创建Excel工作簿
    const worksheet = xlsx.utils.aoa_to_sheet(data)
    const workbook = xlsx.utils.book_new()
    xlsx.utils.book_append_sheet(workbook, worksheet, '检测记录')

    // 设置列宽
    const maxWidths = []
    data.forEach(row => {
      row.forEach((cell, colIndex) => {
        const cellLength = cell ? cell.toString().length : 0
        if (!maxWidths[colIndex] || cellLength > maxWidths[colIndex]) {
          maxWidths[colIndex] = cellLength
        }
      })
    })

    worksheet['!cols'] = maxWidths.map(width => ({ width: Math.min(width + 2, 50) }))

    // 生成文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `检测记录批量导出_${selectedRecords.value.length}条_${timestamp}.xlsx`

    // 导出文件
    xlsx.writeFile(workbook, filename)

    ElNotification({
      title: '导出成功',
      message: `已导出 ${selectedRecords.value.length} 条记录到 ${filename}`,
      type: 'success',
      duration: 3000
    })

  } catch (err) {
    // 用户取消操作
    if (err !== 'cancel') {
      console.error('批量导出失败:', err)
      ElNotification({
        title: '导出失败',
        message: err.message || '导出失败，请重试',
        type: 'error',
        duration: 3000
      })
    }
  }
}

// 删除选中记录
// 在批量删除函数中改用新的批量API
const deleteSelectedRecords = async () => {
  if (selectedRecords.value.length === 0) return

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedRecords.value.length} 条记录吗？此操作不可恢复。`,
      '批量删除确认',
      { /* ... 配置 ... */ }
    )

    const loadingInstance = ElLoading.service({
      lock: true,
      text: '批量删除中...',
      background: 'rgba(0, 0, 0, 0.7)'
    })

    try {
      const recordIds = selectedRecords.value.map(r => r.id)
      const response = await axios.post('http://localhost:5000/api/records/batch_delete', {
        record_ids: recordIds
      })

      loadingInstance.close()

      if (response.data.success) {
        ElNotification({
          title: '删除成功',
          message: `已删除 ${response.data.deleted_count} 条记录`,
          type: 'success',
          duration: 3000
        })

        // 重新加载数据
        await loadRecords()
        selectedRecords.value = []
      }
    } catch (err) {
      loadingInstance.close()
      throw err
    }
  } catch (err) {
    if (err !== 'cancel') {
      ElNotification({
        title: '删除失败',
        message: err.message || '批量删除失败',
        type: 'error',
        duration: 3000
      })
    }
  }
}

// 处理表格选择
const handleSelectionChange = (selection) => {
  // 这里需要特殊处理，因为表格只显示当前页的数据
  // 但我们需要存储所有选中的记录（包括不同页的）

  // 先清空当前页的选中状态
  const currentPageRecordIds = paginatedRecords.value.map(r => r.id);

  // 移除当前页的选中记录
  selectedRecords.value = selectedRecords.value.filter(
    r => !currentPageRecordIds.includes(r.id)
  );

  // 添加当前页新选中的记录
  selectedRecords.value.push(...selection);

  // 去重
  const uniqueMap = new Map();
  selectedRecords.value.forEach(record => {
    uniqueMap.set(record.id, record);
  });
  selectedRecords.value = Array.from(uniqueMap.values());
}

// 处理操作命令
const handleActionCommand = async (record, command) => {
  try {
    switch (command) {
      case 'download':
        await downloadResult(record)
        break
      case 'export':
        await exportSingleRecord(record)
        break
      case 'share':
        await shareRecord(record)
        break
      case 'delete':
        await deleteSingleRecord(record)
        break
      default:
        console.warn('未知命令:', command)
    }
  } catch (err) {
    console.error('执行操作失败:', err)
  }
}

// 查看记录详情
const viewRecordDetail = (record) => {
  console.log('查看记录详情，record对象:', record);
  console.log('记录ID:', record.id, '文件名:', record.filename);

  if (!record || !record.id) {
    ElNotification({
      title: '错误',
      message: '记录ID不存在，无法查看详情',
      type: 'error',
      duration: 3000
    });
    return;
  }

  // 创建一个精简的记录对象传递给详情组件
  selectedRecord.value = {
    id: record.id,
    filename: record.filename || '',
    detection_type: record.detection_type || 'image',
    model_used: record.model_used || 'best.pt'
  };

  detailDialogVisible.value = true;
  console.log('已打开详情对话框，记录ID:', record.id);
};

// 预览记录
const previewRecord = (record) => {
  previewRecordData.value = record
  previewDialogVisible.value = true
}

// 下载结果 - 修改为只下载处理后的结果
const downloadResult = async (record) => {
  try {
    let downloadUrl = ''
    let filename = ''

    // 根据检测类型获取对应的结果文件
    if (record.detection_type === 'image') {
      // 图片检测：下载标注后的结果图
      if (record.result_filename) {
        downloadUrl = `http://localhost:5000/static/results/${record.result_filename}`
        filename = record.result_filename
      } else {
        // 如果数据库中没有存储 result_filename，尝试获取详情
        try {
          const res = await axios.get(`http://localhost:5000/api/records/${record.id}`)
          if (res.data.record.result_filename) {
            downloadUrl = `http://localhost:5000/static/results/${res.data.record.result_filename}`
            filename = res.data.record.result_filename
          } else {
            throw new Error('未找到结果文件')
          }
        } catch (err) {
          throw new Error('无法获取结果文件信息')
        }
      }
    } else if (record.detection_type === 'video') {
      // 视频检测：下载处理后的视频
      if (record.processed_video_filename) {
        downloadUrl = `http://localhost:5000/static/results/${record.processed_video_filename}`
        filename = record.processed_video_filename
      } else {
        // 如果数据库中没有存储 processed_video_filename，尝试获取详情
        try {
          const res = await axios.get(`http://localhost:5000/api/records/${record.id}`)
          if (res.data.record.processed_video_path) {
            downloadUrl = `http://localhost:5000/static/results/${res.data.record.processed_video_path}`
            filename = res.data.record.processed_video_path.split('/').pop() || 'processed_video.mp4'
          } else {
            throw new Error('未找到处理后的视频文件')
          }
        } catch (err) {
          throw new Error('无法获取视频结果文件信息')
        }
      }
    } else {
      // 摄像头检测：提示无法下载
      ElNotification({
        title: '提示',
        message: '摄像头检测记录无法下载',
        type: 'info',
        duration: 2000
      })
      return
    }

    // 使用fetch下载文件
    const response = await fetch(downloadUrl)

    if (!response.ok) {
      throw new Error(`下载失败: ${response.status} ${response.statusText}`)
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    ElNotification({
      title: '下载成功',
      message: '文件下载完成',
      type: 'success',
      duration: 2000
    })

  } catch (err) {
    console.error('下载失败:', err)
    ElNotification({
      title: '下载失败',
      message: err.message || '文件下载失败，请重试',
      type: 'error',
      duration: 3000
    })
  }
}

// 导出单条记录
const exportSingleRecord = async (record) => {
  try {
    // 安全处理置信度
    const confidenceAvg = parseFloat(record.confidence_avg) || 0;
    const confidencePercent = (confidenceAvg * 100).toFixed(1);

    // 先检查是否有详细的检测数据
    let detections = [];

    // 尝试多种方式获取detections数据
    if (record.detections && Array.isArray(record.detections)) {
      // 如果detections已经是数组
      detections = record.detections;
    } else if (record.detections && typeof record.detections === 'string') {
      // 如果detections是字符串（可能是JSON字符串）
      try {
        detections = JSON.parse(record.detections);
        if (!Array.isArray(detections)) {
          detections = [];
        }
      } catch (e) {
        console.error('解析detections失败:', e);
        detections = [];
      }
    }

    // 如果没有检测数据，尝试从API获取
    if (detections.length === 0 && record.id) {
      try {
        const res = await axios.get(`http://localhost:5000/api/records/${record.id}`);
        if (res.data && res.data.detections) {
          if (Array.isArray(res.data.detections)) {
            detections = res.data.detections;
          } else if (typeof res.data.detections === 'string') {
            try {
              detections = JSON.parse(res.data.detections);
              if (!Array.isArray(detections)) {
                detections = [];
              }
            } catch (e) {
              console.error('解析API返回的detections失败:', e);
            }
          }
        }
      } catch (err) {
        console.error('获取详细检测数据失败:', err);
      }
    }

    // 准备导出数据
    const data = [
      ['检测记录报告', '', '', '', '', ''],
      ['导出时间', new Date().toLocaleString(), '', '', '', ''],
      ['文件名称', record.filename],
      ['检测类型', getTypeLabel(record.detection_type)],
      ['检测时间', formatDateTime(record.detect_time)],
      ['检测数量', record.total_objects || 0],
      ['平均置信度', confidencePercent + '%'],
      ['使用模型', record.model_used || 'best.pt'],
      ['置信度阈值', (parseFloat(record.confidence_threshold) || 0.25).toFixed(2)],
      ['IoU阈值', (parseFloat(record.iou_threshold) || 0.45).toFixed(2)],
      ['', ''],
      ['序号', '类别', '置信度', '位置X1', '位置Y1', '位置X2', '位置Y2']
    ];

    // 如果有检测详情，添加到表格中
    if (detections.length > 0) {
      detections.forEach((det, index) => {
        // 确保检测数据格式正确
        const detection = det.detection || det; // 兼容不同的数据结构

        data.push([
          index + 1,
          detection.class || detection.class_name || '未知',
          ((parseFloat(detection.confidence) || 0) * 100).toFixed(1) + '%',
          detection.x1 || detection.x || '-',
          detection.y1 || detection.y || '-',
          detection.x2 || detection.x + detection.width || '-',
          detection.y2 || detection.y + detection.height || '-'
        ]);
      });
    } else {
      // 如果没有检测数据，显示提示
      data.push(['', '暂无详细检测数据', '', '', '', '', '']);
    }

    // 动态导入xlsx库
    const xlsx = await import('xlsx');

    // 创建Excel工作簿
    const worksheet = xlsx.utils.aoa_to_sheet(data);
    const workbook = xlsx.utils.book_new();
    xlsx.utils.book_append_sheet(workbook, worksheet, '检测记录详情');

    // 生成文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const filename = `检测记录_${record.filename.split('.')[0]}_${timestamp}.xlsx`;

    // 导出文件
    xlsx.writeFile(workbook, filename);

    ElNotification({
      title: '导出成功',
      message: `记录已导出为 ${filename}`,
      type: 'success',
      duration: 2000
    });

  } catch (err) {
    console.error('导出记录失败:', err);
    ElNotification({
      title: '导出失败',
      message: '导出记录失败，请重试',
      type: 'error',
      duration: 3000
    });
  }
};

// 分享记录
const shareRecord = async (record) => {
  try {
    // 构建指向记录详情页面的链接
    const detailUrl = `${window.location.origin}/record/${record.id}`

    const shareData = {
      title: `绝缘子缺陷检测记录 - ${record.filename}`,
      text: `检测时间: ${formatDateTime(record.detect_time)}\n检测数量: ${record.total_objects}\n平均置信度: ${(record.confidence_avg * 100).toFixed(1)}%`,
      url: detailUrl
    }

    if (navigator.share) {
      try {
        await navigator.share(shareData)
        ElNotification({
          title: '分享成功',
          message: '内容已分享',
          type: 'success',
          duration: 2000
        })
      } catch (err) {
        if (err.name !== 'AbortError') {
          // 用户取消分享不视为错误
          throw err
        }
      }
    } else {
      // 备用方案：复制到剪贴板
      await navigator.clipboard.writeText(shareData.url)
      ElNotification({
        title: '复制成功',
        message: '分享链接已复制到剪贴板',
        type: 'success',
        duration: 2000
      })
    }

  } catch (err) {
    console.error('分享失败:', err)
    ElNotification({
      title: '分享失败',
      message: '分享功能出错，请手动复制链接',
      type: 'error',
      duration: 3000
    })
  }
}

// 删除单条记录
const deleteSingleRecord = async (record) => {
  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要删除记录 "${record.filename}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    // 调用删除API
    const response = await axios.delete(`http://localhost:5000/api/records/${record.id}`)

    if (response.data.success) {
      ElNotification({
        title: '删除成功',
        message: '记录已删除',
        type: 'success',
        duration: 2000
      })

      // 重新加载记录
      loadRecords()
    } else {
      throw new Error(response.data.message || '删除失败')
    }

  } catch (err) {
    // 如果是用户取消操作，不显示错误
    if (err === 'cancel' || err === 'close') {
      return
    }

    console.error('删除失败:', err)
    ElNotification({
      title: '删除失败',
      message: err.message || '删除记录失败，请重试',
      type: 'error',
      duration: 3000
    })
  }
}



// 导出全部记录
const exportAllRecords = () => {
  if (filteredRecords.value.length === 0) {
    ElNotification({
      title: '导出失败',
      message: '没有可导出的记录',
      type: 'warning',
      duration: 2000
    })
    return
  }

  import('xlsx').then(xlsx => {
    // 准备数据
    const data = [
      ['检测记录导出报告', '', '', '', '', '', '', '', ''],  // 注意：这里需要9列，因为后面有9列数据
      ['导出时间', new Date().toLocaleString(), '', '', '', '', '', '', ''],
      ['总记录数', filteredRecords.value.length, '', '', '', '', '', '', ''],
      [],
      ['序号', '文件名称', '检测类型', '检测时间', '缺陷数量', '平均置信度', '使用模型', '置信度阈值', 'IoU阈值']
    ]

    filteredRecords.value.forEach((record, index) => {
      data.push([
        index + 1,
        record.filename,
        getTypeLabel(record.detection_type),
        formatDateTime(record.detect_time),
        record.total_objects || 0,
        (record.confidence_avg * 100 || 0).toFixed(1) + '%',
        record.model_used || 'best.pt',
        (record.confidence_threshold || 0.25).toFixed(2),
        (record.iou_threshold || 0.45).toFixed(2)
      ])
    })

    // 创建Excel工作簿
    const worksheet = xlsx.utils.aoa_to_sheet(data)
    const workbook = xlsx.utils.book_new()
    xlsx.utils.book_append_sheet(workbook, worksheet, '检测记录')

    // 生成文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `检测记录导出_${timestamp}.xlsx`

    // 导出文件
    xlsx.writeFile(workbook, filename)

    ElNotification({
      title: '导出成功',
      message: `记录已导出为 ${filename}`,
      type: 'success',
      duration: 3000
    })
  }).catch(err => {
    console.error('导出失败:', err)
    ElNotification({
      title: '导出失败',
      message: '导出失败，请确保已安装xlsx库',
      type: 'error',
      duration: 3000
    })
  })
}

// 导出统计报告
const exportStatistics = async () => {
  try {
    ElNotification({
      title: '生成报告',
      message: '正在生成统计报告，请稍候...',
      type: 'info',
      duration: 3000
    })

    // 收集统计数据
    const statsData = {
      totalRecords: totalRecords.value,
      imageCount: imageCount.value,
      videoCount: videoCount.value,
      cameraCount: cameraCount.value,
      totalDefects: totalDefects.value,
      averageConfidence: parseFloat(averageConfidence.value) || 0,
      oldestRecordTime: oldestRecordTime.value,
      exportTime: new Date().toLocaleString(),
      recentRecords: recentRecords.value.slice(0, 5)
    }

    // 动态导入jsPDF和html2canvas
    const { jsPDF } = await import('jspdf')
    const html2canvas = (await import('html2canvas')).default

    // 创建PDF文档
    const doc = new jsPDF('p', 'mm', 'a4')
    const pageWidth = doc.internal.pageSize.getWidth()
    const margin = 20
    let yPosition = 20

    // 添加标题
    doc.setFontSize(20)
    doc.setFont('helvetica', 'bold')
    doc.text('绝缘子缺陷检测系统 - 统计报告', pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 15

    // 添加导出时间
    doc.setFontSize(12)
    doc.setFont('helvetica', 'normal')
    doc.text(`导出时间: ${statsData.exportTime}`, pageWidth / 2, yPosition, { align: 'center' })
    yPosition += 20

    // 添加统计概览
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    doc.text('统计概览', margin, yPosition)
    yPosition += 10

    // 添加统计数据
    doc.setFontSize(12)
    doc.setFont('helvetica', 'normal')
    const stats = [
      { label: '总检测记录数', value: statsData.totalRecords },
      { label: '图片检测记录', value: statsData.imageCount },
      { label: '视频检测记录', value: statsData.videoCount },
      { label: '摄像头检测记录', value: statsData.cameraCount },
      { label: '总检测缺陷数', value: statsData.totalDefects },
      { label: '平均置信度', value: `${statsData.averageConfidence}%` },
      { label: '最早记录时间', value: statsData.oldestRecordTime }
    ]

    stats.forEach(stat => {
      doc.text(`${stat.label}: ${stat.value}`, margin, yPosition)
      yPosition += 8
    })

    yPosition += 15

    // 添加最近检测记录
    doc.setFontSize(16)
    doc.setFont('helvetica', 'bold')
    doc.text('最近检测记录', margin, yPosition)
    yPosition += 10

    doc.setFontSize(10)
    statsData.recentRecords.forEach((record, index) => {
      const recordInfo = `${index + 1}. ${shortenFilename(record.filename, 30)} - ${formatDateTime(record.detect_time)} - ${record.total_objects || 0} 检测`
      doc.text(recordInfo, margin, yPosition)
      yPosition += 6
      if (yPosition > 270) {
        doc.addPage()
        yPosition = 20
      }
    })

    // 生成文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `绝缘子缺陷检测系统_统计报告_${timestamp}.pdf`

    // 保存PDF
    doc.save(filename)

    ElNotification({
      title: '导出成功',
      message: `统计报告已导出为 ${filename}`,
      type: 'success',
      duration: 3000
    })
  } catch (err) {
    console.error('导出统计报告失败:', err)
    ElNotification({
      title: '导出失败',
      message: '生成统计报告失败，请重试',
      type: 'error',
      duration: 3000
    })
  }
}

// 清空所有记录
const clearAllRecords = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有检测记录吗？此操作不可恢复，且会删除所有数据。',
      '清空确认',
      {
        confirmButtonText: '确定清空',
        cancelButtonText: '取消',
        type: 'error',
        confirmButtonClass: 'el-button--danger'
      }
    )

    // 显示加载状态
    const loadingInstance = ElLoading.service({
      lock: true,
      text: '正在清空记录...',
      background: 'rgba(0, 0, 0, 0.7)'
    })

    try {
      // 发送请求到后端API清空所有记录
      const response = await axios.post('http://localhost:5000/api/records/clear_all')

      loadingInstance.close()

      if (response.data.success) {
        ElNotification({
          title: '清空成功',
          message: `已清空 ${response.data.deleted_count} 条记录`,
          type: 'success',
          duration: 3000
        })

        // 重新加载数据
        await loadRecords()
      } else {
        throw new Error(response.data.message || '清空失败')
      }
    } catch (err) {
      loadingInstance.close()
      throw err
    }
  } catch (err) {
    // 如果是用户取消操作，不显示错误
    if (err === 'cancel' || err === 'close') {
      return
    }

    console.error('清空记录失败:', err)
    ElNotification({
      title: '清空失败',
      message: err.message || '清空记录失败，请重试',
      type: 'error',
      duration: 3000
    })
  }
}

// 分页处理
const handleSizeChange = (newSize) => {
  pageSize.value = newSize
  currentPage.value = 1
}

const handleCurrentChange = (newPage) => {
  currentPage.value = newPage
}

// ==================== 工具函数 ====================
// 格式化日期
const formatDate = (date) => {
  if (!date) return '--'
  const d = new Date(date)
  return d.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 格式化时间
const formatTime = (date) => {
  if (!date) return '--'
  const d = new Date(date)
  return d.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// 格式化日期时间
const formatDateTime = (date) => {
  if (!date) return '--'
  const d = new Date(date)
  return d.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化相对时间
const formatRelativeTime = (date) => {
  if (!date) return '--'
  const now = new Date()
  const recordDate = new Date(date)
  const diffInSeconds = Math.floor((now - recordDate) / 1000)

  if (diffInSeconds < 60) return '刚刚'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}分钟前`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}小时前`
  if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)}天前`

  return formatDate(date)
}

// 缩短文件名
const shortenFilename = (filename, maxLength = 20) => {
  if (!filename || filename.length <= maxLength) return filename
  const parts = filename.split('.')
  const ext = parts.pop()
  const name = parts.join('.')
  return name.substring(0, maxLength - 3) + '...' + ext
}

// 获取类型标签
const getTypeLabel = (type) => {
  const types = {
    'image': '图片检测',
    'video': '视频检测',
    'camera': '摄像头检测'
  }
  return types[type] || '未知类型'
}

// 获取类型标签样式
const getTypeTagType = (type) => {
  const types = {
    'image': 'success',
    'video': 'primary',
    'camera': 'warning'
  }
  return types[type] || 'info'
}

// 获取置信度颜色
const getConfidenceColor = (confidence) => {
  if (!confidence) return '#909399'
  if (confidence >= 0.8) return '#67C23A'
  if (confidence >= 0.6) return '#E6A23C'
  if (confidence >= 0.4) return '#F56C6C'
  return '#909399'
}

// 获取预览图片URL
// 修改 getPreviewImageUrl 方法
const getPreviewImageUrl = (record) => {
  // 确保图片URL始终有效
  try {
    if (record.detection_type === 'image' && record.result_filename) {
      return `http://localhost:5000/static/results/${record.result_filename}?t=${Date.now()}`;
    }

    if (record.detection_type === 'image') {
      return `http://localhost:5000/static/uploads/${record.filename}?t=${Date.now()}`;
    }

    // 视频或摄像头检测的预览图
    return 'https://via.placeholder.com/80x60?text=暂无预览';
  } catch (error) {
    console.error('生成预览URL失败:', error);
    return 'https://via.placeholder.com/80x60?text=错误';
  }
};

// 修改 getFullImageUrl 方法
const getFullImageUrl = (record) => {
  if (record.detection_type === 'image' && record.result_filename) {
    return `http://localhost:5000/static/results/${record.result_filename}`
  }
  if (record.detection_type === 'image') {
    return `http://localhost:5000/static/uploads/${record.filename}`
  }
  return ''
}

// 修改 getFullVideoUrl 方法
const getFullVideoUrl = (record) => {
  if (record.detection_type === 'video' && record.processed_video_filename) {
    return `http://localhost:5000/static/results/${record.processed_video_filename}`
  }
  if (record.detection_type === 'video' && record.video_path) {
    return `http://localhost:5000/static/uploads/${record.video_path}`
  }
  return ''
}


// 改进的图片错误处理方法
const handleImageError = (event) => {
  console.log('图片加载失败:', event.target.src)
  // 尝试加载原始图片
  const src = event.target.src
  const filenameMatch = src.match(/\/static\/results\/(.+)\?/)

  if (filenameMatch && filenameMatch[1]) {
    const originalUrl = src.replace('/static/results/', '/static/uploads/')
    event.target.src = originalUrl
  } else {
    // 使用在线占位图
    event.target.src = 'https://via.placeholder.com/80x60?text=加载失败'
  }
}

// ==================== 导航功能 ====================
const goToHome = () => {
  router.push('/upload')
}

const goToVideo = () => {
  router.push('/video')
}

const goToAbout = () => {
  router.push('/about')
}

// 监听数据变化
watch([searchQuery, selectedTypes, dateRange], () => {
  filterRecords()
})
</script>

<style scoped>
.history-container {
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
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-btn:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

/* 主要内容区域 */
.main-content {
  display: grid;
  grid-template-columns: 300px 1fr 300px;
  gap: 24px;
  padding: 30px;
  max-width: 1920px;
  margin: 0 auto;
}

/* 筛选面板 */
.filter-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filter-card {
  border-radius: 16px;
  border: none;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

.filter-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 16px 20px;
  border-bottom: none;
}


.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 600;
}

/* 文字增强 */
.card-header span {
  font-weight: 700;
  letter-spacing: 0.5px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  color: black;
}
.card-header .el-icon {
  font-size: 20px;
  color: black !important;
}

/* 搜索框 */
.search-filter {
  padding: 10px 16px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 类型筛选 */
.type-filter {
  padding: 10px 16px;
}

.type-option {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 8px 0;
}

/* 日期筛选 */
.date-filter {
  padding: 10px 16px;
}

.date-range-picker {
  width: 100%;
}

.quick-dates {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.quick-date-btn {
  flex: 1;
  min-width: 60px;
}

/* 统计信息 */
.stats-summary {
  padding: 10px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.stat-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.stat-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-size: 20px;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
}

.stat-label {
  font-size: 12px;
  color: #6c757d;
}

/* 记录列表区域 */
.records-area {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 工具栏 */
.toolbar-card {
  border-radius: 16px;
  background: white;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.toolbar-left h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 批量操作下拉菜单样式 */
.batch-dropdown {
  margin-left: 10px;
}

/* 批量删除确认对话框样式 */
.batch-delete-dialog .el-message-box__btns {
  display: flex;
  justify-content: space-between;
}

/* 选中记录计数样式 */
.selection-count {
  margin-left: 10px;
  font-size: 14px;
  color: #409eff;
  font-weight: 500;
}

/* 操作按钮组样式 */
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* 选中记录操作区域 */
.selection-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #ecf5ff;
  border-radius: 6px;
  border: 1px solid #d9ecff;
  margin-bottom: 10px;
}

.selection-actions .el-button {
  margin: 0;
}

/* 增强表格选择列样式 */
.history-table :deep(.el-table__selection-column) .el-checkbox {
  margin-right: 0;
}

/* 批量操作按钮悬停效果 */
.toolbar-right .el-button-group .el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 列表视图 */
.list-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.records-card {
  border-radius: 16px;
  background: white;
  min-height: 600px;
}

/* 表格样式 */
.history-table {
  border-radius: 12px;
  overflow: hidden;
}

.history-table :deep(.el-table__header) th {
  background: #f8f9fa;
  color: #2c3e50;
  font-weight: 600;
  border-bottom: 2px solid #e9ecef;
}

.history-table :deep(.el-table__row) {
  transition: all 0.3s ease;
}

.history-table :deep(.el-table__row:hover) {
  background-color: #f8f9fa;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 预览单元格 */
.record-preview {
  width: 80px;
  height: 60px;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
}

.record-preview:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.image-preview, .video-preview {
  width: 100%;
  height: 100%;
  position: relative;
  background: #f8f9fa;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.video-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.record-preview:hover .preview-overlay {
  opacity: 1;
}

/* 文件信息单元格 */
.file-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filename-text {
  font-weight: 500;
  color: #2c3e50;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 时间单元格 */
.time-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.time-cell .date {
  font-weight: 500;
  color: #2c3e50;
}

.time-cell .time {
  font-size: 12px;
  color: #6c757d;
}

/* 结果单元格 */
.result-cell {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.defect-count {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #2c3e50;
  font-weight: 500;
}

.defect-count .el-icon {
  color: #667eea;
}

.confidence {
  display: flex;
  align-items: center;
  gap: 8px;
}

.confidence-bar {
  flex: 1;
}

.confidence-text {
  font-size: 12px;
  color: #6c757d;
  min-width: 40px;
  text-align: right;
}

/* 参数单元格 */
.params-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.param-label {
  font-size: 12px;
  color: #6c757d;
}

.param-value {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 500;
}

.more-dropdown {
  margin-left: auto;
}

.delete-item {
  color: #f56c6c;
}

/* 分页 */
.pagination-container {
  padding: 20px;
  display: flex;
  justify-content: center;
  border-top: 1px solid #e9ecef;
}

.pagination :deep(.el-pagination) {
  padding: 0;
}

/* 网格视图 */
.grid-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.records-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.record-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.record-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.record-time {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #6c757d;
}

.card-preview {
  height: 160px;
  position: relative;
  overflow: hidden;
  background: #f8f9fa;
}

.image-card-preview {
  width: 100%;
  height: 100%;
}

.card-preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.record-card:hover .card-preview-img {
  transform: scale(1.05);
}

.video-card-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.video-card-icon {
  margin-bottom: 12px;
}

.video-label {
  font-size: 14px;
  font-weight: 500;
}

.card-content {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-title h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.card-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-item .el-icon {
  color: #667eea;
  font-size: 16px;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.stat-label {
  font-size: 12px;
  color: #6c757d;
}

.card-params {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.param-tag {
  padding: 10px 20px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 13px;
  color: #6c757d;
}

.card-footer {
  padding: 12px 16px;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.card-btn {
  flex: 1;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
}

/* 空状态 */
.empty-state {
  margin-top: 40px;
}

.empty-card {
  border-radius: 16px;
  background: white;
}

.empty-content {
  padding: 60px 40px;
  text-align: center;
}

.empty-icon {
  margin-bottom: 24px;
  color: #6c757d;
}

.empty-text h3 {
  margin: 0 0 12px 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}

.empty-text p {
  margin: 0 0 24px 0;
  color: #6c757d;
  font-size: 16px;
}

.empty-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
}

/* 信息面板 */
.info-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.info-card {
  border-radius: 16px;
  background: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}

/* 系统信息 */
.system-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.info-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.info-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #2c3e50;
  font-weight: 500;
}

.info-label .el-icon {
  color: #667eea;
}

.info-value {
  font-size: 18px;
  font-weight: 700;
  color: #2c3e50;
}

/* 最近活跃 */
.recent-activity {
  min-height: 200px;
}

.empty-activity {
  padding: 40px 0;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
}

.activity-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
}

.activity-icon {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 8px;
  font-size: 18px;
}

.activity-content {
  flex: 1;
  min-width: 0; /* 关键：允许flex子元素收缩 */
  overflow: hidden; /* 确保内容不溢出 */
}

.activity-title {
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
  margin-bottom: 4px;
  overflow: hidden; /* 隐藏溢出内容 */
  text-overflow: ellipsis; /* 添加省略号 */
  white-space: nowrap; /* 不换行 */
  max-width: 100%; /* 确保不超过父容器 */
  display: block; /* 确保为块级元素 */
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
  overflow: hidden; /* 防止内容溢出浅色框 */
}


/* 导出选项 */
.export-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.export-option {
  text-align: center;
}

.export-btn {
  width: 100%;
  padding: 16px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  margin-bottom: 8px;
}

.export-desc {
  font-size: 12px;
  color: #6c757d;
  line-height: 1.4;
}

/* 弹窗样式 */
.detail-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
}

.detail-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  margin-right: 0;
}

.detail-dialog :deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
}

.preview-dialog :deep(.el-dialog) {
  border-radius: 20px;
  overflow: hidden;
}

.preview-content {
  max-height: 70vh;
  overflow-y: auto;
}

.preview-image-container, .preview-video-container {
  width: 100%;
  height: 400px;
  overflow: hidden;
  border-radius: 12px;
  margin-bottom: 20px;
}

.preview-full-image {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.preview-full-video {
  width: 100%;
  height: 100%;
  background: #000;
}

.preview-info {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.preview-info h4 {
  margin: 0 0 16px 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
}

.preview-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6c757d;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 1400px) {
  .main-content {
    grid-template-columns: 280px 1fr;
    gap: 20px;
    padding: 20px;
  }

  .info-panel {
    grid-column: span 2;
  }
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .filter-panel {
    grid-row: 2;
  }

  .records-area {
    grid-row: 1;
  }

  .info-panel {
    grid-row: 3;
    grid-column: 1;
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

  .toolbar {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }

  .toolbar-left, .toolbar-right {
    width: 100%;
  }

  .toolbar-right {
    justify-content: space-between;
  }

  .records-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }

  .action-buttons {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .action-btn {
    width: 100%;
  }

  .empty-actions {
    flex-direction: column;
  }
}
</style>
