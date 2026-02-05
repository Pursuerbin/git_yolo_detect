<!-- src/views/VideoDetect.vue -->
<template>
  <div class="video-detect-container">
    <!-- 顶部导航栏 -->
    <div class="top-nav">
      <div class="nav-brand">
        <h1>🎬 视频检测系统</h1>
        <p class="subtitle">基于YOLOv11的视频实时检测平台</p>
      </div>
      <div class="nav-menu">
        <el-button @click="goToHome" type="primary" size="large" class="nav-btn">
          <el-icon><Picture /></el-icon>
          图片检测
        </el-button>
        <el-button @click="goToHistory" type="info" size="large" class="nav-btn">
          <el-icon><Histogram /></el-icon>
          历史记录
        </el-button>
        <el-button @click="goToAbout" type="info" size="large" class="nav-btn">
          <el-icon><InfoFilled /></el-icon>
          关于系统
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content">
      <!-- 左侧配置面板 -->
      <div class="config-panel">
        <!-- 检测模式 -->
        <el-card class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><VideoCamera /></el-icon>
              <span>检测模式</span>
            </div>
          </template>
          <div class="mode-selector">
            <el-radio-group v-model="activeMode" class="mode-radio-group">
              <el-radio-button label="video" size="large">
                <el-icon><VideoPlay /></el-icon>
                视频文件
              </el-radio-button>
              <el-radio-button label="camera" size="large">
                <el-icon><Camera /></el-icon>
                实时摄像头
              </el-radio-button>
            </el-radio-group>
          </div>
        </el-card>

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

        <!-- 设备选择 -->
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
                                <el-icon class="warning-icon"><Warning /></el-icon>
                            </el-tooltip>
                        </el-radio>
                    </el-radio-group>

                    <!-- 强制CPU选项 -->
                    <div class="option-item" v-if="deviceInfo && deviceInfo.hasGpu">
                        <el-divider content-position="left">高级选项</el-divider>
                        <el-switch v-model="forceCpu" size="large" @change="onForceCpuChange">
                            <template #prefix>
                                <el-icon><Cpu /></el-icon>
                            </template>
                            <template #default>
                                强制CPU模式
                            </template>
                        </el-switch>
                        <p class="option-desc">当GPU内存不足时启用</p>
                    </div>
                </div>
            </div>
        </el-card>

        <!-- 参数配置 -->
        <el-card v-if="activeMode === 'video'" class="config-card" shadow="hover">
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

        <!-- 摄像头控制 -->
        <el-card v-if="activeMode === 'camera'" class="config-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Camera /></el-icon>
              <span>摄像头控制</span>
            </div>
          </template>

          <div class="camera-control">
            <div class="control-item">
              <div class="control-label">
                <el-icon><VideoCamera /></el-icon>
                <span>摄像头来源</span>
              </div>
              <el-radio-group v-model="cameraSource" size="large" class="camera-source-radio">
                <el-radio-button label="server">
                  <el-icon><Server /></el-icon>
                  服务器摄像头
                </el-radio-button>
                <el-radio-button label="local">
                  <el-icon><Monitor /></el-icon>
                  本地摄像头
                </el-radio-button>
              </el-radio-group>
            </div>

            <div class="control-item" v-if="cameraSource === 'server'">
              <div class="control-label">
                <el-icon><VideoCamera /></el-icon>
                <span>服务器摄像头选择</span>
              </div>
              <el-select
                v-model="selectedCamera"
                placeholder="选择摄像头"
                size="large"
                class="camera-select"
              >
                <el-option label="默认摄像头" value="0" />
                <el-option label="摄像头 1" value="1" />
                <el-option label="摄像头 2" value="2" />
              </el-select>
            </div>

            <div class="control-buttons">
              <el-button
                @click="startCamera"
                type="success"
                size="large"
                :disabled="cameraActive"
                class="control-btn"
              >
                <template #icon>
                  <el-icon><VideoPlay /></el-icon>
                </template>
                启动摄像头
              </el-button>

              <el-button
                @click="stopCamera"
                type="danger"
                size="large"
                :disabled="!cameraActive"
                class="control-btn"
              >
                <template #icon>
                  <el-icon><VideoPause /></el-icon>
                </template>
                停止摄像头
              </el-button>
            </div>
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

          <div v-if="activeMode === 'video'" class="quick-actions">
            <el-button
              @click="detectVideo"
              type="primary"
              size="large"
              :disabled="!selectedVideo || videoLoading"
              :loading="videoLoading"
              class="action-btn"
            >
              <template #icon>
                <el-icon><Search /></el-icon>
              </template>
              {{ videoLoading ? '处理中...' : '开始检测' }}
            </el-button>

            <el-button
              @click="clearVideo"
              type="warning"
              size="large"
              :disabled="!selectedVideo"
              class="action-btn"
            >
              <template #icon>
                <el-icon><Delete /></el-icon>
              </template>
              清除视频
            </el-button>
          </div>

          <div v-else class="quick-actions">
            <el-button
              @click="startCamera"
              type="success"
              size="large"
              :disabled="cameraActive"
              class="action-btn"
            >
              <template #icon>
                <el-icon><VideoPlay /></el-icon>
              </template>
              开始实时检测
            </el-button>

            <el-button
              @click="stopCamera"
              type="danger"
              size="large"
              :disabled="!cameraActive"
              class="action-btn"
            >
              <template #icon>
                <el-icon><VideoPause /></el-icon>
              </template>
              停止检测
            </el-button>
          </div>
        </el-card>
      </div>

      <!-- 中间上传/预览区域 -->
      <div class="preview-area">
        <!-- 视频上传卡片 -->
        <el-card v-if="activeMode === 'video'" class="upload-card" shadow="never">
          <template #header>
            <div class="upload-header">
              <el-icon><VideoCameraFilled /></el-icon>
              <span>视频上传</span>
              <el-tag type="info" size="small">支持 MP4, AVI, MOV, MKV 格式</el-tag>
            </div>
          </template>

          <div
            class="upload-zone"
            @dragover.prevent="onDragOver"
            @dragleave.prevent="onDragLeave"
            @drop.prevent="onDrop"
            :class="{ 'drag-over': isDragOver }"
            @click="triggerVideoInput"
          >
            <input
              type="file"
              id="video-input"
              accept=".mp4,.avi,.mov,.mkv"
              @change="onVideoSelected"
              hidden
            >

            <div class="upload-content" v-if="!selectedVideo">
              <div class="upload-icon">
                <el-icon size="80"><VideoCamera /></el-icon>
              </div>
              <div class="upload-text">
                <h3>点击或拖拽视频到此处</h3>
                <p>支持常见视频格式，最大100MB</p>
              </div>
              <el-button type="primary" size="large" class="select-btn">
                <el-icon><FolderOpened /></el-icon>
                选择视频文件
              </el-button>
            </div>

            <!-- 视频预览 -->
            <div class="video-preview" v-else>
              <div class="preview-header">
                <div class="file-info">
                  <el-icon><VideoCamera /></el-icon>
                  <div class="file-details">
                    <h4>{{ selectedVideo.name }}</h4>
                    <p>{{ formatFileSize(selectedVideo.size) }} • {{ getVideoType(selectedVideo.type) }}</p>
                  </div>
                </div>
                <div class="preview-actions">
                  <el-button @click.stop="playVideo" type="primary" circle>
                    <el-icon><VideoPlay /></el-icon>
                  </el-button>
                  <el-button @click.stop="clearVideo" type="danger" text circle>
                    <el-icon><Close /></el-icon>
                  </el-button>
                </div>
              </div>

              <div class="preview-container">
                <video
                  ref="videoPlayer"
                  :src="videoPreviewUrl"
                  controls
                  class="preview-video"
                  @loadedmetadata="onVideoLoaded"
                ></video>
                <div class="video-info-overlay">
                  <div class="video-info-item">
                    <el-icon><Clock /></el-icon>
                    <span v-if="videoDuration">{{ formatTime(videoDuration) }}</span>
                    <span v-else>加载中...</span>
                  </div>
                  <div class="video-info-item">
                    <el-icon><DataAnalysis /></el-icon>
                    <span>{{ formatFileSize(selectedVideo?.size || 0) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="videoError" class="error-alert">
            <el-alert
              :title="videoError"
              type="error"
              :closable="true"
              @close="videoError = ''"
              show-icon
            />
          </div>
        </el-card>

        <!-- 摄像头预览 -->
        <el-card v-else class="camera-card" shadow="never">
          <template #header>
            <div class="camera-header">
              <el-icon><CameraFilled /></el-icon>
              <span>实时摄像头</span>
              <el-tag :type="cameraActive ? 'success' : 'info'" size="small">
                {{ cameraActive ? '运行中' : '未启动' }}
              </el-tag>
            </div>
          </template>

          <div class="camera-preview">
            <div v-if="cameraActive" class="camera-stream">
              <!-- 服务器摄像头 -->
              <div v-if="cameraSource === 'server'" class="camera-frame">
                <img :src="cameraStreamUrl" alt="摄像头画面" class="camera-feed" />
                <div class="camera-overlay">
                  <div class="camera-status">
                    <el-icon><VideoCamera /></el-icon>
                    <span>实时检测中...</span>
                  </div>
                  <div class="camera-stats">
                    <div class="stat-item">
                      <el-icon><Timer /></el-icon>
                      <span>{{ formatRunTime }}</span>
                    </div>
                    <div class="stat-item">
                      <el-icon><DataLine /></el-icon>
                      <span>实时帧率: {{ estimatedFps }} FPS</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 本地摄像头 -->
              <div v-else class="camera-frame">
                <video
                  ref="localVideoRef"
                  autoplay
                  playsinline
                  muted
                  class="camera-feed"
                ></video>
                <canvas
                  ref="localCanvasRef"
                  class="camera-feed"
                  style="display: none"
                ></canvas>
                <div class="camera-overlay">
                  <div class="camera-status">
                    <el-icon><VideoCamera /></el-icon>
                    <span>实时检测中...</span>
                  </div>
                  <div class="camera-stats">
                    <div class="stat-item">
                      <el-icon><Timer /></el-icon>
                      <span>{{ formatRunTime }}</span>
                    </div>
                    <div class="stat-item">
                      <el-icon><DataLine /></el-icon>
                      <span>实时帧率: {{ estimatedFps }} FPS</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="camera-placeholder">
              <div class="placeholder-content">
                <div class="placeholder-icon">
                  <el-icon size="80"><Camera /></el-icon>
                </div>
                <div class="placeholder-text">
                  <h3>摄像头预览</h3>
                  <p>请点击左侧"启动摄像头"按钮开始实时检测</p>
                </div>
                <div class="placeholder-tips">
                  <el-alert title="使用提示" type="info" :closable="false">
                    <ul class="tips-list" style="color: #333;">
                      <li>确保摄像头已正确连接</li>
                      <li>在光线良好的环境下检测效果更佳</li>
                      <li>实时检测会持续处理摄像头画面</li>
                    </ul>
                  </el-alert>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <!-- 检测结果 -->
        <div v-if="detectionResult" class="result-section">
          <el-card class="result-card" shadow="never">
            <template #header>
              <div class="result-header">
                <el-icon><Finished /></el-icon>
                <span>视频检测结果</span>
                <el-tag :type="detectionResult.total_detections > 0 ? 'warning' : 'success'" size="small">
                  {{ detectionResult.total_detections > 0 ? `发现${detectionResult.total_detections}处缺陷` : '未发现缺陷' }}
                </el-tag>
              </div>
            </template>

            <!-- 视频对比 -->
            <div class="video-comparison">
              <div class="comparison-item">
                <div class="comparison-header">
                  <el-icon><VideoCamera /></el-icon>
                  <span>原始视频</span>
                </div>
                <div class="comparison-video">
                  <video
                    :src="`${API_BASE}${detectionResult.video_url}`"
                    controls
                    class="result-video"
                  ></video>
                  <div class="video-label">原始</div>
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
                <div class="comparison-video">
                  <video
                    :src="`${API_BASE}${detectionResult.processed_video_url}`"
                    controls
                    class="result-video"
                  ></video>
                  <div class="video-label">结果</div>
                </div>
              </div>
            </div>

            <!-- 检测统计 -->
            <div class="detection-stats">
              <el-row :gutter="20">
                <el-col :span="4">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><Timer /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ new Date().toLocaleTimeString() }}</div>
                      <div class="stat-label">完成时间</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="4">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><DataAnalysis /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ detectionResult.avg_confidence?.toFixed(4) || '0.0000' }}</div>
                      <div class="stat-label">平均置信度</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="4">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><Collection /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ detectionResult.total_detections }}</div>
                      <div class="stat-label">缺陷数量</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="4">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><DataBoard /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ detectionResult.model_used }}</div>
                      <div class="stat-label">使用模型</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="4">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><Clock /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ detectionResult.duration }}秒</div>
                      <div class="stat-label">视频时长</div>
                    </div>
                  </div>
                </el-col>
                <el-col :span="4">
                  <div class="stat-item">
                    <div class="stat-icon">
                      <el-icon><TrendCharts /></el-icon>
                    </div>
                    <div class="stat-content">
                      <div class="stat-value">{{ detectionResult.fps }} FPS</div>
                      <div class="stat-label">处理帧率</div>
                    </div>
                  </div>
                </el-col>
              </el-row>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button @click="downloadVideo(detectionResult.processed_video_url)" type="success" size="large">
                <el-icon><Download /></el-icon>
                下载结果视频
              </el-button>
              <el-button @click="viewRecord(detectionResult.record_id)" type="primary" size="large">
                <el-icon><DocumentAdd /></el-icon>
                查看详细记录
              </el-button>
              <el-button @click="exportVideoReport" type="warning" size="large">
                <el-icon><Document /></el-icon>
                导出检测报告
              </el-button>
            </div>
          </el-card>
        </div>

        <!-- 摄像头统计信息 -->
        <div v-if="activeMode === 'camera' && cameraActive" class="camera-stats-section">
          <el-card class="stats-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><TrendCharts /></el-icon>
                <span>实时统计</span>
              </div>
            </template>

            <div class="camera-metrics">
              <div class="metric-item">
                <div class="metric-icon">
                  <el-icon><Timer /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-value">{{ formatRunTime }}</div>
                  <div class="metric-label">运行时长</div>
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-icon">
                  <el-icon><DataLine /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-value">{{ estimatedFps }} FPS</div>
                  <div class="metric-label">实时帧率</div>
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-icon">
                  <el-icon><Cpu /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-value">{{ selectedModel }}</div>
                  <div class="metric-label">检测模型</div>
                </div>
              </div>

              <div class="metric-item">
                <div class="metric-icon">
                  <el-icon><VideoCamera /></el-icon>
                </div>
                <div class="metric-content">
                  <div class="metric-value">摄像头 {{ selectedCamera }}</div>
                  <div class="metric-label">设备编号</div>
                </div>
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
                <el-icon><VideoCamera /></el-icon>
                <span>检测模式</span>
              </div>
              <el-tag :type="activeMode === 'video' ? 'primary' : 'success'" effect="dark">
                {{ activeMode === 'video' ? '视频文件' : '实时摄像头' }}
              </el-tag>
            </div>
          </div>
        </el-card>

        <!-- 视频检测记录 -->
        <el-card class="info-card" shadow="hover">
          <template #header>
            <div class="card-header">
              <el-icon><Clock /></el-icon>
              <span>视频记录</span>
            </div>
          </template>
          <div class="video-records">
            <div v-if="videoRecords.length === 0" class="empty-records">
              <el-empty description="暂无视频检测记录" :image-size="100" />
            </div>
            <div v-else class="record-list">
              <div v-for="(record, index) in videoRecords" :key="index" class="record-item">
                <div class="record-header">
                  <el-icon>
                    <component :is="record.type === 'video' ? 'VideoCamera' : 'Camera'" />
                  </el-icon>
                  <span class="record-time">{{ record.time }}</span>
                  <el-tag size="small" :type="record.type === 'video' ? 'primary' : 'success'" class="record-type">
                    {{ record.type === 'video' ? '视频' : '摄像头' }}
                  </el-tag>
                </div>
                <div class="record-info">
                  <div class="record-name">{{ record.name }}</div>
                  <div class="record-stats">
                    <el-tag size="small" :type="record.defects > 0 ? 'danger' : 'success'">
                      {{ record.defects }}处缺陷
                    </el-tag>
                    <span class="record-duration">{{ record.duration }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="record-footer">
              <el-button @click="goToHistory" type="text" size="small">查看全部记录 →</el-button>
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
              <span>视频检测可能需要较长时间，请耐心等待</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>摄像头检测需要授予摄像头访问权限</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>检测结果会自动保存到历史记录中</span>
            </div>
            <div class="tip-item">
              <el-icon><InfoFilled /></el-icon>
              <span>视频文件建议使用MP4格式以获得最佳兼容性</span>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 页脚 -->
    <div class="footer">
      <div class="footer-content">
        <div class="footer-info">
          <p>© 2024 绝缘子缺陷检测系统 v3.0</p>
          <p>视频检测模块 | 基于 YOLOv11 深度学习模型</p>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

const icons = ElementPlusIconsVue
const router = useRouter()

// ==================== 响应式数据 ====================
const activeMode = ref('video') // 'video' 或 'camera'

// 视频检测相关
const selectedModel = ref('best.pt')
const modelList = ref([])
const modelInfo = ref('')
const confThreshold = ref(0.25)
const iouThreshold = ref(0.45)
const selectedVideo = ref(null)
const videoPreviewUrl = ref('')
const videoDuration = ref(0)
const videoPlayer = ref(null)
const videoLoading = ref(false)
const videoError = ref('')
const detectionResult = ref(null)
const isDragOver = ref(false)
const modelLoaded = ref(true)
const videoRecords = ref([])

// 后端连接状态
const backendStatus = ref({
    connected: false,
    lastChecked: null,
    error: null
})

// 设备选择相关
const selectedDevice = ref('auto')
const forceCpu = ref(false)
const deviceInfo = ref(null)
const loadingDevice = ref(false)

// 定时器
let backendCheckInterval = null

// 摄像头检测相关
const selectedCamera = ref('0')
const cameraActive = ref(false)
const cameraStreamUrl = ref('')
const cameraStartTime = ref(null)
const cameraEventSource = ref(null)
const estimatedFps = ref(0)
const frameCount = ref(0)
const lastFrameTime = ref(0)

// 本地摄像头相关
const cameraSource = ref('server') // 'server' 或 'local'
const localStream = ref(null)
const localVideoRef = ref(null)
const localCanvasRef = ref(null)
const localCaptureInterval = ref(null)

// ==================== 计算属性 ====================
const formatRunTime = computed(() => {
  if (!cameraStartTime.value) return '0秒'
  const seconds = Math.floor((Date.now() - cameraStartTime.value) / 1000)
  if (seconds < 60) return `${seconds}秒`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}分${remainingSeconds}秒`
})

// ==================== API基础地址 ====================
const getApiBase = () => {
  const hostname = window.location.hostname
  const protocol = window.location.protocol

  // 本地开发环境
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return `${protocol}//${hostname}:5000`
  }

  // 内网环境
  if (hostname.startsWith('192.168.') || hostname.startsWith('10.') || hostname.startsWith('172.')) {
    return `${protocol}//${hostname}:5000`
  }

  // 默认使用当前域
  return `${protocol}//${hostname}${window.location.port ? ':' + window.location.port : ''}`
}

