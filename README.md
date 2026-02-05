# 绝缘子缺陷检测系统

## 项目简介

绝缘子缺陷检测系统是一个基于YOLOv11目标检测模型的智能化检测系统，用于识别电力系统中绝缘子的各种缺陷。系统支持图片、视频和摄像头实时检测，能够自动识别绝缘子的破损、污秽、锈蚀等缺陷类型。

### 主要功能

- **多模态检测**：支持图片、视频和摄像头实时检测
- **设备自适应**：自动检测和切换CPU/GPU设备，优化检测性能
- **实时摄像头检测**：支持本地和服务器摄像头实时检测
- **完整的历史记录**：支持查看、筛选、搜索和批量操作检测记录
- **详细的检测结果**：包括置信度、位置、类别等详细信息
- **美观的用户界面**：现代化的响应式界面，提供良好的用户体验

## 技术栈说明

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.5.26 | 前端框架 |
| TypeScript | 5.9.3 | 类型检查 |
| Element Plus | 2.13.0 | UI组件库 |
| Vite | 7.3.0 | 构建工具 |
| Pinia | 3.0.4 | 状态管理 |
| Vue Router | 4.6.4 | 路由管理 |
| Axios | 1.13.2 | HTTP客户端 |
| Chart.js | 4.5.1 | 数据可视化 |

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Flask | 3.1.2 | Web框架 |
| Python | 3.x | 开发语言 |
| YOLOv11 | 8.4.11 | 目标检测模型 |
| PyTorch | 2.10.0+cu128 | 深度学习框架 |
| OpenCV | 4.13.0.92 | 图像处理 |
| MySQL | - | 数据存储 |
| PyMySQL | 1.1.2 | 数据库驱动 |
| python-dotenv | 1.2.1 | 环境变量管理 |

## 快速开始指南

### 前置条件

- **前端**：Node.js 20.19.0 或更高版本
- **后端**：Python 3.8 或更高版本，CUDA 12.8（用于GPU加速）
- **数据库**：MySQL 5.7 或更高版本

### 安装步骤

#### 1. 克隆项目

```bash
git clone <https://github.com/Pursuerbin/git_yolo_detect.git>
cd git_yolo_detect
```

#### 2. 配置后端

```bash
# 进入后端目录
cd backend

# 创建虚拟环境（可选）
python -m venv venv

# 使用conda创建环境，名称为flask，python版本为3.11，需要下载miniconda
conda create -n flask python=3.11

# 激活虚拟环境
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，配置数据库连接等参数
```

#### 3. 配置数据库

```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE insulator_detection CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 退出MySQL
quit
```

#### 4. 配置前端

```bash
# 进入前端目录
cd ../frontend

# 安装依赖
npm install
```

### 运行项目

#### 1. 启动后端服务

```bash
# 进入后端目录
cd backend

# 启动服务
python app.py
```

后端服务默认运行在 `http://0.0.0.0:5000`。

#### 2. 启动前端服务

```bash
# 进入前端目录
cd frontend

# 启动开发服务器
npm run dev
```

前端服务默认运行在 `http://localhost:5173`。

### 构建生产版本

#### 1. 构建前端

```bash
# 进入前端目录
cd frontend

# 构建生产版本
npm run build

# 构建产物将生成在 dist 目录
```

#### 2. 部署后端

将后端代码和依赖部署到服务器，配置环境变量和数据库连接。

## 部署说明

### 环境变量配置

后端使用 `.env` 文件管理环境变量，主要配置项包括：

- **服务器配置**：`FLASK_ENV`, `SERVER_PORT`
- **数据库配置**：`DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`
- **路径配置**：`UPLOAD_FOLDER`, `RESULT_FOLDER`, `VIDEO_FOLDER`, `MODEL_FOLDER`
- **CORS配置**：`ALLOWED_ORIGINS`
- **设备配置**：`USE_GPU`

### 跨环境部署

#### Windows环境

