# API接口文档

## 1. 接口概述

本API文档描述了绝缘子缺陷检测系统的后端API接口，包括核心检测API、设备管理API、历史记录API和系统API。所有API接口均以`/api`为前缀，采用RESTful设计风格。

## 2. 接口列表

### 2.1 核心检测API

| 接口路径 | 方法 | 功能描述 | 请求体 | 响应体 | 状态码 |
|---------|------|---------|--------|--------|--------|
| `/api/detect` | POST | 图片检测 | `multipart/form-data` | `JSON` | 200/400/500 |
| `/api/video/detect` | POST | 视频检测 | `multipart/form-data` | `JSON` | 200/400/500 |
| `/api/camera/start` | POST | 启动服务器摄像头检测 | `JSON` | `JSON` | 200/400/500 |
| `/api/camera/stop` | POST | 停止服务器摄像头检测 | `JSON` | `JSON` | 200/400/500 |
| `/api/camera/stream` | GET | 获取服务器摄像头视频流 | N/A | `Video Stream` | 200/500 |
| `/api/camera/detect_frame` | POST | 处理本地摄像头帧 | `JSON` | `JSON` | 200/400/500 |

### 2.2 设备管理API

| 接口路径 | 方法 | 功能描述 | 请求体 | 响应体 | 状态码 |
|---------|------|---------|--------|--------|--------|
| `/api/device_info` | GET | 获取当前设备信息 | N/A | `JSON` | 200/500 |
| `/api/switch_device` | POST | 切换检测设备 | `JSON` | `JSON` | 200/400/500 |

### 2.3 历史记录API

| 接口路径 | 方法 | 功能描述 | 请求体 | 响应体 | 状态码 |
|---------|------|---------|--------|--------|--------|
| `/api/history` | GET | 获取所有历史检测记录 | N/A | `JSON` | 200/500 |
| `/api/records/<int:record_id>` | GET | 获取单条记录详细信息 | N/A | `JSON` | 200/404/500 |
| `/api/records/<int:record_id>` | DELETE | 删除单条记录 | N/A | `JSON` | 200/404/500 |
| `/api/records/batch_delete` | POST | 批量删除记录 | `JSON` | `JSON` | 200/400/500 |

### 2.4 系统API

| 接口路径 | 方法 | 功能描述 | 请求体 | 响应体 | 状态码 |
|---------|------|---------|--------|--------|--------|
| `/api/health` | GET | 健康检查端点 | N/A | `JSON` | 200/500 |

## 3. 详细接口说明

### 3.1 核心检测API

#### 3.1.1 POST /api/detect

**功能描述**：处理图片上传和缺陷检测

**请求体**：
```multipart/form-data
image: <图片文件>
model: <模型名称，可选>
confidence: <置信度阈值，可选>
iou: <IoU阈值，可选>
```

**响应体**：
```json
{
  "success": true,
  "filename": "原始文件名",
  "result_filename": "结果文件名",
  "detections": [
    {
      "class": "缺陷类型",
      "confidence": 0.95,
      "box": [x1, y1, x2, y2]
    }
  ],
  "total_detections": 5,
  "model_used": "best.pt",
  "confidence_avg": 0.85,
  "device_used": "cuda:0",
  "detect_time": "2024-01-01 12:00:00"
}
```

**状态码**：
- 200: 检测成功
- 400: 请求参数错误
- 500: 服务器内部错误

#### 3.1.2 POST /api/video/detect

**功能描述**：处理视频上传和缺陷检测

**请求体**：
```multipart/form-data
video: <视频文件>
model: <模型名称，可选>
confidence: <置信度阈值，可选>
iou: <IoU阈值，可选>
```

**响应体**：
```json
{
  "success": true,
  "filename": "原始文件名",
  "result_filename": "结果文件名",
  "video_path": "视频路径",
  "processed_video_path": "处理后的视频路径",
  "detections": [
    {
      "frame": 10,
      "objects": [
        {
          "class": "缺陷类型",
          "confidence": 0.95,
          "box": [x1, y1, x2, y2]
        }
      ]
    }
  ],
  "total_detections": 25,
  "model_used": "best.pt",
  "confidence_avg": 0.82,
  "duration": 10.5,
  "frame_count": 315,
  "fps": 30.0,
  "device_used": "cuda:0",
  "detect_time": "2024-01-01 12:00:00"
}
```