const API_BASE = getApiBase()
console.log('🔧 API基础地址:', API_BASE)

// ==================== 后端连接状态检测 ====================
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
                currentDevice: 'CPU',
                gpuName: '',
                gpuMemory: 0
            }
            return
        }
        
        const res = await axios.get(`${API_BASE}/api/device_info`, {
            timeout: 5000
        })
        if (res.data.success) {
            deviceInfo.value = {
                hasGpu: res.data.cuda_available || false,
                currentDevice: res.data.current_device || 'CPU',
                gpuName: res.data.devices?.find(d => d.type === 'GPU')?.name || '',
                gpuMemory: 0
            }
            console.log('✅ 加载设备信息成功:', deviceInfo.value)
        } else {
            throw new Error('获取设备信息失败')
        }
    } catch (err) {
        console.error('❌ 加载设备信息失败:', err)
        deviceInfo.value = {
            hasGpu: false,
            currentDevice: 'CPU',
            gpuName: '',
            gpuMemory: 0
        }
    } finally {
        loadingDevice.value = false
    }
}

// ==================== 生命周期钩子 ====================
onMounted(async () => {
  // 检查后端连接状态
  await checkBackendStatus()
  // 加载设备信息
  await loadDeviceInfo()
  // 加载模型列表
  await loadModelList()
  // 加载视频记录
  await loadVideoRecords()
  
  // 定期检查后端状态（每10秒）
  backendCheckInterval = setInterval(async () => {
    await checkBackendStatus()
  }, 10000)
  
  window.addEventListener('beforeunload', handleBeforeUnload)
})