- 使用 `cmd` 或 `PowerShell` 运行命令
- 虚拟环境激活命令：`venv\Scripts\activate`
- 路径分隔符使用 `\`

#### Linux环境

- 使用 `bash` 运行命令
- 虚拟环境激活命令：`source venv/bin/activate`
- 路径分隔符使用 `/`
- 可能需要安装额外的系统依赖

### 性能优化

1. **GPU加速**：确保安装了正确版本的CUDA和PyTorch，启用GPU加速
2. **模型优化**：使用量化或剪枝技术优化YOLO模型
3. **批量处理**：对于大量图片，使用批量处理提高效率
4. **缓存策略**：合理使用缓存，减少重复计算
5. **资源监控**：监控系统资源使用情况，及时调整配置

### 安全注意事项

1. **文件上传验证**：严格验证上传文件的类型和大小
2. **数据库安全**：使用参数化查询，防止SQL注入
3. **API访问控制**：实现适当的权限控制，防止未授权访问
4. **密码安全**：使用加密存储用户密码
5. **CORS配置**：在生产环境中严格配置CORS允许的源

## 目录结构

### 前端文件结构

```
frontend/
├── src/                 # 源代码
│   ├── views/           # 页面组件
│   │   ├── AboutView.vue        # 关于页面
│   │   ├── HistoryView.vue      # 历史记录页面 - 查看和管理检测记录
│   │   ├── LoginView.vue        # 登录页面
│   │   ├── RecordDetailView.vue # 记录详情页面 - 查看检测结果详情
│   │   ├── RegisterView.vue     # 注册页面
│   │   ├── UploadView.vue       # 图片上传检测页面 - 上传图片进行缺陷检测
│   │   └── VideoDetect.vue      # 视频/摄像头检测页面 - 视频文件或实时摄像头检测
│   ├── components/      # 通用组件
│   │   ├── __tests__/           # 测试文件
│   │   ├── icons/               # 图标组件
│   │   ├── DeviceSelector.vue   # 设备选择组件 - 切换CPU/GPU设备
│   │   ├── NavBar.vue           # 导航栏组件 - 应用顶部导航
│   │   └── HelloWorld.vue       # 示例组件
│   ├── router/          # 路由配置
│   │   ├── index.js             # 路由配置（JavaScript版本）
│   │   └── index.ts             # 路由配置（TypeScript版本）
│   ├── utils/           # 工具函数
│   │   └── logger.ts            # 日志工具
│   ├── App.vue          # 应用根组件
│   └── main.ts          # 应用入口文件
├── package.json         # 项目配置
└── vite.config.ts       # Vite配置
```

### 后端文件结构

```
backend/
├── app.py               # 主应用文件 - 核心后端逻辑
├── requirements.txt     # 依赖文件 - Python包依赖
├── .env                 # 环境变量 - 配置参数
├── .env.bak             # 环境变量备份
├── uploads/             # 上传文件目录 - 存储用户上传的图片/视频
├── results/             # 检测结果目录 - 存储检测后的结果文件
└── logs/                # 日志目录 - 存储应用运行日志
```

### 项目根目录

```
git_yolo_detect/
├── backend/                    # 后端代码
├── frontend/                   # 前端代码
├── README.md                   # 项目说明
├── 核心功能模块.md              # 核心功能模块分析
├── 项目技术分析报告.md           # 项目技术分析报告
├── 绝缘子缺陷检测系统需求文档.md    # 需求文档
├── API接口文档.md               # API接口文档
├── 数据库设计文档.md             # 数据库设计文档
├── 架构设计图描述.md             # 架构设计图描述
└── .gitignore                  # Git忽略文件
```

## 常见问题

### 1. 无法启动后端服务

- 检查Python版本是否符合要求
- 检查依赖是否正确安装
- 检查数据库连接是否配置正确
- 检查端口是否被占用

### 2. 检测速度慢

- 确保启用了GPU加速
- 检查模型文件是否正确
- 考虑使用更轻量级的模型版本
- 减少视频分辨率或帧率

### 3. 前端无法连接后端

- 检查后端服务是否正在运行
- 检查CORS配置是否正确
- 检查前端API基础URL是否配置正确
- 检查网络连接是否正常

### 4. 检测结果不准确

- 确保使用了正确的模型文件
- 调整置信度阈值
- 考虑重新训练模型，使用更多的训练数据
- 确保输入图片/视频的质量良好

## 联系方式

- **作者**：吴权彬
- **邮箱**：<1597338110@qq.com>
- **项目地址**：<https://github.com/Pursuerbin/git_yolo_detect>

## 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。