**状态码**：
- 200: 检测成功
- 400: 请求参数错误
- 500: 服务器内部错误

#### 3.1.3 POST /api/camera/start

**功能描述**：启动服务器摄像头检测

**请求体**：
```json
{
  "camera_id": 0,  // 摄像头ID，默认为0
  "model": "best.pt",  // 模型名称
  "confidence": 0.5,  // 置信度阈值
  "iou": 0.45  // IoU阈值
}
```

**响应体**：
```json
{
  "success": true,
  "message": "摄像头检测已启动",
  "camera_id": 0,
  "stream_url": "/api/camera/stream"
}
```

**状态码**：
- 200: 启动成功
- 400: 请求参数错误
- 500: 服务器内部错误

#### 3.1.4 POST /api/camera/stop

**功能描述**：停止服务器摄像头检测

**请求体**：
```json
{
  "camera_id": 0  // 摄像头ID
}
```

**响应体**：
```json
{
  "success": true,
  "message": "摄像头检测已停止"
}
```

**状态码**：
- 200: 停止成功
- 400: 请求参数错误
- 500: 服务器内部错误

#### 3.1.5 GET /api/camera/stream

**功能描述**：获取服务器摄像头视频流

**请求体**：N/A

**响应体**：视频流 (MJPEG格式)

**状态码**：
- 200: 成功
- 500: 服务器内部错误

#### 3.1.6 POST /api/camera/detect_frame

**功能描述**：处理本地摄像头帧

**请求体**：
```json
{
  "image": "base64编码的图片数据",
  "use_gpu": true,  // 是否使用GPU
  "force_cpu": false  // 是否强制使用CPU
}
```

**响应体**：
```json
{
  "success": true,
  "image": "base64编码的处理后图片",
  "detections": [
    {
      "class": "缺陷类型",
      "confidence": 0.95,
      "box": [x1, y1, x2, y2]
    }
  ],
  "total_detections": 3,
  "device_used": "cuda:0"
}
```

**状态码**：
- 200: 处理成功
- 400: 请求参数错误
- 500: 服务器内部错误

### 3.2 设备管理API

#### 3.2.1 GET /api/device_info

**功能描述**：获取当前设备信息（CPU/GPU）

**请求体**：N/A

**响应体**：
```json
{
  "success": true,
  "device": {
    "type": "cuda:0",
    "name": "NVIDIA GeForce RTX 5060 Ti",
    "has_gpu": true,
    "gpu_count": 1,
    "cpu_info": "Intel(R) Core(TM) i7-12700K",
    "current_device": "cuda:0"
  }
}
```

**状态码**：
- 200: 成功
- 500: 服务器内部错误

#### 3.2.2 POST /api/switch_device

**功能描述**：切换检测设备（CPU/GPU）

**请求体**：
```json
{
  "device": "cuda:0"  // 设备名称，可选值："cpu", "cuda:0"
}
```

**响应体**：
```json
{
  "success": true,
  "message": "设备已切换",
  "current_device": "cuda:0"
}
```

**状态码**：
- 200: 切换成功
- 400: 请求参数错误
- 500: 服务器内部错误

### 3.3 历史记录API

#### 3.3.1 GET /api/history

**功能描述**：获取所有历史检测记录

**请求参数**：
- `page`: 页码，默认为1
- `page_size`: 每页记录数，默认为10
- `type`: 检测类型，可选值："image", "video", "camera"
- `start_date`: 开始日期，格式："YYYY-MM-DD"
- `end_date`: 结束日期，格式："YYYY-MM-DD"
- `search`: 搜索关键词

**响应体**：
```json
{
  "success": true,
  "total": 100,
  "page": 1,
  "page_size": 10,
  "records": [
    {
      "id": 1,
      "filename": "insulator_001.jpg",
      "result_filename": "result_insulator_001.jpg",
      "model_used": "best.pt",
      "total_objects": 5,
      "confidence_avg": 0.85,
      "detection_type": "image",
      "detect_time": "2024-01-01 12:00:00"
    }
  ]
}
```

**状态码**：
- 200: 成功
- 500: 服务器内部错误