onUnmounted(() => {
  if (cameraActive.value) {
    stopCamera()
  }
  if (cameraEventSource.value) {
    cameraEventSource.value.close()
  }
  // 清除定时器
  if (backendCheckInterval) {
    clearInterval(backendCheckInterval)
  }
  window.removeEventListener('beforeunload', handleBeforeUnload)
})

const handleBeforeUnload = () => {
  if (cameraActive.value) {
    stopCamera()
  }
}

// ==================== 方法 ====================
// 加载模型列表
const loadModelList = async () => {
  try {
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

// 加载视频记录
const loadVideoRecords = async () => {
  try {
    const res = await axios.get(`${API_BASE}/api/history`)
    // 过滤出视频和摄像头检测记录
    const videoRecordsData = res.data
      .filter(record => record.detection_type === 'video' || record.detection_type === 'camera')
      .slice(0, 5) // 只取最近的5条

    videoRecords.value = videoRecordsData.map(record => ({
      name: record.filename || `摄像头检测 ${record.id}`,
      time: record.detect_time,
      defects: record.total_objects || 0,
      duration: record.duration ? `${record.duration.toFixed(1)}秒` : '--',
      type: record.detection_type
    }))
  } catch (err) {
    console.error('加载视频记录失败:', err)
  }
}

// 模型切换
const onModelChange = () => {
  modelInfo.value = selectedModel.value
  modelLoaded.value = true
}

// 设备变更处理
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
        ElNotification({
            title: '强制CPU模式',
            message: '已启用强制CPU模式，将忽略GPU设置',
            type: 'info',
            duration: 3000
        })
    }
}