#### 3.3.2 GET /api/records/<int:record_id>

**功能描述**：获取单条记录详细信息

**请求体**：N/A

**响应体**：
```json
{
  "success": true,
  "record": {
    "id": 1,
    "filename": "insulator_001.jpg",
    "result_filename": "result_insulator_001.jpg",
    "model_used": "best.pt",
    "confidence_avg": 0.85,
    "total_objects": 5,
    "confidence_threshold": 0.5,
    "iou_threshold": 0.45,
    "detections": [
      {
        "class": "破损",
        "confidence": 0.95,
        "box": [100, 200, 300, 400]
      }
    ],
    "detection_type": "image",
    "detect_time": "2024-01-01 12:00:00"
  }
}
```

**状态码**：
- 200: 成功
- 404: 记录不存在
- 500: 服务器内部错误

#### 3.3.3 DELETE /api/records/<int:record_id>

**功能描述**：删除单条记录

**请求体**：N/A

**响应体**：
```json
{
  "success": true,
  "message": "记录删除成功"
}
```

**状态码**：
- 200: 删除成功
- 404: 记录不存在
- 500: 服务器内部错误

#### 3.3.4 POST /api/records/batch_delete

**功能描述**：批量删除记录

**请求体**：
```json
{
  "ids": [1, 2, 3]  // 记录ID数组
}
```

**响应体**：
```json
{
  "success": true,
  "message": "批量删除成功",
  "deleted_count": 3
}
```

**状态码**：
- 200: 删除成功
- 400: 请求参数错误
- 500: 服务器内部错误

### 3.4 系统API

#### 3.4.1 GET /api/health

**功能描述**：健康检查端点，检查系统状态

**请求体**：N/A

**响应体**：
```json
{
  "status": "healthy",
  "model_loaded": true,
  "model_name": "best.pt",
  "device": "cuda:0",
  "server_time": "2024-01-01 12:00:00",
  "uptime": 3600
}
```

**状态码**：
- 200: 系统健康
- 500: 系统异常

## 4. 数据格式

### 4.1 检测结果格式

```json
{
  "class": "缺陷类型",  // 缺陷类型，如"破损", "污秽", "锈蚀"
  "confidence": 0.95,  // 置信度，0-1之间
  "box": [x1, y1, x2, y2]  // 边界框坐标，左上角和右下角
}
```

### 4.2 错误响应格式

```json
{
  "success": false,
  "message": "错误信息描述",
  "error": "详细错误信息"  // 可选
}
```

## 5. 调用示例

### 5.1 使用curl调用图片检测API

```bash
curl -X POST http://localhost:5000/api/detect \
  -F "image=@insulator.jpg" \
  -F "model=best.pt" \
  -F "confidence=0.5"
```

### 5.2 使用JavaScript调用本地摄像头检测API

```javascript
// 捕获摄像头帧
const canvas = document.createElement('canvas');
const ctx = canvas.getContext('2d');
const video = document.getElementById('video');

// 绘制视频帧到画布
ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

// 转换为base64
const imageData = canvas.toDataURL('image/jpeg').split(',')[1];

// 发送到后端
fetch('http://localhost:5000/api/camera/detect_frame', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    image: imageData,
    use_gpu: true
  })
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    // 处理返回的结果
    const resultImage = document.getElementById('result');
    resultImage.src = 'data:image/jpeg;base64,' + data.image;
    console.log('检测到的缺陷:', data.detections);
  }
});
```

## 6. 注意事项

1. **文件大小限制**：图片和视频上传有大小限制，默认最大为100MB
2. **并发限制**：系统对并发请求有一定限制，建议不要同时发送过多请求
3. **权限控制**：部分API可能需要用户认证，具体以实际实现为准
4. **错误处理**：客户端应妥善处理API返回的错误信息
5. **CORS配置**：前端调用API时需注意CORS配置，确保请求源被允许

## 7. 版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| 1.0.0 | 2024-01-01 | 初始版本，包含核心检测API |
| 1.1.0 | 2024-01-15 | 添加本地摄像头检测API |
| 1.2.0 | 2024-02-01 | 优化设备管理API，添加批量操作API |

## 8. 联系方式

如有API相关问题，请联系系统管理员。