// 切换设备
const switchDevice = (deviceType) => {
    console.log('切换设备:', deviceType)
    // 这里可以添加设备切换的逻辑
    // 例如，通知用户设备切换成功
    ElNotification({
        title: '设备切换成功',
        message: `已切换到${deviceType === 'auto' ? '自动选择' : deviceType === 'gpu' ? 'GPU加速' : 'CPU模式'}`,
        type: 'success',
        duration: 2000
    })
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
  handleVideoFile(file)
}

// 触发文件选择
const triggerVideoInput = () => {
  document.getElementById('video-input').click()
}

// 文件选择处理
const onVideoSelected = (event) => {
  const file = event.target.files[0]
  handleVideoFile(file)
}

// 处理视频文件
const handleVideoFile = (file) => {
  if (!file) return

  // 验证文件类型
  const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-matroska']
  const validExtensions = ['.mp4', '.avi', '.mov', '.mkv']
  const fileExtension = file.name.toLowerCase().slice(file.name.lastIndexOf('.'))

  if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
    videoError.value = '请上传有效的视频文件（MP4/AVI/MOV/MKV）'
    return
  }

  // 验证文件大小（限制100MB）
  if (file.size > 100 * 1024 * 1024) {
    videoError.value = '视频文件大小不能超过100MB'
    return
  }

  selectedVideo.value = file
  videoError.value = ''
  detectionResult.value = null

  // 创建预览URL
  videoPreviewUrl.value = URL.createObjectURL(file)
}

// 视频加载完成
const onVideoLoaded = () => {
  if (videoPlayer.value) {
    videoDuration.value = videoPlayer.value.duration
  }
}

// 播放视频
const playVideo = () => {
  if (videoPlayer.value) {
    videoPlayer.value.play()
  }
}

// 清除视频
const clearVideo = () => {
  selectedVideo.value = null
  videoPreviewUrl.value = ''
  videoDuration.value = 0
  detectionResult.value = null
  document.getElementById('video-input').value = ''
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化时间
const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${minutes}:${secs.toString().padStart(2, '0')}`
}

// 获取视频类型
const getVideoType = (mimeType) => {
  const types = {
    'video/mp4': 'MP4 视频',
    'video/avi': 'AVI 视频',
    'video/quicktime': 'MOV 视频',
    'video/x-matroska': 'MKV 视频'
  }
  return types[mimeType] || '视频文件'
}

// 格式化置信度
const formatConfidence = (value) => {
  return `置信度: ${value.toFixed(2)}`
}

// 格式化IoU
const formatIoU = (value) => {
  return `IoU: ${value.toFixed(2)}`
}

// 视频检测
const detectVideo = async () => {
  if (!selectedVideo.value) {
    videoError.value = '请先选择一个视频文件'
    return
  }

  // 检查后端连接状态
  const isConnected = await checkBackendStatus()
  if (!isConnected) {
    videoError.value = '后端服务未连接，请检查后端是否运行'
    return
  }

  const formData = new FormData()
  formData.append('video', selectedVideo.value)
  formData.append('model', selectedModel.value)
  formData.append('conf', confThreshold.value.toString())
  formData.append('iou', iouThreshold.value.toString())
  formData.append('use_gpu', (selectedDevice.value === 'gpu' || selectedDevice.value === 'auto').toString())
  formData.append('force_cpu', forceCpu.value.toString())

  videoLoading.value = true
  videoError.value = ''

  try {
    const response = await axios.post(`${API_BASE}/api/detect_video`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000 // 5分钟超时
    })

    if (response.data.success) {
      detectionResult.value = response.data
      console.log('视频检测成功:', response.data)

      // 重新加载视频记录
      await loadVideoRecords()

      ElNotification({
        title: '检测成功',
        message: `视频处理完成，发现${response.data.total_detections}处缺陷，使用设备: ${response.data.device_used || 'CPU'}`,
        type: 'success',
        duration: 5000
      })
    } else {
      videoError.value = response.data.error || '视频检测失败'
    }
  } catch (err) {
    console.error('视频检测失败:', err)
    videoError.value = `检测失败: ${err.response?.data?.error || err.message}`
    ElNotification({
      title: '检测失败',
      message: videoError.value,
      type: 'error',
      duration: 5000
    })
  } finally {
    videoLoading.value = false
  }
}

// 下载视频
const downloadVideo = (videoUrl) => {
  if (!videoUrl) return
  const fullUrl = `${API_BASE}${videoUrl}`
  window.open(fullUrl, '_blank')
}

// 查看记录
const viewRecord = (recordId) => {
  router.push(`/record/${recordId}`)
}

// 导出视频报告
const exportVideoReport = async () => {
  if (!detectionResult.value) return

  import('xlsx').then(xlsx => {
    // 准备数据
    const data = [
      ['视频检测报告', '', '', '', '', ''],
      ['检测时间', new Date().toLocaleString(), '', '', '', ''],
      ['视频文件', detectionResult.value.video_url, '', '', '', ''],
      ['检测模型', detectionResult.value.model_used, '', '', '', ''],
      ['视频时长', `${detectionResult.value.duration}秒`, '', '', '', ''],
      ['总帧数', detectionResult.value.total_frames, '', '', '', ''],
      ['处理帧率', `${detectionResult.value.fps} FPS`, '', '', '', ''],
      ['缺陷总数', detectionResult.value.total_detections, '', '', '', ''],
      ['平均置信度', detectionResult.value.avg_confidence?.toFixed(4) || '0.0000', '', '', '', ''],
      [],
      ['检测参数', '', '', '', '', ''],
      ['置信度阈值', confThreshold.value, '', '', '', ''],
      ['IoU阈值', iouThreshold.value, '', '', '', ''],
      [],
      ['检测统计', '', '', '', '', '']
    ]

    // 创建Excel工作簿
    const worksheet = xlsx.utils.aoa_to_sheet(data)
    const workbook = xlsx.utils.book_new()
    xlsx.utils.book_append_sheet(workbook, worksheet, '视频检测报告')

    // 生成文件名
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
    const filename = `视频检测报告_${timestamp}.xlsx`

    // 导出文件
    xlsx.writeFile(workbook, filename)

    ElNotification({
      title: '导出成功',
      message: `报告已保存为: ${filename}`,
      type: 'success',
      duration: 3000
    })
  }).catch(err => {
    console.error('导出失败:', err)
    ElNotification({
      title: '导出失败',
      message: '导出失败，请重试',
      type: 'error',
      duration: 3000
    })
  })
}

// ==================== 摄像头功能 ====================
// 启动摄像头
const startCamera = async () => {
  // 检查后端连接状态
  const isConnected = await checkBackendStatus()
  if (!isConnected) {
    ElNotification({
      title: '启动失败',
      message: '后端服务未连接，请检查后端是否运行',
      type: 'error',
      duration: 5000
    })
    return
  }

  try {
    if (cameraSource.value === 'server') {
      // 服务器摄像头
      const response = await axios.post(`${API_BASE}/api/camera/start`, {
        camera_id: parseInt(selectedCamera.value),
        use_gpu: (selectedDevice.value === 'gpu' || selectedDevice.value === 'auto'),
        force_cpu: forceCpu.value
      })

      if (response.data.success) {
        cameraActive.value = true
        cameraStartTime.value = Date.now()
        frameCount.value = 0
        lastFrameTime.value = Date.now()

        // 开始接收视频流
        startCameraStream()

        ElNotification({
          title: '摄像头启动成功',
          message: `服务器摄像头 ${selectedCamera.value} 已启动`,
          type: 'success',
          duration: 3000
        })
      } else {
        ElNotification({
          title: '启动摄像头失败',
          message: response.data.message,
          type: 'error',
          duration: 3000
        })
      }
    } else {
      // 本地摄像头
      // 请求摄像头权限
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: false
      })

      // 显示本地摄像头流
      if (localVideoRef.value) {
        localVideoRef.value.srcObject = stream
        localStream.value = stream
      }

      cameraActive.value = true
      cameraStartTime.value = Date.now()
      frameCount.value = 0
      lastFrameTime.value = Date.now()

      // 开始本地摄像头检测
      startLocalCameraStream()

      ElNotification({
        title: '摄像头启动成功',
        message: '本地摄像头已启动',
        type: 'success',
        duration: 3000
      })
    }
  } catch (err) {
    console.error('启动摄像头失败:', err)
    if (cameraSource.value === 'local') {
      ElNotification({
        title: '启动摄像头失败',
        message: '无法访问本地摄像头，请检查权限设置',
        type: 'error',
        duration: 3000
      })
    } else {
      ElNotification({
        title: '启动摄像头失败',
        message: '请检查后端服务是否正常运行',
        type: 'error',
        duration: 3000
      })
    }
  }
}

// 停止摄像头
const stopCamera = async () => {
  try {
    if (cameraSource.value === 'server') {
      // 停止服务器摄像头
      const response = await axios.post(`${API_BASE}/api/camera/stop`)

      if (response.data.success) {
        cameraActive.value = false
        cameraStreamUrl.value = ''

        // 关闭EventSource
        if (cameraEventSource.value) {
          cameraEventSource.value.close()
          cameraEventSource.value = null
        }
      }
    } else {
      // 停止本地摄像头
      if (localStream.value) {
        localStream.value.getTracks().forEach(track => track.stop())
        localStream.value = null
      }
      if (localCaptureInterval.value) {
        clearInterval(localCaptureInterval.value)
        localCaptureInterval.value = null
      }
      cameraActive.value = false
    }

    ElNotification({
      title: '摄像头已停止',
      message: '实时检测已结束',
      type: 'info',
      duration: 3000
    })
  } catch (err) {
    console.error('停止摄像头失败:', err)
    // 即使失败也设置为非活动状态
    cameraActive.value = false
  }
}

// 开始服务器摄像头流
const startCameraStream = () => {
  // 使用EventSource接收服务器发送的事件流
  cameraEventSource.value = new EventSource(`${API_BASE}/api/camera/stream`)

  cameraEventSource.value.onmessage = (event) => {
    // 更新视频流URL
    cameraStreamUrl.value = `data:image/jpeg;base64,${event.data}`

    // 计算帧率
    frameCount.value++
    const now = Date.now()
    const elapsed = now - lastFrameTime.value

    // 每1秒更新一次帧率
    if (elapsed >= 1000) {
      estimatedFps.value = Math.round((frameCount.value * 1000) / elapsed)
      frameCount.value = 0
      lastFrameTime.value = now
    }
  }

  cameraEventSource.value.onerror = (error) => {
    console.error('摄像头流错误:', error)
    if (cameraActive.value) {
      stopCamera()
    }
  }
}

// 开始本地摄像头流
const startLocalCameraStream = () => {
  // 定期捕获本地摄像头帧并发送到后端
  localCaptureInterval.value = setInterval(async () => {
    if (!localVideoRef.value || !localCanvasRef.value) return

    try {
      // 捕获视频帧到canvas
      const video = localVideoRef.value
      const canvas = localCanvasRef.value
      const ctx = canvas.getContext('2d')

      // 设置canvas尺寸
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight

      // 绘制视频帧
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

      // 将canvas转换为base64
      const base64Image = canvas.toDataURL('image/jpeg', 0.8)
      
      // 发送到后端进行检测
      const response = await axios.post(`${API_BASE}/api/camera/detect_frame`, {
        image: base64Image.split(',')[1], // 移除data:image/jpeg;base64,前缀
        use_gpu: (selectedDevice.value === 'gpu' || selectedDevice.value === 'auto'),
        force_cpu: forceCpu.value
      })

      if (response.data.success) {
        // 更新视频流URL为检测结果
        cameraStreamUrl.value = `data:image/jpeg;base64,${response.data.image}`

        // 计算帧率
        frameCount.value++
        const now = Date.now()
        const elapsed = now - lastFrameTime.value

        // 每1秒更新一次帧率
        if (elapsed >= 1000) {
          estimatedFps.value = Math.round((frameCount.value * 1000) / elapsed)
          frameCount.value = 0
          lastFrameTime.value = now
        }
      }
    } catch (err) {
      console.error('本地摄像头检测失败:', err)
    }
  }, 100) // 每100ms捕获一帧，约10FPS
}

// ==================== 导航功能 ====================
const goToHome = () => {
  router.push('/upload')
}

const goToHistory = () => {
  router.push('/history')
}

const goToAbout = () => {
  router.push('/about')
}
</script>

<style scoped>
.video-detect-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  font-family: 'Inter', 'Segoe UI', 'Microsoft YaHei', sans-serif;
  color: #e2e8f0;
}

/* 顶部导航栏 */
.top-nav {
  background: linear-gradient(135deg, rgba(30, 60, 114, 0.95) 0%, rgba(42, 82, 152, 0.95) 100%);
  backdrop-filter: blur(10px);
  color: white;
  padding: 20px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
  position: sticky;
  top: 0;
  z-index: 1000;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.nav-brand h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(45deg, #a8edea, #fed6e3);
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
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
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
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  color: #e2e8f0;
}

.config-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color:white;
}

.card-header .el-icon {
  font-size: 24px;
}

/* 模式选择器 */
.mode-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mode-radio-group {
  width: 100%;
}

.mode-radio-group :deep(.el-radio-button) {
  flex: 1;
}

.mode-radio-group :deep(.el-radio-button__inner) {
  width: 100%;
  padding: 15px;
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.mode-radio-group :deep(.el-radio-button__inner:hover) {
  background: rgba(255, 255, 255, 0.1);
}

.mode-radio-group :deep(.el-radio-button__orig-radio:checked + .el-radio-button__inner) {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  border-color: #4f46e5;
  color: white;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4);
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

.model-select :deep(.el-select__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.model-select :deep(.el-select__placeholder) {
  color: rgba(255, 255, 255, 0.5);
}

.model-info .el-tag {
  padding: 8px 16px;
  font-size: 14px;
  border-radius: 8px;
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.3);
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
  color: #e2e8f0;
}

.param-control :deep(.el-slider) {
  margin: 8px 0;
}

.param-control :deep(.el-slider__runway) {
  background: rgba(255, 255, 255, 0.1);
}

.param-control :deep(.el-slider__bar) {
  background: linear-gradient(90deg, #4f46e5, #7c3aed);
}

.param-control :deep(.el-slider__button) {
  border-color: #4f46e5;
  background: #4f46e5;
}

.param-desc {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 8px;
  line-height: 1.5;
}

/* 摄像头控制 */
.camera-control {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.control-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.control-label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #e2e8f0;
  font-weight: 500;
}

.camera-select {
  width: 100%;
}

.camera-select :deep(.el-select__wrapper) {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.control-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.control-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: none;
}

.control-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
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
  border: none;
}

.action-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.3);
}

/* 预览区域 */
.preview-area {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.upload-card, .camera-card {
  border-radius: 16px;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  min-height: 500px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.upload-header, .camera-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
}

.upload-header .el-icon, .camera-header .el-icon {
  font-size: 24px;
  color: #4f46e5;
}

/* 上传区域 */
.upload-zone {
  border: 3px dashed rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  padding: 60px 40px;
  background: rgba(255, 255, 255, 0.05);
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.upload-zone:hover {
  border-color: #4f46e5;
  background: rgba(79, 70, 229, 0.1);
}

.upload-zone.drag-over {
  border-color: #4f46e5;
  background: rgba(79, 70, 229, 0.2);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.4);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(79, 70, 229, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(79, 70, 229, 0);
  }
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.upload-icon {
  color: #4f46e5;
}

.upload-text h3 {
  margin: 0 0 8px 0;
  color: #e2e8f0;
  font-size: 24px;
  font-weight: 600;
}

.upload-text p {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.select-btn {
  padding: 12px 32px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #4f46e5, #7c3aed);
  border: none;
  color: white;
}

.select-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(79, 70, 229, 0.4);
}

/* 视频预览 */
.video-preview {
  width: 100%;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
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
  color: #4f46e5;
}

.file-details h4 {
  margin: 0 0 4px 0;
  color: #e2e8f0;
  font-size: 16px;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.file-details p {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.preview-container {
  position: relative;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.preview-video {
  width: 100%;
  height: auto;
  display: block;
  background: #000;
}

.video-info-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.video-info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 14px;
}

/* 摄像头预览 */
.camera-preview {
  height: 500px;
}

.camera-stream {
  height: 100%;
  position: relative;
}

.camera-frame {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #000;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}

.camera-feed {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.camera-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.camera-status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-weight: 500;
}

.camera-status .el-icon {
  color: #10b981;
}

.camera-stats {
  display: flex;
  gap: 20px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  font-size: 14px;
}

/* 摄像头占位符 */
.camera-placeholder {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-content {
  text-align: center;
  padding: 40px;
}

.placeholder-icon {
  color: rgba(255, 255, 255, 0.2);
  margin-bottom: 20px;
}

.placeholder-text h3 {
  margin: 0 0 8px 0;
  color: #e2e8f0;
  font-size: 24px;
  font-weight: 600;
}

.placeholder-text p {
  margin: 0;
  color: #94a3b8;
  font-size: 16px;
}

.placeholder-tips {
  margin-top: 30px;
  max-width: 400px;
}

.tips-list {
  text-align: left;
  padding-left: 20px;
  color: #e2e8f0;
}

.tips-list li {
  margin: 8px 0;
}

/* 错误提示 */
.error-alert {
  margin-top: 20px;
}

.error-alert :deep(.el-alert) {
  border-radius: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  color: #fecaca;
}

.error-alert :deep(.el-alert__title) {
  color: #fecaca;
}

/* 结果部分 */
.result-section {
  margin-top: 20px;
}

.result-card {
  border-radius: 16px;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 20px;
  font-weight: 600;
  color: #e2e8f0;
}

.result-header .el-icon {
  font-size: 24px;
  color: #10b981;
}

/* 视频对比 */
.video-comparison {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  margin: 40px 0;
  padding: 40px;
  background: rgba(255, 255, 255, 0.05);
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
  color: #e2e8f0;
}

.comparison-video {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  transition: transform 0.3s ease;
  background: #000;
}

.comparison-video:hover {
  transform: translateY(-4px);
}

.result-video {
  width: 100%;
  height: 300px;
  object-fit: contain;
  background: #000;
}

.video-label {
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
  color: #4f46e5;
}

/* 检测统计 */
.detection-stats {
  margin: 40px 0;
  padding: 30px;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.2) 0%, rgba(124, 58, 237, 0.2) 100%);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  backdrop-filter: blur(10px);
  transition: transform 0.3s ease;
  height: 100px;
}

.stat-item:hover {
  transform: translateY(-4px);
  background: rgba(255, 255, 255, 0.15);
}

.stat-icon {
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
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
  color: #e2e8f0;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #94a3b8;
  font-weight: 500;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.action-buttons .el-button {
  padding: 15px 30px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 12px;
  border: none;
  transition: all 0.3s ease;
}

.action-buttons .el-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
}

/* 摄像头统计信息 */
.camera-stats-section {
  margin-top: 20px;
}

.stats-card {
  border-radius: 16px;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.camera-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.metric-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.metric-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  border-radius: 10px;
  font-size: 24px;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 18px;
  font-weight: 700;
  color: #e2e8f0;
  margin-bottom: 4px;
}

.metric-label {
  font-size: 12px;
  color: #94a3b8;
}

/* 信息面板 */
.info-panel {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.info-card {
  border-radius: 16px;
  background: rgba(30, 41, 59, 0.8);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.status-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.status-label {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #e2e8f0;
  font-weight: 500;
}

.status-label .el-icon {
  color: #4f46e5;
}

/* 视频记录 */
.video-records {
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
  flex-direction: column;
  gap: 8px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.record-item:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(4px);
}

.record-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4f46e5;
  font-size: 12px;
  font-weight: 500;
}

.record-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.record-name {
  font-weight: 600;
  color: #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.record-duration {
  font-size: 12px;
  color: #94a3b8;
}

.record-footer {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.record-footer .el-button {
  color: #4f46e5;
}

.record-footer .el-button:hover {
  color: #7c3aed;
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
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.tip-item:hover {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.2) 0%, rgba(124, 58, 237, 0.2) 100%);
  transform: translateX(4px);
}

.tip-item .el-icon {
  color: #4f46e5;
  margin-top: 2px;
}

.tip-item span {
  color: #e2e8f0;
  font-size: 14px;
  line-height: 1.5;
}

/* 页脚 */
.footer {
  margin-top: 60px;
  padding: 40px 0;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.95) 100%);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
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

  .preview-area {
    order: 1;
  }

  .video-comparison {
    flex-direction: column;
    gap: 30px;
  }

  .detection-stats .el-col {
    margin-bottom: 16px;
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

  .action-buttons {
    flex-direction: column;
    align-items: stretch;
  }

  .camera-metrics {
    grid-template-columns: 1fr;
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

@keyframes cameraActive {
  0% {
    border-color: rgba(16, 185, 129, 0.5);
  }
  50% {
    border-color: rgba(16, 185, 129, 1);
  }
  100% {
    border-color: rgba(16, 185, 129, 0.5);
  }
}

.camera-frame {
  animation: cameraActive 2s infinite;
}

@keyframes streamIndicator {
  0% {
    opacity: 0.5;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.5;
  }
}

.camera-status .el-icon {
  animation: streamIndicator 2s infinite;
}
</style>
